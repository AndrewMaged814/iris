"""The owner's own Shopify store, read-only, with fixed queries.

One Iris per store: credentials come from the profile's .env.
Auth: a Dev Dashboard app on the owner's store using the client credentials grant
(same method as cgaravitoq/shopify-hermes-agent, MIT), or a static Admin API token.
The model never sees credentials and cannot write its own queries.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

try:
    from agent.secret_scope import get_secret as _profile_value
except ImportError:  # standalone scripts/tests, or Hermes before profile scopes
    _profile_value = os.environ.get

API_VERSION = "2026-07"
STORE_RE = re.compile(r"^[a-z0-9][a-z0-9-]*\.myshopify\.com$")

CATALOG_QUERY = """
query IrisCatalog($after: String) {
  shop { name currencyCode myshopifyDomain }
  products(first: 100, after: $after, query: "status:active") {
    pageInfo { hasNextPage endCursor }
    nodes {
      title handle productType tags vendor createdAt
      priceRangeV2 { minVariantPrice { amount currencyCode } maxVariantPrice { amount } }
      compareAtPriceRange { maxVariantCompareAtPrice { amount } }
    }
  }
}"""

SEARCH_QUERY = """
query IrisProducts($q: String!) {
  shop { currencyCode }
  products(first: 10, query: $q) {
    nodes {
      title handle productType tags vendor status createdAt description
      options { name values }
      variants(first: 20) { nodes { title sku price compareAtPrice availableForSale } }
      metafields(first: 10) { nodes { namespace key type value } }
    }
  }
}"""


class StoreError(Exception):
    """A plain-words problem Iris can explain to the owner."""


def _store() -> str:
    store = _profile_value("SHOPIFY_STORE", "").strip().lower()
    store = re.sub(r"^https?://", "", store).split("/")[0]
    if not STORE_RE.match(store):
        raise StoreError("The store is not set up yet (SHOPIFY_STORE must be the store's myshopify.com address).")
    return store


def _cache_path(store: str) -> Path:
    base = _profile_value("IRIS_DATA_DIR")
    if not base:
        try:
            from hermes_constants import get_hermes_home
            base = str(Path(get_hermes_home()) / "iris")
        except ImportError:
            base = str(Path.home() / ".hermes" / "iris")
    path = Path(base) / f".shopify-token-{store}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _token(store: str) -> str:
    static = _profile_value("SHOPIFY_ADMIN_TOKEN", "").strip()
    if static:
        return static
    client_id = _profile_value("SHOPIFY_CLIENT_ID", "").strip()
    secret = _profile_value("SHOPIFY_CLIENT_SECRET", "").strip()
    if not (client_id and secret):
        raise StoreError("The store connection is missing its app credentials.")
    cache = _cache_path(store)
    try:
        data = json.loads(cache.read_text())
        if data.get("store") == store and data.get("expires_at", 0) > time.time() and data.get("token"):
            return data["token"]
    except (OSError, ValueError):
        pass
    body = json.dumps({"client_id": client_id, "client_secret": secret, "grant_type": "client_credentials"}).encode()
    req = urllib.request.Request(f"https://{store}/admin/oauth/access_token", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            token = json.loads(resp.read()).get("access_token")
    except urllib.error.HTTPError as exc:
        raise StoreError(f"Shopify refused the store connection (HTTP {exc.code}).")
    except (OSError, ValueError):
        raise StoreError("Shopify could not be reached.")
    if not token:
        raise StoreError("Shopify did not return an access token.")
    cache.write_text(json.dumps({"store": store, "token": token, "expires_at": int(time.time()) + 23 * 3600}))
    os.chmod(cache, 0o600)
    return token


def _graphql(query: str, variables: dict, post=None) -> dict:
    store = _store()
    if post is not None:
        return post(query, variables)
    api_version = _profile_value("SHOPIFY_API_VERSION", API_VERSION)
    req = urllib.request.Request(
        f"https://{store}/admin/api/{api_version}/graphql.json",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Content-Type": "application/json", "X-Shopify-Access-Token": _token(store)})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        raise StoreError(f"Shopify returned an error (HTTP {exc.code}).")
    except (OSError, ValueError):
        raise StoreError("Shopify could not be reached.")
    if payload.get("errors"):
        raise StoreError("Shopify could not answer this request.")
    return payload.get("data") or {}


def _money(node, *path):
    for key in path:
        node = (node or {}).get(key)
    try:
        return round(float(node), 2) if node is not None else None
    except (TypeError, ValueError):
        return None


def catalog(post=None, max_pages: int = 5) -> dict:
    """The owner's active catalog grouped by product type."""
    after, shop, products = None, {}, []
    for _ in range(max_pages):
        data = _graphql(CATALOG_QUERY, {"after": after}, post)
        shop = data.get("shop") or shop
        page = data.get("products") or {}
        for n in page.get("nodes") or []:
            products.append({
                "title": n.get("title"), "handle": n.get("handle"),
                "product_type": n.get("productType") or "other", "tags": (n.get("tags") or [])[:10],
                "price_min": _money(n, "priceRangeV2", "minVariantPrice", "amount"),
                "price_max": _money(n, "priceRangeV2", "maxVariantPrice", "amount"),
                "compare_at_max": _money(n, "compareAtPriceRange", "maxVariantCompareAtPrice", "amount"),
                "created_at": n.get("createdAt"),
            })
        info = page.get("pageInfo") or {}
        if not info.get("hasNextPage"):
            break
        after = info.get("endCursor")
    types: dict[str, dict] = {}
    for p in products:
        t = types.setdefault(p["product_type"], {"count": 0, "price_min": None, "price_max": None, "products": []})
        t["count"] += 1
        if p["price_min"] is not None:
            t["price_min"] = p["price_min"] if t["price_min"] is None else min(t["price_min"], p["price_min"])
        if p["price_max"] is not None:
            t["price_max"] = p["price_max"] if t["price_max"] is None else max(t["price_max"], p["price_max"])
        if len(t["products"]) < 8:
            t["products"].append({k: p[k] for k in ("title", "tags", "price_min", "price_max", "compare_at_max")})
    newest = sorted(products, key=lambda p: p.get("created_at") or "", reverse=True)[:5]
    return {"shop": shop.get("name"), "currency": shop.get("currencyCode"), "product_count": len(products),
            "by_type": types, "newest": [{"title": p["title"], "created_at": p["created_at"]} for p in newest]}


def search(query: str, post=None) -> dict:
    """Details for products matching a Shopify search (title, type, tag or SKU)."""
    query = (query or "").strip()[:100]
    if not query:
        raise StoreError("Tell me which product to look for.")
    data = _graphql(SEARCH_QUERY, {"q": query}, post)
    out = []
    for n in (data.get("products") or {}).get("nodes") or []:
        out.append({
            "title": n.get("title"), "handle": n.get("handle"), "product_type": n.get("productType"),
            "tags": (n.get("tags") or [])[:10], "status": n.get("status"),
            "description": re.sub(r"\s+", " ", n.get("description") or "")[:600],
            "options": n.get("options") or [],
            "variants": [{"title": v.get("title"), "sku": v.get("sku"), "price": _money(v, "price"),
                          "compare_at": _money(v, "compareAtPrice"), "available": v.get("availableForSale")}
                         for v in (n.get("variants") or {}).get("nodes") or []],
            "details": [{"key": f"{m.get('namespace')}.{m.get('key')}", "value": str(m.get("value"))[:200]}
                        for m in (n.get("metafields") or {}).get("nodes") or []],
        })
    return {"currency": (data.get("shop") or {}).get("currencyCode"), "products": out}
