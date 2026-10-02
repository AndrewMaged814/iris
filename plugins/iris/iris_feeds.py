"""Read public product data from other stores.

Order of attempts for a store link:
  1. Shopify storefront feed   <base>/products.json      (paged, 250 per page)
  2. WooCommerce Store API     <base>/wp-json/wc/store/v1/products
  3. The page itself           JSON-LD Product / Offer data

Feed paging and the "compare_at > price means on sale" signal follow
zhaoheng588-tech/shopify-scout (MIT). Unlike that tool, Iris never disguises
itself or works around blocks: one honest user agent, and a block is reported.

This module has no package-relative imports, so the cron scripts can import it.
"""
from __future__ import annotations

import html
import ipaddress
import json
import re
import socket
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import quote, urljoin, urlparse
from urllib.robotparser import RobotFileParser

USER_AGENT = "IrisBot/1.0 (market watch for a store owner; read-only)"
ROBOTS_AGENT = "IrisBot"
TIMEOUT_S = 15
MAX_BYTES = 2_000_000
MAX_PAGES = 20
PAGE_DELAY_S = 1.0

# Access states returned to the agent.
OK, BLOCKED, NOT_FOUND, UNREACHABLE, NO_PRODUCTS = "ok", "blocked", "not_found", "unreachable", "no_products"
DISALLOWED = "disallowed_by_robots"  # the store's robots.txt asks bots not to read this page
UNAVAILABLE = "reader_unavailable"   # a page-reading dependency is missing on this host


class FetchError(Exception):
    def __init__(self, access: str, detail: str = ""):
        super().__init__(detail or access)
        self.access = access


# ---------------------------------------------------------------- fetching

def _hermes_client():
    """Hermes' SSRF-safe httpx client (checks every redirect, dials the checked IP)."""
    from tools.url_safety import create_ssrf_safe_client  # provided by the Hermes runtime
    return create_ssrf_safe_client(timeout=TIMEOUT_S, follow_redirects=True,
                                   headers={"User-Agent": USER_AGENT, "Accept": "text/html, application/json;q=0.9"})


