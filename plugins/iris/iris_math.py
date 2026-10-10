"""Stateless calculations from supplied facts, with no research or business advice."""
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_HALF_UP

UNITS = {"ml": ("volume", Decimal(1)), "l": ("volume", Decimal(1000)),
         "g": ("mass", Decimal(1)), "kg": ("mass", Decimal(1000)),
         "item": ("items", Decimal(1))}


def number(value, field, *, optional=False):
    if value is None and optional:
        return None
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ValueError(f"{field}: a finite nonnegative number is required")
    try:
        result = Decimal(str(value))
    except InvalidOperation:
        raise ValueError(f"{field}: invalid number") from None
    if not result.is_finite() or result < 0 or result > Decimal("1000000000000"):
        raise ValueError(f"{field}: outside supported numeric range")
    return result


def rounded(value, places=2, rounding=ROUND_HALF_UP):
    return float(value.quantize(Decimal(1).scaleb(-places), rounding=rounding)) if value is not None else None


def quantity(basket, field):
    value = number(basket.get("quantity"), field, optional=True)
    unit = basket.get("unit")
    if value is None or unit is None:
        return None, None
    if value == 0 or unit not in UNITS:
        raise ValueError(f"{field}: positive quantity and ml/l/g/kg/item unit required")
    family, scale = UNITS[unit]
    return value * scale, family


def currency(value):
    if not isinstance(value, str):
        return None
    value = value.strip().upper()
    return value if len(value) == 3 and value.isascii() and value.isalpha() else None


def relation(left, right):
    if left is None or right is None:
        return None
    return "greater_than" if left > right else "less_than" if left < right else "equal"


def compare_baskets(args):
    own, rival = args.get("own"), args.get("rival")
    if not isinstance(own, dict) or not isinstance(rival, dict):
        raise ValueError("own and rival baskets required")
    prices = rival.get("totals")
    if not isinstance(prices, list) or not 1 <= len(prices) <= 4:
        raise ValueError("rival.totals: one to four separately plausible payable totals required")
    own_price = number(own.get("price"), "own.price")
    totals = [number(p, "rival.totals") for p in prices]
    own_qty, own_family = quantity(own, "own.quantity")
    rival_qty, rival_family = quantity(rival, "rival.quantity")
    comparable_quantity = own_qty is not None and rival_qty is not None and own_family == rival_family
    own_currency, rival_currency = currency(own.get("currency")), currency(rival.get("currency"))
    comparable_money = own_currency is not None and own_currency == rival_currency
    warnings = []
    if not comparable_money:
        warnings.append("currency_unknown_or_mismatched")
    if not comparable_quantity:
        warnings.append("quantity_unknown_or_incompatible")
    return {
        "operation": "compare_baskets", "inputs": args,
        "currency": own_currency if comparable_money else None,
        "quantity_ratio_rival_to_own": rounded(rival_qty / own_qty, 6) if comparable_quantity else None,
        "quantity_difference_rival_minus_own": rounded(rival_qty - own_qty, 6) if comparable_quantity else None,
        "quantity_percent_more_than_own": rounded((rival_qty / own_qty - 1) * 100, 4) if comparable_quantity else None,
        "normalized_quantity_unit": {"volume": "ml", "mass": "g", "items": "item"}.get(own_family) if comparable_quantity else None,
        "own_price_per_normalized_unit": rounded(own_price / own_qty, 6) if comparable_money and comparable_quantity else None,
        "scenarios": [{"rival_total": rounded(p),
                       "upfront_difference_rival_minus_own": rounded(p - own_price) if comparable_money else None,
                       "own_upfront_price_relation_to_rival": relation(own_price, p) if comparable_money else None,
                       "own_unit_price_relation_to_rival": relation(own_price / own_qty, p / rival_qty)
                           if comparable_money and comparable_quantity else None,
                       "rival_price_per_normalized_unit": rounded(p / rival_qty, 6) if comparable_money and comparable_quantity else None}
                      for p in totals],
        "warnings": warnings, "checkout_verified": False, "product_equivalence_verified": False,
    }


