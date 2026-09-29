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
from urllib.parse import urljoin, urlparse

USER_AGENT = "IrisBot/1.0 (market watch for a store owner; read-only)"
TIMEOUT_S = 15
MAX_BYTES = 2_000_000
MAX_PAGES = 20
PAGE_DELAY_S = 1.0

# Access states returned to the agent.
OK, BLOCKED, NOT_FOUND, UNREACHABLE, NO_PRODUCTS = "ok", "blocked", "not_found", "unreachable", "no_products"


class FetchError(Exception):
    def __init__(self, access: str, detail: str = ""):
        super().__init__(detail or access)
        self.access = access


# ---------------------------------------------------------------- fetching

def _hermes_client():
    """Hermes' SSRF-safe httpx client (checks every redirect, dials the checked IP)."""
    from tools.url_safety import create_ssrf_safe_client  # provided by the Hermes runtime
    return create_ssrf_safe_client(timeout=TIMEOUT_S, follow_redirects=True,
                                   headers={"User-Agent": USER_AGENT, "Accept": "application/json, text/html;q=0.9"})


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


def http_get(url: str) -> tuple[int, str]:
    """GET a public URL. Returns (status, text). Uses Hermes' safe client when available."""
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
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
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
            url=f"{base}/products/{p.get('handle')}" if p.get("handle") else base,
            product_type=_clean(p.get("product_type"), 60),
            tags=[_clean(t, 40) for t in tags][:10],
            vendor=_clean(p.get("vendor"), 60),
            price=price,
            compare_at=compare_at,
            available=any(bool(v.get("available")) for v in variants) if variants else None,
            created_at=p.get("created_at") or p.get("published_at"),
            variants=len(variants),
            image=(images[0].get("src") if images and isinstance(images[0], dict) else None),
        ))
    return out


def _read_shopify(base: str, get) -> list[dict] | None:
    products, seen_first = [], set()
    for page in range(1, MAX_PAGES + 1):
        status, text = get(f"{base}/products.json?limit=250&page={page}")
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
            return None if page == 1 else products
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
    return products


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
            image=(images[0].get("src") if images and isinstance(images[0], dict) else None),
        ))
    return out


def _read_woo(base: str, get) -> list[dict] | None:
    products, seen_first = [], set()
    for page in range(1, MAX_PAGES + 1):
        status, text = get(f"{base}/wp-json/wc/store/v1/products?per_page=100&page={page}")
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


# ---------------------------------------------------------------- page JSON-LD

class _LdParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.blocks, self.meta, self._in_ld, self._buf, self.title = [], {}, False, [], ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script" and (a.get("type") or "").lower() == "application/ld+json":
            self._in_ld, self._buf = True, []
        elif tag == "meta" and (a.get("property") or a.get("name")):
            self.meta[(a.get("property") or a.get("name")).lower()] = a.get("content") or ""
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "script" and self._in_ld:
            self.blocks.append("".join(self._buf))
            self._in_ld = False
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_ld:
            self._buf.append(data)
        elif self._in_title:
            self.title += data


def _walk_ld(node):
    if isinstance(node, list):
        for n in node:
            yield from _walk_ld(n)
    elif isinstance(node, dict):
        kind = node.get("@type")
        kinds = kind if isinstance(kind, list) else [kind]
        if "Product" in kinds:
            yield node
        for key in ("@graph", "itemListElement", "item", "mainEntity"):
            if key in node:
                yield from _walk_ld(node[key])


def _ld_products(page_html: str, page_url: str) -> list[dict]:
    parser = _LdParser()
    parser.feed(page_html)
    out = []
    for raw in parser.blocks:
        data = _json_or_none(raw.strip())
        for p in _walk_ld(data):
            offers = p.get("offers") or {}
            offers = offers[0] if isinstance(offers, list) and offers else offers
            price = _num(offers.get("price") or offers.get("lowPrice"))
            spec = offers.get("priceSpecification") or {}
            spec = spec[0] if isinstance(spec, list) and spec else spec
            compare_at = _num(spec.get("price")) if isinstance(spec, dict) and spec.get("priceType", "").endswith("ListPrice") else None
            availability = str(offers.get("availability") or "")
            image = p.get("image")
            image = image[0] if isinstance(image, list) and image else image
            image = image.get("url") if isinstance(image, dict) else image
            props = [f"{_clean(x.get('name'), 40)}: {_clean(x.get('value'), 60)}"
                     for x in (p.get("additionalProperty") or []) if isinstance(x, dict)]
            url = urljoin(page_url, p.get("url") or page_url)
            out.append(_product(
                key=f"page:{_base(url)}#{_clean(p.get('sku') or p.get('name'), 60)}",
                title=_clean(p.get("name")),
                url=url,
                product_type=_clean(p.get("category"), 60),
                tags=props[:10],
                vendor=_clean((p.get("brand") or {}).get("name") if isinstance(p.get("brand"), dict) else p.get("brand"), 60),
                price=price,
                compare_at=compare_at,
                currency=offers.get("priceCurrency"),
                available=(None if not availability else "InStock" in availability or "LimitedAvailability" in availability),
                created_at=None,
                variants=1,
                image=image if isinstance(image, str) else None,
            ))
    if not out and (parser.meta.get("og:title") or parser.title):
        price = _num(parser.meta.get("product:price:amount") or parser.meta.get("og:price:amount"))
        if price is not None:
            out.append(_product(key=f"page:{_base(page_url)}", title=_clean(parser.meta.get("og:title") or parser.title),
                                url=page_url, product_type="", tags=[], vendor=None, price=price, compare_at=None,
                                currency=parser.meta.get("product:price:currency") or parser.meta.get("og:price:currency"),
                                available=None, created_at=None, variants=1, image=parser.meta.get("og:image")))
    return out


def _read_page(url: str, get) -> list[dict]:
    status, text = get(url)
    access = _status_access(status, text)
    if access:
        raise FetchError(access)
    return _ld_products(text, url)


# ---------------------------------------------------------------- public entry

def read_store(url: str, get=None, kind: str = "auto") -> dict:
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
    except FetchError as exc:
        result["access"] = exc.access
        return result
    if not result["products"]:
        result["access"] = NO_PRODUCTS
    return result