def _basic_guard(url: str) -> None:
    """Fallback check when the Hermes client is not importable (for example a bare test run).
    Blocks non-http schemes and private, loopback, link-local and metadata addresses."""
    parts = urlparse(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise FetchError(UNREACHABLE, "only http and https links are allowed")
    try:
        infos = socket.getaddrinfo(parts.hostname, parts.port or (443 if parts.scheme == "https" else 80))
    except OSError:
        raise FetchError(UNREACHABLE, "the address did not resolve")
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise FetchError(UNREACHABLE, "private network addresses are not allowed")


def _uri(url: str) -> str:
    """Percent-encode non-ASCII links (Arabic product slugs) so every HTTP client accepts them."""
    if url.isascii():
        return url
    parts = urlparse(url)
    netloc = parts.netloc
    if parts.hostname and not parts.hostname.isascii():
        netloc = netloc.replace(parts.hostname, parts.hostname.encode("idna").decode())
    return quote(parts._replace(netloc=netloc).geturl(), safe=":/?#[]@!$&'()*+,;=%~")


_ROBOTS: dict[str, tuple[float, RobotFileParser | None]] = {}
ROBOTS_TTL_S = 3600


def robots_allows(url: str, get=None) -> bool:
    """True unless the site's robots.txt disallows Iris's user agent for this URL (cached per site)."""
    origin = _origin(url)
    cached = _ROBOTS.get(origin)
    if cached is None or time.time() - cached[0] > ROBOTS_TTL_S:
        rules = None
        try:
            status, text = (get or _fetch)(origin + "/robots.txt")
            if status == 200:
                rules = RobotFileParser()
                rules.parse(text.splitlines())
        except FetchError:
            rules = None  # no readable robots.txt: nothing is disallowed
        cached = _ROBOTS[origin] = (time.time(), rules)
    return cached[1] is None or cached[1].can_fetch(ROBOTS_AGENT, url)


def http_get(url: str) -> tuple[int, str]:
    """GET a public URL after checking the site's robots.txt. Returns (status, text)."""
    url = _uri(url)
    if not url.endswith("/robots.txt") and not robots_allows(url):
        raise FetchError(DISALLOWED)
    return _fetch(url)


def _fetch(url: str) -> tuple[int, str]:
    """GET a public URL. Uses Hermes' safe client when available."""
    url = _uri(url)
    try:
        client = _hermes_client()
    except ImportError:
        client = None
    if client is not None:
        try:
            with client:
                resp = client.get(url)
                body = resp.content[:MAX_BYTES]
                return resp.status_code, body.decode(resp.encoding or "utf-8", "replace")
        except Exception as exc:  # the safe client raises on blocked targets and network errors
            raise FetchError(UNREACHABLE, type(exc).__name__)
    import urllib.error
    import urllib.request
    _basic_guard(url)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html, application/json;q=0.9"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            _basic_guard(resp.geturl())
            return resp.status, resp.read(MAX_BYTES).decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(MAX_BYTES).decode("utf-8", "replace") if exc.fp else ""
    except OSError as exc:
        raise FetchError(UNREACHABLE, type(exc).__name__)


def _status_access(status: int, text: str) -> str | None:
    if status in (401, 403, 429) or (status == 503 and "cloudflare" in text.lower()):
        return BLOCKED
    if status in (404, 410):
        return NOT_FOUND
    if status >= 400:
        return UNREACHABLE
    return None


def _allowed_get(get, url: str) -> tuple[int, str]:
    """Optional sources (feeds, metadata) that robots.txt disallows count as absent, not as failures."""
    try:
        return get(url)
    except FetchError as exc:
        if exc.access == DISALLOWED:
            return 404, ""
        raise


def _json_or_none(text: str):
    """Parse JSON whatever the content type says (static hosts often send the wrong one)."""
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------- helpers

def _num(value):
    try:
        if value is None or value == "":
            return None
        return round(float(str(value).replace(",", "")), 2)
    except (TypeError, ValueError):
        return None


def _clean(text, limit=160):
    text = html.unescape(re.sub(r"<[^>]+>", " ", str(text or "")))
    return re.sub(r"\s+", " ", text).strip()[:limit]


def _base(url: str) -> str:
    return url.split("?", 1)[0].split("#", 1)[0].rstrip("/")


def _origin(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def _options(pairs) -> list[dict]:
    """Variant option names and values (Size, Color, Storage...): what distinguishes comparable products."""
    out = []
    for name, values in pairs:
        name = _clean(name, 40)
        values = [_clean(v, 40) for v in values or [] if _clean(v, 40)]
        if name and name.lower() != "title" and values and values != ["Default Title"]:
            out.append({"name": name, "values": values[:12]})
    return out[:4]


def _product(**fields) -> dict:
    price, compare_at = fields.get("price"), fields.get("compare_at")
    fields["on_sale"] = bool(fields.get("on_sale")) or bool(price and compare_at and compare_at > price)
    fields.setdefault("currency", None)
    fields.setdefault("available", None)
    return fields


# ---------------------------------------------------------------- Shopify feed

def _shopify_products(items, base: str) -> list[dict]:
    out = []
    for p in items:
        variants = p.get("variants") or []
        prices = [v for v in (_num(v.get("price")) for v in variants) if v is not None]
        compares = [c for c in (_num(v.get("compare_at_price")) for v in variants) if c is not None]
        price = min(prices) if prices else None
        cheapest = next((v for v in variants if _num(v.get("price")) == price), {})
        compare_at = _num(cheapest.get("compare_at_price")) if cheapest else (max(compares) if compares else None)
        tags = p.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        images = p.get("images") or []
        out.append(_product(
            key=f"shopify:{p.get('handle') or p.get('id')}",
            title=_clean(p.get("title")),
            description=_clean(p.get("body_html"), 1200),
            url=f"{base}/products/{p.get('handle')}" if p.get("handle") else base,
            product_type=_clean(p.get("product_type"), 60),
            tags=[_clean(t, 40) for t in tags][:10],
            vendor=_clean(p.get("vendor"), 60),
            price=price,
            compare_at=compare_at,
            available=any(bool(v.get("available")) for v in variants) if variants else None,
            created_at=p.get("created_at") or p.get("published_at"),
            variants=len(variants),
            options=_options((o.get("name"), o.get("values")) for o in p.get("options") or [] if isinstance(o, dict)),
            image=(images[0].get("src") if images and isinstance(images[0], dict) else None),
        ))
    return out


def _read_shopify(base: str, get) -> list[dict] | None:
    products, seen_first = [], set()
    for page in range(1, MAX_PAGES + 1):
        status, text = _allowed_get(get, f"{base}/products.json?limit=250&page={page}")
        access = _status_access(status, text)
        if access:
            if page == 1:
                if access == BLOCKED:
                    raise FetchError(BLOCKED)
                return None
            break
        data = _json_or_none(text)
        items = data.get("products") if isinstance(data, dict) else None
        if not isinstance(items, list):
            if page == 1:
                return None
            break
        if not items:
            break
        first = str(items[0].get("id") or items[0].get("handle"))
        if first in seen_first:  # static hosts ignore ?page=N and repeat page 1
            break
        seen_first.add(first)
        products.extend(_shopify_products(items, base))
        if len(items) < 250:
            break
        time.sleep(PAGE_DELAY_S)
    _confirm_shopify_currency(products, base, get)
    return products


def _confirm_shopify_currency(products: list[dict], base: str, get) -> None:
    """Confirm feed currency with store metadata and one matching first-party price.

    Public feeds omit currency. A presentment currency alone could mislabel base
    prices, so require the metadata currency AND the representative page's price
    to agree. Optional evidence failures leave the readable feed intact.
    """
    sample = next((p for p in products if p.get("price") and p.get("url")), None)
    if sample is None:
        return
    metadata_url = f"{_origin(base)}/meta.json"
    try:
        status, raw = _allowed_get(get, metadata_url)
        if _status_access(status, raw):
            return
        metadata = _json_or_none(raw)
        currency = metadata.get("currency") if isinstance(metadata, dict) else None
        if not isinstance(currency, str) or not re.fullmatch(r"[A-Z]{3}", currency):
            return
        status, page = get(sample["url"])
        if _status_access(status, page):
            return
        handle = urlparse(sample["url"]).path.rstrip("/").rsplit("/", 1)[-1]
        evidence = [p for p in _page_products(page, sample["url"])
                    if _origin(p["url"]) == _origin(sample["url"])
                    and urlparse(p["url"]).path.rstrip("/").rsplit("/", 1)[-1] == handle]
        if not evidence or any(p["currency"] != currency or p["price"] != sample["price"]
                               for p in evidence):
            return
    except FetchError:
        return
    for product in products:
        product["currency"] = currency
        product["currency_evidence"] = {"metadata_url": metadata_url,
                                        "verified_product_url": sample["url"]}


# ---------------------------------------------------------------- WooCommerce Store API

def _woo_price(prices: dict, key: str):
    raw = prices.get(key)
    if raw in (None, ""):
        return None
    try:
        return round(int(raw) / (10 ** int(prices.get("currency_minor_unit", 2))), 2)
    except (TypeError, ValueError):
        return _num(raw)


def _woo_products(items) -> list[dict]:
    out = []
    for p in items:
        prices = p.get("prices") or {}
        price = _woo_price(prices, "price")
        regular = _woo_price(prices, "regular_price")
        images = p.get("images") or []
        out.append(_product(
            key=f"woo:{p.get('id')}",
            title=_clean(p.get("name")),
            url=p.get("permalink"),
            product_type=_clean(((p.get("categories") or [{}])[0] or {}).get("name"), 60),
            tags=[_clean(t.get("name"), 40) for t in (p.get("tags") or []) if isinstance(t, dict)][:10],
            vendor=None,
            price=price,
            compare_at=regular if regular and price and regular > price else None,
            on_sale=bool(p.get("on_sale")),
            currency=prices.get("currency_code"),
            available=p.get("is_in_stock"),
            created_at=p.get("date_created"),
            variants=len(p.get("variations") or []) or 1,
            options=_options((a.get("name"), [t.get("name") for t in a.get("terms") or [] if isinstance(t, dict)])
                             for a in p.get("attributes") or [] if isinstance(a, dict)),
            image=(images[0].get("src") if images and isinstance(images[0], dict) else None),
        ))
    return out


def _read_woo(base: str, get) -> list[dict] | None:
    products, seen_first = [], set()
    for page in range(1, MAX_PAGES + 1):
        status, text = _allowed_get(get, f"{base}/wp-json/wc/store/v1/products?per_page=100&page={page}")
        access = _status_access(status, text)
        if access:
            if page == 1:
                if access == BLOCKED:
                    raise FetchError(BLOCKED)
                return None
            break
        items = _json_or_none(text)
        if not isinstance(items, list):
            return None if page == 1 else products
        if not items:
            break
        first = str(items[0].get("id"))
        if first in seen_first:
            break
        seen_first.add(first)
        products.extend(_woo_products(items))
        if len(items) < 100:
            break
        time.sleep(PAGE_DELAY_S)
    return products


# ---------------------------------------------------------------- page product data
# Structured data is read with extruct (JSON-LD, microdata, OpenGraph) and price strings with
# price-parser, both from Zyte (BSD). Iris only maps schema.org Product/Offer fields.

def _extract(page_html: str, page_url: str) -> dict:
    try:
        import extruct
    except ImportError:
        raise FetchError(UNAVAILABLE, "page reader not installed (extruct, price-parser)")
    return extruct.extract(page_html, base_url=page_url, syntaxes=["json-ld", "microdata", "opengraph"],
                           uniform=True, errors="ignore")


def _price(value):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return round(float(value), 2)
    if value in (None, ""):
        return None
    from price_parser import Price
    amount = Price.fromstring(str(value)).amount_float
    return round(amount, 2) if amount is not None else None


def _walk(node):
    if isinstance(node, list):
        for n in node:
            yield from _walk(n)
    elif isinstance(node, dict):
        kind = node.get("@type")
        kinds = [str(k).rsplit("/", 1)[-1] for k in (kind if isinstance(kind, list) else [kind])]
        if "Product" in kinds:
            yield node
        for key in ("@graph", "itemListElement", "item", "mainEntity"):
            if key in node:
                yield from _walk(node[key])


def _first(value):
    return value[0] if isinstance(value, list) and value else value


def _page_products(page_html: str, page_url: str) -> list[dict]:
    data = _extract(page_html, page_url)
    og = {}
    for block in data.get("opengraph") or []:
        og.update({k.lower(): _first(v) for k, v in block.items() if isinstance(k, str)})
    og_currency = og.get("product:price:currency") or og.get("og:price:currency")
    out = []
    for p in _walk((data.get("json-ld") or []) + (data.get("microdata") or [])):
        offers = _first(p.get("offers") or {})
        if not isinstance(offers, dict):
            continue
        price = _price(offers.get("price") if offers.get("price") not in (None, "") else offers.get("lowPrice"))
        spec = _first(offers.get("priceSpecification") or {})
        compare_at = (_price(spec.get("price")) if isinstance(spec, dict)
                      and str(spec.get("priceType", "")).endswith("ListPrice") else None)
        availability = str(_first(offers.get("availability")) or "")
        image = _first(p.get("image"))
        image = image.get("url") if isinstance(image, dict) else image
        props = [f"{_clean(x.get('name'), 40)}: {_clean(x.get('value'), 60)}"
                 for x in (p.get("additionalProperty") or []) if isinstance(x, dict)]
        brand = p.get("brand")
        url = urljoin(page_url, _first(p.get("url")) or page_url)
        currency = _first(offers.get("priceCurrency"))
        product = _product(
            key=f"page:{_base(url)}#{_clean(p.get('sku') or p.get('name'), 60)}",
            title=_clean(_first(p.get("name"))),
            description=_clean(_first(p.get("description")), 1200),
            url=url,
            product_type=_clean(_first(p.get("category")), 60),
            tags=props[:10],
            vendor=_clean(brand.get("name") if isinstance(brand, dict) else brand, 60),
            price=price,
            compare_at=compare_at,
            currency=currency,
            available=(None if not availability else "InStock" in availability or "LimitedAvailability" in availability),
            created_at=None,
            variants=1,
            image=image if isinstance(image, str) else None,
        )
        if currency and og_currency and og_currency != currency:  # the page contradicts itself
            product["currency"], product["currency_conflict"] = None, sorted({currency, og_currency})
        out.append(product)
    if not out:
        price = _price(og.get("product:price:amount") or og.get("og:price:amount"))
        title = og.get("og:title") or (re.search(r"<title[^>]*>(.*?)</title>", page_html, re.I | re.S) or [None, ""])[1]
        if price is not None and title:
            out.append(_product(key=f"page:{_base(page_url)}", title=_clean(title), url=page_url, product_type="",
                                tags=[], vendor=None, price=price, compare_at=None, currency=og_currency,
                                available=None, created_at=None, variants=1, image=og.get("og:image")))
    return out


_VOID = {"br", "img", "input", "hr", "meta", "link", "source", "wbr"}
_DATE_LIKE = re.compile(r"\d{4}.*[:\-]|[:\-].*\d{4}")


class _PageText(HTMLParser):
    """Bounded page evidence for Iris to interpret, never a parsed promotion claim.

    Countdown widgets ship placeholder digits ("00 days 00:00") that JavaScript fills in later.
    Iris doesn't run scripts, so report the widget's configured target instead of fake zeros.
    """
    def __init__(self):
        super().__init__()
        self.parts, self.main_parts, self.hidden, self.in_main = [], [], 0, False
        self.countdown = 0

    def _add(self, text):
        self.parts.append(text)
        if self.in_main:
            self.main_parts.append(text)

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "template"):
            self.hidden += 1
        if tag == "main":
            self.in_main = True
        if self.countdown:
            self.countdown += tag not in _VOID
            return
        a = dict(attrs)
        names = " ".join([tag, a.get("class") or "", a.get("id") or ""]).lower()
        if tag not in _VOID and ("countdown" in names or "timer" in names):
            self.countdown = 1
            targets = [_clean(v, 160) for k, v in attrs if v and k not in ("class", "id", "style")
                       and _DATE_LIKE.search(v)]
            self._add(f"[countdown target: {'; '.join(targets)}]" if targets
                      else "[countdown: end time not in page]")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "template"):
            self.hidden = max(0, self.hidden - 1)
        if tag == "main":
            self.in_main = False
        if self.countdown and tag not in _VOID:
            self.countdown -= 1

    def handle_data(self, data):
        if not self.hidden and not self.countdown and data.strip():
            self.parts.append(data.strip())
            if self.in_main:
                self.main_parts.append(data.strip())


