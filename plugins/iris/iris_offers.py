"""Bounded response offers: proposals, fresh native owner consent, fixed writes and readback.

This module owns the offer lifecycle so catalog reads stay simple. Ledger rows live in Iris's
existing profile database. No model-supplied approval flag, query or mutation is accepted.
"""
from __future__ import annotations

import hashlib
import json
import re
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

import iris_store as store
from iris_watchlist import Watchlist, profile_timezone

READ_SCOPES = {"read_products", "read_discounts"}
OFFER_CURRENCIES = {"EGP", "USD", "EUR", "GBP", "CAD", "AUD"}  # first slice: two-decimal prices
SCOPES_QUERY = "query IrisOfferScopes { currentAppInstallation { accessScopes { handle } } }"
CONTEXT_QUERY = """
query IrisOfferContext($id: ID!) {
  shop { currencyCode taxesIncluded }
  productVariant(id: $id) {
    id title price compareAtPrice availableForSale inventoryQuantity inventoryPolicy
    product { id title status }
    inventoryItem { tracked unitCost { amount currencyCode } }
  }
  discountNodes(first: 50, query: "status:active,scheduled") {
    pageInfo { hasNextPage }
    nodes { id discount { __typename } }
  }
}"""
DISCOUNT_FIELDS = """
id codeDiscount { __typename
  ... on DiscountCodeBasic {
    title status startsAt endsAt usageLimit appliesOncePerCustomer asyncUsageCount
    codes(first: 2) { pageInfo { hasNextPage } nodes { code } }
    combinesWith { orderDiscounts productDiscounts shippingDiscounts }
    context { __typename ... on DiscountBuyerSelectionAll { all } }
    minimumRequirement { __typename ... on DiscountMinimumQuantity { greaterThanOrEqualToQuantity } }
    customerGets {
      appliesOnOneTimePurchase appliesOnSubscription
      value { __typename ... on DiscountPercentage { percentage } }
      items { __typename ... on DiscountProducts {
        products(first: 2) { pageInfo { hasNextPage } nodes { id } }
        productVariants(first: 2) { pageInfo { hasNextPage } nodes { id } }
      } }
    }
  }
}"""
READ_QUERY = "query IrisOfferRead($code: String!) { codeDiscountNodeByCode(code: $code) { " + DISCOUNT_FIELDS + " } }"
CREATE_MUTATION = """
mutation IrisOfferCreate($input: DiscountCodeBasicInput!) {
  discountCodeBasicCreate(basicCodeDiscount: $input) {
    codeDiscountNode { id } userErrors { field code message }
  }
}"""
DEACTIVATE_MUTATION = """
mutation IrisOfferStop($id: ID!) {
  discountCodeDeactivate(id: $id) { codeDiscountNode { id } userErrors { field code message } }
}"""
LEDGER_SCHEMA = """
CREATE TABLE IF NOT EXISTS offers (
  id TEXT PRIMARY KEY, store TEXT NOT NULL, code TEXT NOT NULL,
  created_at TEXT NOT NULL, proposal TEXT NOT NULL, status TEXT NOT NULL,
  discount_id TEXT, approved_at TEXT, UNIQUE(store, code));
"""


def _now():
    return datetime.now(timezone.utc)


def _stamp(value):
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _date(value):
    try:
        date = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if date.tzinfo is None:
            raise ValueError()
        return date.astimezone(timezone.utc)
    except (TypeError, ValueError):
        raise store.StoreError("Offer dates need a time and time zone.")


def _decimal(value, label, low=0, high=Decimal("1e12")):
    try:
        result = Decimal(str(value))
        if not result.is_finite() or result < low or (high is not None and result > high):
            raise InvalidOperation()
        return result
    except (InvalidOperation, TypeError, ValueError):
        raise store.StoreError(f"A valid {label} is needed.")


def _cash(value):
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _scopes(post=None):
    data = store._graphql(SCOPES_QUERY, {}, post)
    granted = {n["handle"] for n in (data.get("currentAppInstallation") or {}).get("accessScopes") or []}
    # Shopify write scopes include their matching reads; the granted list may omit that read.
    return granted | {"read_" + scope[6:] for scope in granted if scope.startswith("write_")}


