"""Compare two snapshots of one store and turn the differences into signals.

Price thresholds follow DannylydST/sorftime-seller-agent's monitor (MIT):
a move of 5% is worth noting, 10% is important.

Signals are data for Iris, never sentences for the owner. Urgent signals are the
two alert types: a listed markdown starts or a watched item goes out of stock.
Everything else waits for the weekly message.
"""
from __future__ import annotations

MINOR_PCT, MAJOR_PCT = 5.0, 10.0


def _matches(product: dict, focus: list[str]) -> bool:
    if not focus:
        return True
    hay = " ".join([product.get("title") or "", product.get("product_type") or "",
                    " ".join(product.get("tags") or [])]).lower()
    return any(word.lower() in hay for word in focus)


def _brief(p: dict) -> dict:
    return {k: p.get(k) for k in ("title", "url", "product_type", "price", "compare_at", "currency", "available")}


def _signal(kind, product, urgent, **extra):
    return {"kind": kind, "product_key": product["key"], "urgent": urgent, "product": _brief(product), **extra}


def diff(previous: list[dict] | None, current: list[dict], focus: list[str] | None = None) -> list[dict]:
    """Return the signals between two product lists. The first snapshot is a baseline: no signals.
    Product watches establish price/stock changes, never catalog additions or removals."""
    if previous is None:
        return []
    focus = focus or []
    before = {p["key"]: p for p in previous}
    now = {p["key"]: p for p in current}
    signals = []
    for key, cur in now.items():
        relevant = _matches(cur, focus)
        old = before.get(key)
        if old is None:
            continue
        if cur.get("on_sale") and not old.get("on_sale"):
            signals.append(_signal("sale_started", cur, urgent=relevant, was_price=old.get("price")))
        elif old.get("on_sale") and not cur.get("on_sale"):
            signals.append(_signal("sale_ended", cur, urgent=False, was_price=old.get("price")))
        elif old.get("price") and cur.get("price") and old["price"] != cur["price"]:
            pct = round((cur["price"] - old["price"]) / old["price"] * 100, 1)
            if abs(pct) >= MINOR_PCT:
                signals.append(_signal("price_change", cur, urgent=False, was_price=old["price"], change_pct=pct,
                                       size="major" if abs(pct) >= MAJOR_PCT else "minor"))
        if old.get("available") is True and cur.get("available") is False:
            signals.append(_signal("out_of_stock", cur, urgent=relevant))
        elif old.get("available") is False and cur.get("available") is True:
            signals.append(_signal("back_in_stock", cur, urgent=False))
    return signals


def summarize(products: list[dict]) -> dict:
    """Market picture by product type: count, price range, median, on sale, out of stock.
    This is the "compare by product type, not head to head" view (pricing-intel method, FlatNine, MIT)."""
    groups: dict[str, list[dict]] = {}
    for p in products:
        groups.setdefault((p.get("product_type") or "other").strip() or "other", []).append(p)
    out = {}
    for name, items in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        priced = [p for p in items if p.get("price") is not None]
        currencies = {p.get("currency") for p in priced}
        prices = sorted(p["price"] for p in items if p.get("price") is not None)
        if len(currencies) > 1:
            prices = []  # an aggregate across different/unknown currencies has no price meaning
        median = None
        if prices:
            mid = len(prices) // 2
            median = prices[mid] if len(prices) % 2 else round((prices[mid - 1] + prices[mid]) / 2, 2)
        out[name] = {
            "count": len(items),
            "currency": next(iter(currencies)) if len(currencies) == 1 else None,
            "price_min": prices[0] if prices else None,
            "price_median": median,
            "price_max": prices[-1] if prices else None,
            "on_sale": sum(1 for p in items if p.get("on_sale")),
            "out_of_stock": sum(1 for p in items if p.get("available") is False),
        }
    return out