# Product links across platforms: Shopify /products/x, WooCommerce /product/x/, Wuilt /product/all/x,
# Magento x.html, and common /p/, /item/, /shop/, /dp/ patterns.
_PRODUCT_LINK = re.compile(r"/(products?|p|item|shop|dp)/[^/]+/?$|/product/[^/]+/[^/]+/?$|"
                           r"/(?!index\.html$)[^/]+\.html$", re.I)


def _handle(url: str) -> str:
    return urlparse(url).path.rstrip("/").rsplit("/", 1)[-1].lower()


def _read_product_page(url: str, get) -> tuple[str, list[dict], str, str]:
    """Read one product link: (source, products, page_text, scope). A link that turns out to be a
    category page (several products, none of them this one) comes back as a "listing"."""
    status, text = get(url)
    access = _status_access(status, text)
    if access:
        raise FetchError(access)
    data = _json_or_none(text)
    handle = _handle(url)
    if isinstance(data, dict) and isinstance(data.get("product"), dict):
        product = data["product"]
        found = _shopify_products([product], _origin(url)) if product.get("handle") == handle else []
        return "shopify", found, "", "product"
    parser = _PageText()
    parser.feed(text)
    page_text = _clean(" ".join(parser.main_parts or parser.parts), 10000)
    found = _page_products(text, url)
    exact = [p for p in found if _handle(p["url"]) == handle]
    if exact or len(found) == 1:
        return "page", (exact or found)[:1], page_text, "product"
    if found:
        return "page", found, page_text, "listing"
    if "/products/" not in urlparse(url).path:
        return "page", [], page_text, "product"
    # A normal documented Shopify product endpoint, only if the page was readable.
    # A missing or blocked product never falls back to an unrelated store catalog.
    status, raw = get(_base(url) + ".json")
    access = _status_access(status, raw)
    if access == BLOCKED:
        raise FetchError(access)
    if access:
        return "page", [], page_text, "product"
    data = _json_or_none(raw)
    product = data.get("product") if isinstance(data, dict) else None
    found = (_shopify_products([product], _origin(url))
             if isinstance(product, dict) and product.get("handle") == handle else [])
    return "shopify" if found else "page", found, page_text, "product"