def context(variant_id, post=None):
    if not re.fullmatch(r"gid://shopify/ProductVariant/\d+", str(variant_id)):
        raise store.StoreError("Select a product variant from your catalog first.")
    scopes = _scopes(post)
    missing = sorted(READ_SCOPES - scopes)
    if missing:
        return {"ready": False, "missing_scopes": missing, "write_access": "write_discounts" in scopes}
    data = store._graphql(CONTEXT_QUERY, {"id": variant_id}, post)
    variant = data.get("productVariant")
    shop = data.get("shop") or {}
    discounts = data.get("discountNodes") or {}
    if not variant or variant.get("id") != variant_id or not shop.get("currencyCode"):
        raise store.StoreError("That variant could not be checked in your connected store.")
    blocks = []
    if shop["currencyCode"] not in OFFER_CURRENCIES:
        blocks.append("This offer workflow currently supports EGP, USD, EUR, GBP, CAD and AUD.")
    inventory = variant.get("inventoryItem") or {}
    cost = inventory.get("unitCost") or {}
    if (variant.get("product") or {}).get("status") != "ACTIVE" or variant.get("availableForSale") is not True:
        blocks.append("Product is not active and available.")
    if inventory.get("tracked") is not True or variant.get("inventoryPolicy") != "DENY":
        blocks.append("Tracked inventory with overselling disabled is needed.")
    quantity = variant.get("inventoryQuantity")
    if type(quantity) is not int or quantity <= 0:
        blocks.append("A known positive stock count is needed.")
    if cost.get("amount") is None or cost.get("currencyCode") != shop["currencyCode"]:
        blocks.append("A Shopify unit cost in the store currency is needed.")
    # First slice deliberately requires no other live/scheduled offer, even on other products.
    # Presence-only inspection covers every discount union type without assuming its eligibility.
    if discounts.get("nodes") or (discounts.get("pageInfo") or {}).get("hasNextPage"):
        blocks.append("Existing active or scheduled discounts need review before creating another.")
    if "nodes" not in discounts or "hasNextPage" not in (discounts.get("pageInfo") or {}):
        blocks.append("The existing-offer check is incomplete.")
    if variant.get("compareAtPrice") is not None:
        if _decimal(variant["compareAtPrice"], "compare-at price") > _decimal(variant.get("price"), "price"):
            blocks.append("The variant already has a marked-down price.")
    if shop.get("taxesIncluded") is not False:
        blocks.append("This first offer workflow requires tax-exclusive prices.")
    return {"ready": not blocks, "blocks": blocks, "variant": variant,
            "currency": shop["currencyCode"], "taxes_included": shop.get("taxesIncluded"),
            "existing_offer_count": len(discounts.get("nodes") or []),
            "write_access": "write_discounts" in scopes}


def _ledger():
    wl = Watchlist()
    wl.db.executescript(LEDGER_SCHEMA)
    return wl


