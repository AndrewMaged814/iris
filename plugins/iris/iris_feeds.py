"""Structured facts for one owner-approved product watch.

Hermes performs web research. This adapter reads one product page for stable
price/stock snapshots; it never crawls catalogs, navigation or sitemaps.
"""
from __future__ import annotations

import html
import ipaddress
import re
import socket
import time
from datetime import datetime, timezone
from urllib.parse import quote, urljoin, urlparse
from urllib.robotparser import RobotFileParser

USER_AGENT = "IrisBot/1.0 (market watch for a store owner; read-only)"
ROBOTS_AGENT = "IrisBot"
TIMEOUT_S = 15
MAX_BYTES = 2_000_000

# Access states returned to the agent.
OK, BLOCKED, NOT_FOUND, UNREACHABLE, NO_PRODUCTS = "ok", "blocked", "not_found", "unreachable", "no_products"
DISALLOWED = "disallowed_by_robots"  # the store's robots.txt asks bots not to read this page
UNAVAILABLE = "reader_unavailable"   # a page-reading dependency is missing on this host


class FetchError(Exception):
    def __init__(self, access: str, detail: str = ""):
        super().__init__(detail or access)
        self.access = access


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


def _clean(text, limit=160):
    text = html.unescape(re.sub(r"<[^>]+>", " ", str(text or "")))
    return re.sub(r"\s+", " ", text).strip()[:limit]


def _base(url: str) -> str:
    return url.split("?", 1)[0].split("#", 1)[0].rstrip("/")


def _origin(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def _product(**fields) -> dict:
    price, compare_at = fields.get("price"), fields.get("compare_at")
    fields["on_sale"] = bool(fields.get("on_sale")) or bool(price and compare_at and compare_at > price)
    fields.setdefault("currency", None)
    fields.setdefault("available", None)
    return fields


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


def read_store(url: str, get=None, kind: str = "auto") -> dict:
    """Read one product, never discover a catalog. Legacy kind is accepted but ignored."""
    url = url.strip()
    if not re.match(r"^https?://", url, re.I):
        url = "https://" + url
    result = {"url": url, "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
              "source": "page", "scope": "product", "access": OK, "products": []}
    if urlparse(url).path.strip("/").lower() in ("", "en", "ar"):
        result["access"] = "product_link_required"
        return result
    try:
        get = get or http_get
        status, text = get(url)
        access = _status_access(status, text)
        if access:
            raise FetchError(access)
        found = _page_products(text, url)
        exact = [p for p in found if _base(p["url"]) == _base(url)]
        # A recommendation carousel/category must not become one watched product.
        if len(exact) == 1:
            found = exact
        if len(found) == 1:
            result["products"] = found
        else:
            result["access"] = NO_PRODUCTS
    except FetchError as exc:
        result["access"] = exc.access
    return result
