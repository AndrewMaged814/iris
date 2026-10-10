"""Compare two snapshots of one store and turn the differences into signals.

Price thresholds follow DannylydST/sorftime-seller-agent's monitor (MIT):
a move of 5% is worth noting, 10% is important.

Signals are data for Iris, never sentences for the owner. Urgent signals are the
two alert types: a listed markdown starts or a watched item goes out of stock.
Everything else waits for the weekly message.
"""
from __future__ import annotations

from math import isfinite

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


def _valid_price(value) -> bool:
    return type(value) in (int, float) and isfinite(value) and value >= 0


def _currency(product: dict) -> str | None:
    value = product.get("currency")
    return (value.strip().upper() or None) if isinstance(value, str) else None


def _sale_state(product: dict) -> bool | None:
    # Readers can return on_sale=False when no price was obtainable. That is
    # missing evidence, not proof that an observed sale ended.
    value = product.get("on_sale")
    return value if _valid_price(product.get("price")) and type(value) is bool else None


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
        comparable = (bool(_currency(old)) and _currency(old) == _currency(cur)
                      and _valid_price(old.get("price")) and _valid_price(cur.get("price")))
        old_sale, cur_sale = _sale_state(old), _sale_state(cur)
        if comparable and cur_sale is True and old_sale is False:
            signals.append(_signal("sale_started", cur, urgent=relevant, was_price=old.get("price")))
        elif comparable and old_sale is True and cur_sale is False:
            signals.append(_signal("sale_ended", cur, urgent=False, was_price=old.get("price")))
        elif comparable and old["price"] > 0 and old["price"] != cur["price"]:
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
