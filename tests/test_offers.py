"""Offline contracts for bounded Shopify offers and authenticated native owner confirmation."""
import copy
import importlib.util
import json
import os
import sys
import tempfile
import types
import unittest
from datetime import timedelta
from unittest import mock

from helpers import ROOT
import iris_offers as offers
import iris_store as store

VARIANT = "gid://shopify/ProductVariant/1"
PRODUCT = "gid://shopify/Product/1"


class Shopify:
    def __init__(self):
        self.scopes = offers.READ_SCOPES | {"write_discounts"}
        self.facts = {
            "shop": {"currencyCode": "EGP", "taxesIncluded": False},
            "productVariant": {"id": VARIANT, "title": "50 ml", "price": "320.00",
                               "compareAtPrice": None, "availableForSale": True,
                               "inventoryQuantity": 40, "inventoryPolicy": "DENY",
                               "product": {"id": PRODUCT, "title": "Sunscreen", "status": "ACTIVE"},
                               "inventoryItem": {"tracked": True, "unitCost": {"amount": "120.00", "currencyCode": "EGP"}}},
            "discountNodes": {"pageInfo": {"hasNextPage": False}, "nodes": []}}
        self.node = None
        self.writes = []
        self.error = None
        self.timeout_create = False
        self.fail_read = False
        self.corrupt_created = False

    def __call__(self, query, variables):
        if "IrisOfferScopes" in query:
            return {"currentAppInstallation": {"accessScopes": [{"handle": s} for s in self.scopes]}}
        if "IrisOfferContext" in query:
            return copy.deepcopy(self.facts)
        if "IrisOfferRead" in query:
            if self.fail_read:
                raise store.StoreError("Shopify could not be reached.")
            return {"codeDiscountNodeByCode": copy.deepcopy(self.node)}
        if "IrisOfferCreate" in query:
            self.writes.append((query, copy.deepcopy(variables)))
            if self.error:
                return {"discountCodeBasicCreate": {"userErrors": [{"message": self.error}], "codeDiscountNode": None}}
            value = variables["input"]
            d = {k: copy.deepcopy(value[k]) for k in ("title", "startsAt", "endsAt", "usageLimit", "appliesOncePerCustomer", "combinesWith", "context")}
            d.update(__typename="DiscountCodeBasic", status="ACTIVE", asyncUsageCount=0,
                     codes={"pageInfo": {"hasNextPage": False}, "nodes": [{"code": value["code"]}]},
                     context={"__typename": "DiscountBuyerSelectionAll", "all": "ALL"},
                     minimumRequirement={"__typename": "DiscountMinimumQuantity", "greaterThanOrEqualToQuantity": "1"},
                     customerGets={"appliesOnOneTimePurchase": True, "appliesOnSubscription": False,
                                   "value": {"__typename": "DiscountPercentage", "percentage": value["customerGets"]["value"]["percentage"]},
                                   "items": {"__typename": "DiscountProducts",
                                             "products": {"nodes": [{"id": PRODUCT}], "pageInfo": {"hasNextPage": False}},
                                             "productVariants": {"nodes": [{"id": VARIANT}], "pageInfo": {"hasNextPage": False}}}})
            if self.corrupt_created:
                d["customerGets"]["appliesOnSubscription"] = True
            self.node = {"id": "gid://shopify/DiscountCodeNode/1", "codeDiscount": d}
            if self.timeout_create:
                raise store.StoreError("Shopify could not be reached.")
            return {"discountCodeBasicCreate": {"codeDiscountNode": {"id": self.node["id"]}, "userErrors": []}}
        if "IrisOfferStop" in query:
            self.writes.append((query, copy.deepcopy(variables)))
            self.node["codeDiscount"]["status"] = "EXPIRED"
            return {"discountCodeDeactivate": {"codeDiscountNode": {"id": self.node["id"]}, "userErrors": []}}
        raise AssertionError("Unexpected query")


