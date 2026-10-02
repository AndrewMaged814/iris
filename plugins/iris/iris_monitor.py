"""Daily product-page monitoring through the operator's changedetection.io (Apache-2.0).

changedetection.io's restock_diff processor already reads price, currency and stock from a
product page every day. Iris only creates, reads and deletes its watches over the documented
REST API (/api/v1/watch, header x-api-key) and turns the result into her own product record;
the change rules and every owner-facing sentence stay with Iris. Not configured = not used.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone

from iris_feeds import USER_AGENT

try:
    from agent.secret_scope import get_secret as _profile_value
except ImportError:  # standalone scripts/tests, or Hermes before profile scopes
    _profile_value = os.environ.get

TIMEOUT_S = 15


class MonitorError(Exception):
    pass


def _settings() -> tuple[str, str] | None:
    url, key = _profile_value("CHANGEDETECTION_URL"), _profile_value("CHANGEDETECTION_API_KEY")
    return (url.rstrip("/"), key) if url and key else None


def configured() -> bool:
    return _settings() is not None


def _call(method: str, path: str, body: dict | None = None, opener=None):
    settings = _settings()
    if not settings:
        raise MonitorError("changedetection.io is not configured")
    base, key = settings
    req = urllib.request.Request(base + path, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={"x-api-key": key, "Content-Type": "application/json"})
    try:
        with (opener or urllib.request.urlopen)(req, timeout=TIMEOUT_S) as resp:
            raw = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        raise MonitorError(f"changedetection.io answered {exc.code}")
    except OSError as exc:
        raise MonitorError(f"changedetection.io unreachable ({type(exc).__name__})")
    try:
        return json.loads(raw) if raw.strip() else None
    except ValueError:
        return raw


def watch(url: str, title: str, opener=None) -> str:
    """Watch one product page daily for price and stock, fetched with Iris's honest user agent."""
    created = _call("POST", "/api/v1/watch", {
        "url": url, "title": f"Iris: {title}"[:200], "processor": "restock_diff",
        "time_between_check_use_default": False, "time_between_check": {"days": 1},
        "headers": {"User-Agent": USER_AGENT}, "fetch_backend": "html_requests",
    }, opener=opener)
    uuid = created.get("uuid") if isinstance(created, dict) else None
    if not uuid:
        raise MonitorError("changedetection.io did not return a watch id")
    return uuid


def unwatch(uuid: str, opener=None) -> None:
    _call("DELETE", f"/api/v1/watch/{uuid}", opener=opener)


def product(uuid: str, url: str, title: str, key: str | None = None, opener=None) -> dict:
    """The watched page as an Iris product record, or MonitorError if it has no usable reading yet."""
    data = _call("GET", f"/api/v1/watch/{uuid}", opener=opener)
    if not isinstance(data, dict):
        raise MonitorError("unexpected changedetection.io answer")
    restock = data.get("restock") or {}
    if data.get("last_error") or (restock.get("price") is None and restock.get("in_stock") is None):
        raise MonitorError(str(data.get("last_error") or "no price or stock reading yet"))
    try:
        price = round(float(restock["price"]), 2) if restock.get("price") is not None else None
    except (TypeError, ValueError):
        price = None
    checked = data.get("last_checked")
    return {"key": key or f"page:{url.split('?', 1)[0].rstrip('/')}", "title": title, "url": url,
            "product_type": "", "tags": [], "vendor": None, "price": price, "compare_at": None,
            "on_sale": False, "currency": restock.get("currency"), "available": restock.get("in_stock"),
            "created_at": None, "variants": 1,
            "checked_at": (datetime.fromtimestamp(checked, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                           if isinstance(checked, (int, float)) and checked else None)}