def _fingerprint(data):
    # Write access may be granted after planning; economic/stock facts cannot change silently.
    data = {key: value for key, value in data.items() if key != "write_access"}
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def plan(args, post=None):
    facts = context(args.get("variant_id"), post)
    if not facts["ready"]:
        return {"status": "blocked", **facts}
    percent = _decimal(args.get("percent_off"), "discount percentage from 1 to 30", 1, 30)
    if percent != percent.quantize(Decimal("0.01")):
        raise store.StoreError("Use at most two decimal places for the discount percentage.")
    fee = _decimal(args.get("fee_percent"), "owner-confirmed fee percentage", 0, 20)
    extra = _decimal(args.get("extra_cost_per_unit"), "owner-confirmed extra cost per unit", 0)
    if extra != extra.quantize(Decimal("0.01")):
        raise store.StoreError("Use at most two decimal places for extra cost per unit.")
    floor = _decimal(args.get("minimum_margin_percent"), "minimum contribution margin", 0, 90)
    limit = args.get("redemption_limit")
    if type(limit) is not int or not 1 <= limit <= 100:
        raise store.StoreError("Use a redemption limit from 1 to 100.")
    start, end = _date(args.get("starts_at")), _date(args.get("ends_at"))
    if start < _now() - timedelta(minutes=5) or start > _now() + timedelta(days=7):
        raise store.StoreError("Choose a start time within the next seven days.")
    if end <= start or end - start > timedelta(days=7):
        raise store.StoreError("The offer must expire within seven days of starting.")
    code = str(args.get("code") or "").strip().upper()
    if not re.fullmatch(r"[A-Z0-9][A-Z0-9-]{3,31}", code):
        raise store.StoreError("Use a code of 4 to 32 letters, digits or hyphens.")
    evidence = str(args.get("market_reason") or "").strip()
    if not evidence or len(evidence) > 600:
        raise store.StoreError("A short market reason with its source and check date is needed.")
    variant = facts["variant"]
    price = _decimal(variant.get("price"), "product price", Decimal("0.01"))
    cost = _decimal(variant["inventoryItem"]["unitCost"]["amount"], "Shopify unit cost", Decimal("0.01"))
    sale = (price * (1 - percent / 100)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    contribution = sale * (1 - fee / 100) - cost - extra
    margin = contribution / sale * 100 if sale else Decimal("-1")
    if contribution <= 0 or margin < floor:
        return {"status": "blocked", "blocks": ["Estimated contribution is below the chosen floor."],
                "discounted_unit_price": _cash(sale), "estimated_contribution_per_unit": _cash(contribution),
                "estimated_margin_percent": _cash(margin), "currency": facts["currency"]}
    terms = {"code": code, "product": variant["product"]["title"], "variant": variant["title"],
             "percent_off": str(percent), "starts_at": _stamp(start), "ends_at": _stamp(end),
             "redemption_limit": limit, "currency": facts["currency"], "unit_price": _cash(price),
             "discounted_unit_price": _cash(sale), "shopify_unit_cost": str(cost),
             "fee_percent": str(fee), "extra_cost_per_unit": _cash(extra),
             "minimum_margin_percent": str(floor), "estimated_contribution_per_unit": _cash(contribution),
             "estimated_margin_percent": _cash(margin), "stock_at_check": variant["inventoryQuantity"],
             "market_reason": evidence, "all_buyers": True, "once_per_customer": True,
             "combines_with_other_discounts": False, "one_time_purchases_only": True,
             "minimum_quantity": 1, "redemption_limit_is_not_a_unit_or_spend_cap": True,
             "estimate_basis": "Before tax; extra costs must include packaging and shipping subsidy per unit."}
    proposal = {"terms": terms, "variant_id": variant["id"], "product_id": variant["product"]["id"],
                "fingerprint": _fingerprint(facts)}
    identifier = secrets.token_hex(8)
    wl = _ledger()
    try:
        wl.db.execute("INSERT INTO offers(id,store,code,created_at,proposal,status) VALUES(?,?,?,?,?,?)",
                      (identifier, store._store(), code, _stamp(_now()), json.dumps(proposal), "proposed"))
        wl.db.commit()
    except sqlite3.IntegrityError:
        raise store.StoreError("That code already has an Iris proposal. Check its status or choose another code.")
    finally:
        wl.close()
    return {"status": "proposed", "proposal_id": identifier, "terms": terms,
            "write_access": facts["write_access"], "approval_required": True,
            "expires_in_minutes": 30}


def _row(identifier):
    wl = _ledger()
    try:
        row = wl.db.execute("SELECT * FROM offers WHERE id=? AND store=?", (identifier, store._store())).fetchone()
        if not row:
            raise store.StoreError("That offer proposal was not found for your store.")
        return dict(row)
    finally:
        wl.close()


def _set(identifier, status, discount_id=None, approved=False):
    wl = _ledger()
    try:
        wl.db.execute("UPDATE offers SET status=?, discount_id=COALESCE(?,discount_id), "
                      "approved_at=COALESCE(?,approved_at) WHERE id=? AND store=?",
                      (status, discount_id, _stamp(_now()) if approved else None, identifier, store._store()))
        wl.db.commit()
    finally:
        wl.close()


def _claim(identifier, old, new):
    wl = _ledger()
    try:
        changed = wl.db.execute("UPDATE offers SET status=? WHERE id=? AND store=? AND status=?",
                                (new, identifier, store._store(), old)).rowcount
        wl.db.commit()
        if changed != 1:
            raise store.StoreError("This offer is already being handled. Check its status first.")
    finally:
        wl.close()


def _native_runner():
    """Version-sensitive Hermes adapter seam: absence or any context mismatch fails closed.

    Ordinary exec approval may auto-approve or reuse cached permission. Native clarify instead
    resolves a fresh question ID with the authenticated owner's response, including answered flag.
    """
    try:
        from tools import approval
        from gateway.session_context import get_session_env
        if approval._is_cron_approval_context() or approval._is_single_query_approval_context():
            raise ValueError()
        key = approval.get_current_session_key()
        notify = approval._gateway_notify_cb(key)
        runner = getattr(notify, "__self__", None)
        ctx = runner._ctx
        source = ctx.source
        owner = str(store._profile_value("TELEGRAM_ALLOWED_USERS", "")).strip()
        if not owner.isdigit() or str(source.user_id) != owner or str(source.chat_id) != owner:
            raise ValueError()
        if (source.platform.value != "telegram" or source.chat_type != "dm" or ctx.session_key != key
                or get_session_env("HERMES_SESSION_PLATFORM", "") != "telegram"
                or str(get_session_env("HERMES_SESSION_USER_ID", "")) != owner
                or str(get_session_env("HERMES_SESSION_CHAT_ID", "")) != owner
                or not ctx._run_still_current() or runner._agent_interrupted()
                or not callable(runner._ask_clarify_question)):
            raise ValueError()
        return runner
    except (ImportError, AttributeError, TypeError, ValueError):
        raise store.StoreError("Offer changes need a fresh confirmation in your private Telegram chat with Iris.")


def _confirm(runner, question, terms, action):
    # Hermes prefixes its own question marker; a repeated one reads as noise on a phone.
    question = str(question or "").strip().lstrip("❓").strip()
    if not question or len(question) > 600:
        raise store.StoreError("Iris needs to present a short approval question first.")
    # Iris supplies the question. The native UI presents canonical form fields, without IDs/JSON.
    # These are a consent receipt, not a tool-authored recommendation or announcement.
    # Binding terms come first, in the profile's time zone; Iris already explained the evidence.
    t = terms
    currency = t["currency"]
    zone = profile_timezone()

    def when(value):
        local = _date(value).astimezone(zone)
        return f"{local:%a} {local.day} {local:%b %H:%M}"

    fields = {
        "Action": action, "Code": t["code"], "Product": f"{t['product']} ({t['variant']})",
        "Discount": f"{t['percent_off']}% off {currency} {t['unit_price']}",
        "Discounted unit price": currency + " " + t["discounted_unit_price"],
        "Runs": f"{when(t['starts_at'])} → {when(t['ends_at'])} ({str(zone).split('/')[-1].replace('_', ' ')} time)",
        "Limit": f"{t['redemption_limit']} uses, once per customer; not a cap on units",
        "Who": "All buyers; one-time purchases; cannot combine with other discounts",
        "You keep per unit": f"~{currency} {t['estimated_contribution_per_unit']} ({t['estimated_margin_percent']}%) "
                             f"after cost {currency} {_cash(Decimal(t['shopify_unit_cost']))}, "
                             f"{t['fee_percent']}% fees, {currency} {t['extra_cost_per_unit']} extra; before tax",
    }
    payload = "\n".join(f"{label}: {value}" for label, value in fields.items())
    if len(question + payload) > 3500:
        raise store.StoreError("The offer review is too long. Use a shorter market reason.")
    response, answered = runner._ask_clarify_question(question + "\n\n" + payload,
                                                     ["Approve", "Cancel"], False, rearm=True)
    return (answered is True and response == "Approve" and runner._ctx._run_still_current()
            and not runner._agent_interrupted())


def _input(proposal):
    t = proposal["terms"]
    return {"title": "Iris " + t["code"], "code": t["code"], "context": {"all": "ALL"},
            "startsAt": t["starts_at"], "endsAt": t["ends_at"], "usageLimit": t["redemption_limit"],
            "appliesOncePerCustomer": True,
            "combinesWith": {"orderDiscounts": False, "productDiscounts": False, "shippingDiscounts": False},
            "minimumRequirement": {"quantity": {"greaterThanOrEqualToQuantity": "1"}},
            "customerGets": {"items": {"products": {"productVariantsToAdd": [proposal["variant_id"]]}},
                             "value": {"percentage": float(Decimal(t["percent_off"]) / 100)},
                             "appliesOnOneTimePurchase": True, "appliesOnSubscription": False}}


def _read(code, post=None):
    return store._graphql(READ_QUERY, {"code": code}, post).get("codeDiscountNodeByCode")


def _matches(node, proposal):
    try:
        t = proposal["terms"]
        d = node["codeDiscount"]
        gets = d["customerGets"]
        items = gets["items"]
        variants = items["productVariants"]
        # Shopify may return the parent product when a variant is selected. Check its identity
        # separately and require exactly one explicit variant; never accept a product-wide match.
        products = items["products"]
        return (d["__typename"] == "DiscountCodeBasic" and d["title"] == "Iris " + t["code"]
                and d["status"] in {"ACTIVE", "SCHEDULED"}
                and [n["code"].upper() for n in d["codes"]["nodes"]] == [t["code"]]
                and d["codes"]["pageInfo"]["hasNextPage"] is False
                and _date(d["startsAt"]) == _date(t["starts_at"]) and _date(d["endsAt"]) == _date(t["ends_at"])
                and d["usageLimit"] == t["redemption_limit"] and d["appliesOncePerCustomer"] is True
                and d["combinesWith"] == {"orderDiscounts": False, "productDiscounts": False, "shippingDiscounts": False}
                and d["context"] == {"__typename": "DiscountBuyerSelectionAll", "all": "ALL"}
                and d["minimumRequirement"]["__typename"] == "DiscountMinimumQuantity"
                and str(d["minimumRequirement"]["greaterThanOrEqualToQuantity"]) == "1"
                and gets["appliesOnOneTimePurchase"] is True and gets["appliesOnSubscription"] is False
                and gets["value"]["__typename"] == "DiscountPercentage"
                and Decimal(str(gets["value"]["percentage"])) == Decimal(t["percent_off"]) / 100
                and items["__typename"] == "DiscountProducts"
                and [n["id"] for n in variants["nodes"]] == [proposal["variant_id"]]
                and variants["pageInfo"]["hasNextPage"] is False
                and products["pageInfo"]["hasNextPage"] is False
                and all(n["id"] == proposal["product_id"] for n in products["nodes"])
                and len(products["nodes"]) <= 1)
    except (KeyError, TypeError, InvalidOperation, store.StoreError):
        return False


def status(identifier, post=None):
    row = _row(identifier)
    proposal = json.loads(row["proposal"])
    result = {"status": row["status"], "proposal_id": identifier, "terms": proposal["terms"], "verified": False}
    if row["status"] in {"executing", "uncertain", "verified", "stopping", "stop_uncertain", "deactivated", "expired"}:
        node = _read(row["code"], post)
        same_id = node and (not row["discount_id"] or row["discount_id"] == node.get("id"))
        if same_id and _matches(node, proposal):
            if row["status"] in {"executing", "uncertain", "stop_uncertain"}:
                _set(identifier, "verified", node["id"])
            result.update(status="verified", verified=True, shopify_status=node["codeDiscount"]["status"],
                          redemption_count_async=node["codeDiscount"]["asyncUsageCount"], checkout_tested=False)
        elif same_id and row["discount_id"] and node["codeDiscount"].get("status") == "EXPIRED":
            ended = "deactivated" if row["status"] in {"stopping", "stop_uncertain", "deactivated"} else "expired"
            _set(identifier, ended)
            result.update(status=ended, verified=True, shopify_status="EXPIRED")
        else:
            result.update(status="unverified", verified=False, retry_creation=False)
    return result


def apply(identifier, question, post=None):
    if store._profile_value("IRIS_ENABLE_OFFERS", "0") != "1":
        raise store.StoreError("Shopify offer changes are not enabled for this profile yet.")
    runner = _native_runner()  # happens before reading a ledger or contacting Shopify
    row = _row(identifier)
    if row["status"] != "proposed":
        return status(identifier, post)
    proposal = json.loads(row["proposal"])
    if _now() - _date(row["created_at"]) > timedelta(minutes=30):
        raise store.StoreError("That proposal expired. Recheck the facts and prepare it again.")
    facts = context(proposal["variant_id"], post)
    if not facts.get("write_access"):
        raise store.StoreError("Shopify discount-write access is needed before this offer can be applied.")
    if _fingerprint(facts) != proposal["fingerprint"]:
        raise store.StoreError("Price, cost, stock or existing offers changed. Prepare a fresh proposal.")
    if _read(row["code"], post):
        raise store.StoreError("That code already exists in Shopify. It will not be overwritten.")
    _claim(identifier, "proposed", "confirming")
    try:
        accepted = _confirm(runner, question, proposal["terms"], "create")
    except Exception:
        _set(identifier, "cancelled")
        raise store.StoreError("Owner confirmation could not be completed. No offer was created.")
    if not accepted:
        _set(identifier, "cancelled")
        return {"status": "cancelled", "created": False}
    # Owner may take minutes to respond: re-read all facts and code immediately before mutation.
    try:
        latest_facts = context(proposal["variant_id"], post)
        if (not latest_facts.get("write_access") or _fingerprint(latest_facts) != proposal["fingerprint"]
                or _read(row["code"], post) or _date(proposal["terms"]["ends_at"]) <= _now()
                or _now() - _date(row["created_at"]) > timedelta(minutes=30)):
            raise store.StoreError("The approved offer is stale. Recheck and get fresh approval.")
        _native_runner()
    except store.StoreError:
        _set(identifier, "cancelled")
        raise
    _set(identifier, "executing", approved=True)
    try:
        response = store._graphql(CREATE_MUTATION, {"input": _input(proposal)}, post).get("discountCodeBasicCreate") or {}
        if response.get("userErrors"):
            _set(identifier, "rejected")
            return {"status": "rejected", "created": False, "shopify_errors": response["userErrors"]}
        discount_id = (response.get("codeDiscountNode") or {}).get("id")
        _set(identifier, "uncertain", discount_id)
        return status(identifier, post)
    except store.StoreError:
        _set(identifier, "uncertain")
        return {"status": "uncertain", "verified": False, "retry_creation": False,
                "proposal_id": identifier, "next_operation": "offer_status"}


def deactivate(identifier, question, post=None):
    if store._profile_value("IRIS_ENABLE_OFFERS", "0") != "1":
        raise store.StoreError("Shopify offer changes are not enabled for this profile yet.")
    runner = _native_runner()
    row = _row(identifier)
    if row["status"] != "verified" or not row["discount_id"]:
        raise store.StoreError("Only a verified offer created by Iris can be deactivated.")
    if "write_discounts" not in _scopes(post):
        raise store.StoreError("Shopify discount-write access is needed.")
    node = _read(row["code"], post)
    if not node or node.get("id") != row["discount_id"]:
        raise store.StoreError("The created offer could not be identified. Nothing was changed.")
    proposal = json.loads(row["proposal"])
    if not _matches(node, proposal):
        raise store.StoreError("That offer changed outside Iris. Review it in Shopify before deactivation.")
    _claim(identifier, "verified", "stopping")
    try:
        accepted = _confirm(runner, question, proposal["terms"], "deactivate; earlier orders remain unchanged")
    except Exception:
        _set(identifier, "verified")
        raise store.StoreError("Owner confirmation could not be completed. The offer was not changed.")
    if not accepted:
        _set(identifier, "verified")
        return {"status": "cancelled", "deactivated": False}
    try:
        _native_runner()
        latest = _read(row["code"], post)
        if not latest or latest.get("id") != row["discount_id"] or not _matches(latest, proposal):
            _set(identifier, "verified")
            raise store.StoreError("The offer changed while awaiting approval. Nothing was changed.")
        response = store._graphql(DEACTIVATE_MUTATION, {"id": row["discount_id"]}, post).get("discountCodeDeactivate") or {}
        if response.get("userErrors"):
            _set(identifier, "verified")
            return {"status": "rejected", "deactivated": False, "shopify_errors": response["userErrors"]}
        _set(identifier, "stop_uncertain")
        result = status(identifier, post)
        result["deactivated"] = result["status"] == "deactivated" and result["verified"]
        return result
    except store.StoreError:
        if _row(identifier)["status"] == "stopping":
            _set(identifier, "stop_uncertain")
        raise