class Runner:
    def __init__(self):
        self.current = True
        self.interrupted = False
        self.answer = ("Approve", True)
        self.questions = []
        self.on_question = None
        self._ctx = types.SimpleNamespace(
            session_key="owner-session", source=types.SimpleNamespace(
                platform=types.SimpleNamespace(value="telegram"), user_id="42", chat_id="42", chat_type="dm"),
            _run_still_current=lambda: self.current)

    def _agent_interrupted(self):
        return self.interrupted

    def notify(self, _data):
        pass

    def _ask_clarify_question(self, question, choices, multi_select, rearm=True):
        self.questions.append((question, choices))
        if self.on_question:
            self.on_question()
        return self.answer


class Offers(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = mock.patch.dict(os.environ, {"SHOPIFY_STORE": "test-store.myshopify.com", "IRIS_DATA_DIR": self.tmp.name,
                                               "IRIS_ENABLE_OFFERS": "1", "TELEGRAM_ALLOWED_USERS": "42"})
        self.env.start()
        self.secret = mock.patch.object(store, "_profile_value", os.environ.get)
        self.secret.start()
        # The Watchlist module may have been reloaded under a profile-scope mock by another test.
        self.data = mock.patch("iris_watchlist._profile_value", os.environ.get)
        self.data.start()
        self.shop = Shopify()
        self.runner = Runner()
        self.session = {"HERMES_SESSION_PLATFORM": "telegram", "HERMES_SESSION_USER_ID": "42", "HERMES_SESSION_CHAT_ID": "42"}
        self.cron = False
        self.single = False
        self.approval = types.ModuleType("tools.approval")
        self.approval._is_cron_approval_context = lambda: self.cron
        self.approval._is_single_query_approval_context = lambda: self.single
        self.approval.get_current_session_key = lambda: "owner-session"
        self.approval._gateway_notify_cb = lambda key: self.runner.notify
        tools = types.ModuleType("tools")
        tools.approval = self.approval
        context = types.ModuleType("gateway.session_context")
        context.get_session_env = lambda key, default="": self.session.get(key, default)
        self.modules = mock.patch.dict(sys.modules, {"tools": tools, "tools.approval": self.approval,
                                                    "gateway": types.ModuleType("gateway"), "gateway.session_context": context})
        self.modules.start()

    def tearDown(self):
        self.modules.stop()
        self.data.stop()
        self.secret.stop()
        self.env.stop()
        self.tmp.cleanup()

    def args(self, **extra):
        now = offers._now()
        return {"variant_id": VARIANT, "code": "SUN10", "percent_off": 10,
                "fee_percent": 3, "extra_cost_per_unit": 15, "minimum_margin_percent": 20,
                "redemption_limit": 20, "starts_at": offers._stamp(now),
                "ends_at": offers._stamp(now + timedelta(days=2)),
                "market_reason": "Competitor SPF50 gel EGP360, checked today: https://example.com/sun", **extra}

    def plan(self, **extra):
        return offers.plan(self.args(**extra), self.shop)

    def apply(self, identifier):
        return offers.apply(identifier, "Create this response offer?", self.shop)

    def test_plan_is_read_only_and_calculates_contribution(self):
        proposal = self.plan()
        self.assertEqual(proposal["terms"]["discounted_unit_price"], "288.00")
        self.assertEqual(proposal["terms"]["estimated_contribution_per_unit"], "144.36")
        self.assertTrue(proposal["terms"]["redemption_limit_is_not_a_unit_or_spend_cap"])
        self.assertEqual(self.shop.writes, [])

    def test_missing_access_fails_closed(self):
        self.shop.scopes = {"read_products"}
        result = self.plan()
        self.assertFalse(result["ready"])
        self.assertEqual(result["missing_scopes"], ["read_discounts"])

    def test_write_scope_includes_read_without_requesting_inventory_access(self):
        self.shop.scopes = {"read_products", "write_discounts"}
        identifier = self.plan()["proposal_id"]
        self.assertTrue(self.apply(identifier)["verified"])

    def test_unknown_cost_currency_stock_tracking_overselling_and_tax_block(self):
        for field, value in [("inventoryQuantity", None), ("inventoryQuantity", 0), ("inventoryPolicy", "CONTINUE"),
                             ("availableForSale", False), ("inventoryItem", {"tracked": False}),
                             ("inventoryItem", {"tracked": True, "unitCost": {"amount": "10", "currencyCode": "USD"}})]:
            with self.subTest(field=field, value=value):
                self.shop = Shopify()
                self.shop.facts["productVariant"][field] = value
                self.assertEqual(self.plan()["status"], "blocked")
        self.shop = Shopify()
        self.shop.facts["shop"]["taxesIncluded"] = True
        self.assertEqual(self.plan()["status"], "blocked")
        self.shop = Shopify()
        self.shop.facts["shop"]["currencyCode"] = "JPY"
        self.shop.facts["productVariant"]["inventoryItem"]["unitCost"]["currencyCode"] = "JPY"
        self.assertEqual(self.plan()["status"], "blocked")
        self.assertEqual(self.shop.writes, [])

    def test_existing_offers_including_unknown_app_types_and_incomplete_scan_block(self):
        for page in [{"nodes": [{"id": "other", "discount": {"__typename": "FutureDiscountType"}}], "pageInfo": {"hasNextPage": False}},
                     {"nodes": [], "pageInfo": {"hasNextPage": True}}, {}]:
            self.shop.facts["discountNodes"] = page
            self.assertEqual(self.plan()["status"], "blocked")

    def test_marked_down_product_blocks(self):
        self.shop.facts["productVariant"]["compareAtPrice"] = "400.00"
        self.assertEqual(self.plan()["status"], "blocked")

    def test_margin_floor_blocks(self):
        self.assertEqual(self.plan(extra_cost_per_unit=200)["status"], "blocked")
        self.assertEqual(self.shop.writes, [])

    def test_invalid_money_dates_limits_and_codes_cannot_be_proposed(self):
        cases = [{"percent_off": 31}, {"percent_off": 10.123}, {"fee_percent": "NaN"},
                 {"extra_cost_per_unit": -1}, {"extra_cost_per_unit": 15.123},
                 {"redemption_limit": True}, {"redemption_limit": 101}, {"code": "x"}, {"market_reason": ""},
                 {"starts_at": "2026-10-01"}, {"ends_at": offers._stamp(offers._now() + timedelta(days=10))}]
        for case in cases:
            with self.subTest(case=case), self.assertRaises(store.StoreError):
                self.plan(**case)

    def test_create_requires_live_owner_and_verifies_all_terms(self):
        identifier = self.plan()["proposal_id"]
        result = self.apply(identifier)
        self.assertTrue(result["verified"])
        self.assertFalse(result["checkout_tested"])
        self.assertEqual(len(self.shop.writes), 1)
        value = self.shop.writes[0][1]["input"]
        self.assertEqual(value["context"], {"all": "ALL"})
        self.assertEqual(value["customerGets"]["items"], {"products": {"productVariantsToAdd": [VARIANT]}})
        self.assertFalse(value["customerGets"]["appliesOnSubscription"])
        self.assertIn('Discounted unit price: EGP 288.00', self.runner.questions[0][0])
        self.assertIn('Action: create', self.runner.questions[0][0])
        self.assertNotIn(VARIANT, self.runner.questions[0][0])
        card = self.runner.questions[0][0]
        self.assertNotIn("UTC)", card)  # owner-facing times use the profile's zone
        self.assertNotIn("Market evidence", card)
        self.assertIn("not a cap on units", card)
        self.assertLessEqual(len(card.splitlines()), 12)
        self.apply(identifier)
        self.assertEqual(len(self.shop.writes), 1)

    def test_cancel_timeout_free_text_and_unanswered_approve_never_create(self):
        for index, answer in enumerate([("Cancel", True), ("", False), ("I approve", True), ("Approve", False)]):
            self.runner.answer = answer
            identifier = self.plan(code=f"SUN-{index}")["proposal_id"]
            self.assertEqual(self.apply(identifier)["status"], "cancelled")
        self.assertEqual(self.shop.writes, [])

    def test_cron_cli_group_other_owner_expired_turn_and_missing_callback_deny(self):
        identifier = self.plan()["proposal_id"]
        cases = [lambda: setattr(self, "cron", True), lambda: setattr(self, "single", True),
                 lambda: setattr(self.runner._ctx.source, "chat_type", "group"),
                 lambda: setattr(self.runner._ctx.source, "user_id", "43"),
                 lambda: setattr(self.runner, "current", False), lambda: setattr(self.runner, "interrupted", True),
                 lambda: self.session.update(HERMES_SESSION_PLATFORM="cli"),
                 lambda: setattr(self.approval, "_gateway_notify_cb", lambda key: None)]
        for change in cases:
            self.cron = self.single = False
            self.runner = Runner()
            self.session["HERMES_SESSION_PLATFORM"] = "telegram"
            self.approval._gateway_notify_cb = lambda key: self.runner.notify
            change()
            with self.assertRaises(store.StoreError):
                self.apply(identifier)
        self.assertEqual(self.shop.writes, [])
        self.assertEqual(self.runner.questions, [])

    def test_disabled_flag_and_missing_write_scope_deny(self):
        identifier = self.plan()["proposal_id"]
        with mock.patch.dict(os.environ, {"IRIS_ENABLE_OFFERS": "0"}), self.assertRaises(store.StoreError):
            self.apply(identifier)
        self.shop.scopes.remove("write_discounts")
        with self.assertRaises(store.StoreError):
            self.apply(identifier)
        self.assertEqual(self.shop.writes, [])

    def test_fact_changes_before_or_during_approval_cancel(self):
        identifier = self.plan()["proposal_id"]
        self.shop.facts["productVariant"]["price"] = "321.00"
        with self.assertRaises(store.StoreError):
            self.apply(identifier)
        self.shop.facts["productVariant"]["price"] = "320.00"
        self.runner.on_question = lambda: self.shop.facts["productVariant"].update(inventoryQuantity=39)
        with self.assertRaises(store.StoreError):
            self.apply(identifier)
        self.assertEqual(self.shop.writes, [])

    def test_turn_interrupt_after_answer_does_not_authorize(self):
        identifier = self.plan()["proposal_id"]
        self.runner.on_question = lambda: setattr(self.runner, "interrupted", True)
        self.assertEqual(self.apply(identifier)["status"], "cancelled")
        self.assertEqual(self.shop.writes, [])

    def test_write_scope_revoked_during_approval_cancels(self):
        identifier = self.plan()["proposal_id"]
        self.runner.on_question = lambda: self.shop.scopes.remove("write_discounts")
        with self.assertRaises(store.StoreError):
            self.apply(identifier)
        self.assertEqual(self.shop.writes, [])

    def test_concurrent_reentrant_apply_does_not_repeat_confirmation_or_mutation(self):
        identifier = self.plan()["proposal_id"]
        self.runner.on_question = lambda: self.assertFalse(self.apply(identifier)["verified"])
        self.assertTrue(self.apply(identifier)["verified"])
        self.assertEqual(len(self.runner.questions), 1)
        self.assertEqual(len(self.shop.writes), 1)

    def test_ambiguous_timeout_is_read_back_without_recreating(self):
        identifier = self.plan()["proposal_id"]
        self.shop.timeout_create = True
        result = self.apply(identifier)
        self.assertEqual(result["status"], "uncertain")
        self.assertFalse(result["retry_creation"])
        self.assertTrue(offers.status(identifier, self.shop)["verified"])
        self.apply(identifier)
        self.assertEqual(len(self.shop.writes), 1)

    def test_shopify_user_error_is_rejected(self):
        identifier = self.plan()["proposal_id"]
        self.shop.error = "Invalid code"
        self.assertEqual(self.apply(identifier)["status"], "rejected")
        self.assertFalse(offers.status(identifier, self.shop)["verified"])

    def test_wrong_readback_never_reports_created(self):
        identifier = self.plan()["proposal_id"]
        self.shop.corrupt_created = True
        self.assertFalse(self.apply(identifier)["verified"])
        self.assertEqual(offers._row(identifier)["status"], "uncertain")

    def test_readback_refuses_broader_target_more_codes_wrong_buyer_and_stacking(self):
        identifier = self.plan()["proposal_id"]
        self.apply(identifier)
        proposal = json.loads(offers._row(identifier)["proposal"])
        good = copy.deepcopy(self.shop.node)
        cases = [lambda d: d["customerGets"]["items"]["productVariants"]["nodes"].append({"id": "gid://shopify/ProductVariant/2"}),
                 lambda d: d["customerGets"]["items"]["products"]["nodes"].append({"id": "gid://shopify/Product/2"}),
                 lambda d: d["codes"]["nodes"].append({"code": "OTHER"}),
                 lambda d: d["context"].update(all="NOT_ALL"),
                 lambda d: d["combinesWith"].update(shippingDiscounts=True),
                 lambda d: d.update(usageLimit=None),
                 lambda d: d["customerGets"].update(appliesOnSubscription=True)]
        for change in cases:
            node = copy.deepcopy(good)
            change(node["codeDiscount"])
            self.assertFalse(offers._matches(node, proposal))

    def test_deactivate_requires_fresh_approval_and_verifies_expiry(self):
        identifier = self.plan()["proposal_id"]
        self.apply(identifier)
        self.runner.answer = ("Cancel", True)
        self.assertFalse(offers.deactivate(identifier, "Stop this offer?", self.shop)["deactivated"])
        self.assertEqual(len(self.shop.writes), 1)
        self.runner.answer = ("Approve", True)
        result = offers.deactivate(identifier, "Stop this offer?", self.shop)
        self.assertEqual(result["status"], "deactivated")
        self.assertTrue(result["verified"])
        self.assertEqual(len(self.runner.questions), 3)
        self.assertEqual(len(self.shop.writes), 2)
        self.assertEqual(self.shop.writes[1][1], {"id": "gid://shopify/DiscountCodeNode/1"})

    def test_cannot_stop_foreign_or_modified_offer(self):
        identifier = self.plan()["proposal_id"]
        with self.assertRaises(store.StoreError):
            offers.deactivate(identifier, "Stop?", self.shop)
        self.apply(identifier)
        self.shop.node["codeDiscount"]["usageLimit"] = 50
        with self.assertRaises(store.StoreError):
            offers.deactivate(identifier, "Stop?", self.shop)
        self.assertEqual(len(self.shop.writes), 1)

    def test_natural_expiry_is_not_reported_as_owner_deactivation(self):
        identifier = self.plan()["proposal_id"]
        self.apply(identifier)
        self.shop.node["codeDiscount"]["status"] = "EXPIRED"
        self.assertEqual(offers.status(identifier, self.shop)["status"], "expired")
        self.assertEqual(len(self.shop.writes), 1)

    def test_failed_stop_prompt_preserves_a_retryable_verified_offer(self):
        identifier = self.plan()["proposal_id"]
        self.apply(identifier)
        with mock.patch.object(self.runner, "_ask_clarify_question", side_effect=RuntimeError("Delivery failed")), self.assertRaises(store.StoreError):
            offers.deactivate(identifier, "Stop this offer?", self.shop)
        self.assertEqual(offers._row(identifier)["status"], "verified")
        self.assertEqual(len(self.shop.writes), 1)

    def test_cross_store_ledger_and_duplicate_code_are_isolated(self):
        identifier = self.plan()["proposal_id"]
        with self.assertRaises(store.StoreError):
            self.plan()
        with mock.patch.dict(os.environ, {"SHOPIFY_STORE": "other-store.myshopify.com"}), self.assertRaises(store.StoreError):
            offers.status(identifier, self.shop)

    def test_expired_proposal_cannot_create(self):
        identifier = self.plan()["proposal_id"]
        wl = offers._ledger()
        wl.db.execute("UPDATE offers SET created_at=? WHERE id=?", (offers._stamp(offers._now() - timedelta(minutes=31)), identifier))
        wl.db.commit()
        wl.close()
        with self.assertRaises(store.StoreError):
            self.apply(identifier)
        self.assertEqual(self.shop.writes, [])

    def test_plugin_keeps_four_tools_and_has_no_approval_argument(self):
        spec = importlib.util.spec_from_file_location("iris_offer_plugin", ROOT / "plugins" / "iris" / "__init__.py")
        plugin = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin)
        self.assertEqual(set(plugin.HANDLERS), {"my_store", "read_store", "watchlist", "market_changes"})
        properties = plugin.SCHEMAS["my_store"]["parameters"]["properties"]
        self.assertNotIn("approved", properties)
        with mock.patch.object(offers, "_native_runner", side_effect=store.StoreError("Private owner confirmation required")):
            result = json.loads(plugin.my_store_tool({"operation": "apply_offer", "proposal_id": "fake", "approved": True}))
        self.assertIn("error", result)
        self.assertEqual(self.shop.writes, [])


if __name__ == "__main__":
    unittest.main()