# ---------------------------------------------------------------- sitemap sample
# When a store publishes no catalog feed, its sitemap (the list it gives search engines) names its
# product pages. Iris reads an even, repeatable sample of them and says it is a sample.

SITEMAP_SAMPLE = 6
MAX_SITEMAPS = 6


def _site(url: str) -> str:
    return (urlparse(url).hostname or "").lower().removeprefix("www.")


def _sitemap_product_urls(origin: str, get) -> list[str]:
    status, robots = _allowed_get(get, origin + "/robots.txt")
    maps = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", robots) if status == 200 else []
    queue = [m for m in maps if _site(m) == _site(origin)][:3] or [origin + "/sitemap.xml"]
    seen, urls = set(), []
    while queue and len(seen) < MAX_SITEMAPS:
        sitemap = queue.pop(0)
        if sitemap in seen or sitemap.endswith(".gz"):
            continue
        seen.add(sitemap)
        try:
            status, xml = _allowed_get(get, sitemap)
        except FetchError:
            continue
        if status != 200:
            continue
        locs = [html.unescape(u) for u in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml)]
        if "<sitemapindex" in xml:
            children = [u for u in locs if "product" in u.lower()] or locs
            queue.extend(children[:3])
        else:
            urls += [u for u in locs if _site(u) == _site(origin) and _PRODUCT_LINK.search(urlparse(u).path)]
    return list(dict.fromkeys(urls))


