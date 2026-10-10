import copy
import unittest

import helpers  # noqa: F401
from iris_changes import diff, summarize


def p(key, price=100.0, compare_at=None, available=True, title="Serum", product_type="Serum"):
    return {"key": key, "title": title, "product_type": product_type, "tags": [], "url": f"https://x/{key}",
            "price": price, "compare_at": compare_at, "on_sale": bool(compare_at and compare_at > price),
            "currency": "EGP", "available": available}


class Signals(unittest.TestCase):
    def kinds(self, before, after, focus=None):
        return {(s["kind"], s["urgent"]) for s in diff(before, after, focus)}

    def test_first_snapshot_is_a_baseline(self):
        self.assertEqual(diff(None, [p("a")]), [])

    def test_product_watches_report_markdown_and_stock_only(self):
        before = [p("a"), p("b")]
        after = [p("a", price=80, compare_at=100), p("b", available=False), p("c")]
        self.assertEqual(self.kinds(before, after),
                         {("sale_started", True), ("out_of_stock", True)})

    def test_price_moves_wait_for_the_week(self):
        got = diff([p("a", 100)], [p("a", 112)])
        self.assertEqual((got[0]["kind"], got[0]["urgent"], got[0]["size"], got[0]["change_pct"]),
                         ("price_change", False, "major", 12.0))
        self.assertEqual(diff([p("a", 100)], [p("a", 103)]), [])  # under 5% is noise

    def test_focus_limits_urgency_to_the_owners_product_types(self):
        before = [p("x", title="Beard Oil", product_type="Men")]
        after = [p("x", price=80, compare_at=100, title="Beard Oil", product_type="Men")]
        self.assertEqual(self.kinds(before, after, focus=["serum"]), {("sale_started", False)})

    def test_ended_back_and_removed_are_not_urgent(self):
        before = [p("a", 80, 100), p("b", available=False), p("gone")]
        after = [p("a", 100), p("b")]
        self.assertEqual(self.kinds(before, after),
                         {("sale_ended", False), ("back_in_stock", False)})

    def test_no_change_no_signal(self):
        items = [p("a"), p("b")]
        self.assertEqual(diff(items, copy.deepcopy(items)), [])

    def test_missing_price_does_not_end_a_sale(self):
        missing = p("a")
        missing.update(price=None, compare_at=None, on_sale=False)
        self.assertEqual(diff([p("a", 80, 100)], [missing]), [])
        self.assertEqual(diff([missing], [p("a", 80, 100)]), [])

    def test_currency_changes_and_unknown_currency_do_not_make_price_signals(self):
        for currency in ("USD", None, ""):
            with self.subTest(currency=currency):
                changed = p("a", 10)
                changed["currency"] = currency
                self.assertEqual(diff([p("a", 100)], [changed]), [])
                changed.update(compare_at=20, on_sale=True)
                self.assertEqual(diff([p("a", 100)], [changed]), [])
                self.assertEqual(diff([changed], [p("a", 100)]), [])

    def test_stock_change_survives_unknown_price_or_changed_currency(self):
        changed = p("a", available=False)
        changed.update(price=None, currency="USD")
        self.assertEqual(self.kinds([p("a", 80, 100)], [changed]),
                         {("out_of_stock", True)})

    def test_invalid_prices_do_not_create_signals(self):
        for price in (float("nan"), float("inf"), -1, "80", True):
            with self.subTest(price=price):
                changed = p("a")
                changed["price"] = price
                self.assertEqual(diff([p("a", 80, 100)], [changed]), [])

    def test_zero_price_and_normalized_currency_can_be_compared(self):
        changed = p("a", 0)
        changed["currency"] = " egp "
        got = diff([p("a", 100)], [changed])
        self.assertEqual((got[0]["kind"], got[0]["change_pct"]), ("price_change", -100.0))


class Summary(unittest.TestCase):
    def test_price_picture_by_type(self):
        s = summarize([p("a", 300), p("b", 500), p("c", 400, available=False), p("d", 90, product_type="Toner")])
        self.assertEqual(s["Serum"], {"count": 3, "price_min": 300, "price_median": 400, "price_max": 500,
                                      "currency": "EGP", "on_sale": 0, "out_of_stock": 1})
        self.assertEqual(list(s)[0], "Serum")  # biggest group first

    def test_mixed_currency_prices_are_not_aggregated(self):
        other = p("b", 10)
        other["currency"] = "USD"
        picture = summarize([p("a", 300), other])["Serum"]
        self.assertIsNone(picture["currency"])
        self.assertIsNone(picture["price_median"])
        self.assertIsNone(picture["price_min"])

    def test_unknown_currency_is_preserved(self):
        unknown = p("a", 300)
        unknown["currency"] = None
        picture = summarize([unknown])["Serum"]
        self.assertIsNone(picture["currency"])
        self.assertEqual(picture["price_min"], 300)


if __name__ == "__main__":
    unittest.main()