def compare_products(args):
    own, products = args.get("own"), args.get("products")
    if not isinstance(own, dict):
        raise ValueError("compare_products: own reference basket is required separately; products contains rival rows only")
    if not isinstance(products, list) or not 1 <= len(products) <= 10:
        raise ValueError("products: one to ten individually identified product rows required")
    rows = []
    for product in products:
        if not isinstance(product, dict) or not isinstance(product.get("name"), str) or not product["name"].strip():
            raise ValueError("products: each row needs its own product name")
        basket = {k: product.get(k) for k in ("currency", "quantity", "unit")}
        basket["totals"] = [product.get("price")]
        comparison = compare_baskets({"own": own, "rival": basket})
        rows.append({"name": product["name"], "source_url": product.get("source_url"),
                     "product_inputs": product, "comparison": comparison})
    prices = [r["comparison"]["scenarios"][0]["rival_price_per_normalized_unit"] for r in rows]
    known_prices = [p for p in prices if p is not None]
    return {"operation": "compare_products", "own_inputs": own, "comparisons": rows,
            "normalized_quantity_unit": next((r["comparison"]["normalized_quantity_unit"]
                for r, price in zip(rows, prices) if price is not None), None),
            "computed_rival_price_per_unit_range": [min(known_prices), max(known_prices)] if known_prices else None,
            "normalized_price_comparison_count": len(known_prices),
            "product_equivalence_verified": False, "checkout_verified": False}


def unit_economics(args):
    current = number(args.get("current_price"), "current_price")
    proposed = number(args.get("proposed_price"), "proposed_price", optional=True)
    cost = number(args.get("unit_cost"), "unit_cost", optional=True)
    fixed = number(args.get("variable_cost_per_item"), "variable_cost_per_item", optional=True)
    fee = number(args.get("payment_fee_percent"), "payment_fee_percent", optional=True)
    floor = number(args.get("minimum_to_keep"), "minimum_to_keep", optional=True)
    baseline = number(args.get("baseline_units"), "baseline_units", optional=True)
    if fee is not None and fee >= 100:
        raise ValueError("payment_fee_percent: must be below 100")
    if baseline is not None and (baseline == 0 or baseline != baseline.to_integral_value()):
        raise ValueError("baseline_units: positive whole units required; orders are not units")
    cur_currency = currency(args.get("currency"))
    if cur_currency is None:
        raise ValueError("currency: confirmed three-letter currency required")
    complete = all(v is not None for v in (cost, fixed, fee))
    def at(price):
        if price is None:
            return None
        fee_amount = price * fee / 100 if fee is not None else None
        contribution = price - cost - fixed - fee_amount if complete else None
        return {"price": rounded(price), "payment_fee": rounded(fee_amount),
                "price_minus_unit_cost": rounded(price - cost) if cost is not None else None,
                "amount_after_supplied_costs": rounded(contribution),
                "gap_above_minimum": rounded(contribution - floor) if contribution is not None and floor is not None else None}
    old, new = at(current), at(proposed)
    # Use exact Decimal values for the ceiling; round only displayed money.
    old_amount = current * (1 - fee / 100) - cost - fixed if complete else None
    new_amount = proposed * (1 - fee / 100) - cost - fixed if complete and proposed is not None else None
    comparable_amounts = old_amount is not None and new_amount is not None
    positive_amounts = comparable_amounts and old_amount > 0 and new_amount > 0
    baseline_period, offer_period = args.get("baseline_period"), args.get("offer_period")
    same_period = bool(baseline_period and offer_period and baseline_period == offer_period)
    units = int((baseline * old_amount / new_amount).to_integral_value(rounding=ROUND_CEILING)) if baseline is not None and positive_amounts else None
    return {"operation": "unit_economics", "inputs": args, "currency": cur_currency,
            "current": old, "proposed": new,
            "amount_lost_per_item": rounded(old_amount - new_amount) if comparable_amounts else None,
            "units_multiplier_to_equal_current": rounded(old_amount / new_amount, 6) if positive_amounts else None,
            "additional_units_percent_to_equal_current": rounded((old_amount / new_amount - 1) * 100, 4) if positive_amounts else None,
            "minimum_price_for_supplied_floor": rounded((cost + fixed + floor) / (1 - fee / 100), rounding=ROUND_CEILING) if complete and floor is not None else None,
            "same_period_confirmed": same_period,
            "whole_period_units_to_equal_baseline": units,
            "additional_units_to_equal_baseline": units - int(baseline) if units is not None else None,
            "offer_period_target_units": units if same_period else None,
            "break_even_assumptions": {"all_baseline_units_at_proposed_price": True,
                                      "equivalent_periods_required": True},
            "missing_cost_fields": [key for key in ("unit_cost", "variable_cost_per_item", "payment_fee_percent") if args.get(key) is None],
            "business_outcome_verified": False}


def calculate(args):
    operation = args.get("operation")
    if operation == "compare_baskets":
        return compare_baskets(args)
    if operation == "compare_products":
        return compare_products(args)
    if operation == "unit_economics":
        return unit_economics(args)
    raise ValueError("operation: compare_products, compare_baskets or unit_economics required")