def _read_sitemap_sample(origin: str, get) -> dict | None:
    urls = sorted(_sitemap_product_urls(origin, get))
    if not urls:
        return None
    picks = urls[:: max(1, len(urls) // SITEMAP_SAMPLE)][:SITEMAP_SAMPLE]
    products = []
    for i, link in enumerate(picks):
        if i:
            time.sleep(PAGE_DELAY_S)
        try:
            _, found, _, scope = _read_product_page(link, get)
        except FetchError:
            continue
        if scope == "product":
            products += found[:1]
    return {"products": products, "listed_products": len(urls), "pages_read": len(picks)}


def _read_page(url: str, get) -> list[dict]:
    status, text = get(url)
    access = _status_access(status, text)
    if access:
        raise FetchError(access)
    return _page_products(text, url)


# ---------------------------------------------------------------- public entry

class _PageLinks(HTMLParser):
    """Preserve first-party destinations omitted by main-text extraction."""

    def __init__(self, url):
        super().__init__()
        self.url, self.tags, self.anchor, self.links = url, [], None, []

    def handle_starttag(self, tag, attrs):
        if tag not in _VOID:
            self.tags.append(tag)
        if tag == 'a' and not any(t in self.tags for t in ('script', 'style', 'template', 'noscript')):
            a = dict(attrs)
            target = urlparse(urljoin(self.url, a.get('href') or ''))
            if a.get('href') and target.scheme in ('http', 'https') and target.netloc == urlparse(self.url).netloc:
                priority = any(t in self.tags for t in ('header', 'nav', 'footer'))
                self.anchor = (target._replace(fragment='').geturl(), priority, [], a.get('aria-label') or a.get('title') or '')

    def handle_data(self, data):
        if self.anchor and not any(t in self.tags for t in ('script', 'style', 'template', 'noscript')):
            self.anchor[2].append(data)

    def handle_endtag(self, tag):
        if tag == 'a' and self.anchor:
            url, priority, parts, fallback = self.anchor
            title = _clean(' '.join(parts) or fallback, 160)
            if title:
                self.links.append((priority, {'url': url, 'title': title}))
            self.anchor = None
        if tag in self.tags:
            self.tags = self.tags[:len(self.tags) - 1 - self.tags[::-1].index(tag)]


def read_page_links(url: str, get=None) -> dict:
    result = {'url': url, 'access': OK, 'links': []}
    try:
        status, text = (get or http_get)(url)
        result['access'] = _status_access(status, text) or OK
        if result['access'] != OK:
            return result
        parser = _PageLinks(url)
        parser.feed(text)
        seen = set()
        for _, link in sorted(parser.links, key=lambda p: not p[0]):
            if link['url'] not in seen:
                seen.add(link['url'])
                result['links'].append(link)
        result['links_truncated'] = len(result['links']) > 80
        result['links'] = result['links'][:80]
    except FetchError as exc:
        result['access'] = exc.access
    return result


def read_store(url: str, get=None, kind: str = "auto", include_links: bool = False) -> dict:
    """Read one store or page. Never raises: failures come back as an access state."""
    get = get or http_get
    url = url.strip()
    if not re.match(r"^https?://", url, re.I):
        url = "https://" + url
    base = _base(url)
    if base.endswith("/products.json"):
        base, kind = base[: -len("/products.json")], "shopify"
    result = {"url": url, "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
              "source": None, "access": OK, "products": []}
    attempts = {"auto": ("shopify", "woocommerce", "page"), "shopify": ("shopify",),
                "woocommerce": ("woocommerce",), "page": ("page",)}.get(kind, ("shopify", "woocommerce", "page"))
    try:
        if _PRODUCT_LINK.search(urlparse(base).path):
            link = url.split("#", 1)[0]  # as given: WooCommerce product links end in "/"
            result["source"], result["products"], result["page_text"], result["scope"] = _read_product_page(link, get)
            if not result["products"]:
                result["access"] = NO_PRODUCTS
            return result
        for attempt in attempts:
            if attempt == "shopify":
                found = _read_shopify(base, get)
                if found is None and _origin(url) != base:
                    found = _read_shopify(_origin(url), get)
            elif attempt == "woocommerce":
                found = _read_woo(base, get)
                if found is None and _origin(url) != base:
                    found = _read_woo(_origin(url), get)
            else:
                found = _read_page(url, get)
            if found is not None:
                result["source"], result["products"] = attempt, found
                break
        if not result["products"] and kind == "auto" and urlparse(url).path.strip("/").lower() in ("", "en", "ar"):
            sample = _read_sitemap_sample(_origin(url), get)
            if sample and sample["products"]:
                result.update(source="sitemap", scope="sample", products=sample.pop("products"), sample=sample)
    except FetchError as exc:
        result["access"] = exc.access
        return result
    if not result["products"]:
        result["access"] = NO_PRODUCTS
    if include_links:
        result['page_links'] = read_page_links(url, get=get)
    return result
