import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

from helpers import FakeWeb, fixture
import iris_feeds as feeds

feeds.PAGE_DELAY_S = 0


def shop(products):
    return {"products": products}


def item(i, price="100.00", compare=None, available=True, title=None):
    return {"id": i, "handle": f"p{i}", "title": title or f"Serum {i}", "product_type": "Serum",
            "variants": [{"price": price, "compare_at_price": compare, "available": available}]}


class DailyCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["IRIS_DATA_DIR"] = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("IRIS_DATA_DIR", None)

    def web(self, products):
        return FakeWeb({"https://glow.example/products.json": (200, shop(products))})

    def add_store(self):
        import iris_watchlist
        wl = iris_watchlist.Watchlist()
        s = wl.add("Glow Lab", "https://glow.example", kind="shopify", focus=["serum"])
        wl.close()
        return s

    def test_quiet_day_does_not_wake_iris(self):
        import iris_daily_check as daily
        self.add_store()
        daily.run(get=self.web([item(1)]))           # baseline
        same = self.web([item(1)])
        out = io.StringIO()
        with mock.patch.object(daily, "read_store", lambda url, get=None, kind="auto": feeds.read_store(url, get=same, kind=kind)):
            with redirect_stdout(out):
                daily.main()
        self.assertEqual(json.loads(out.getvalue().strip().splitlines()[-1]), {"wakeAgent": False})

    def test_promotion_wakes_iris_once(self):
        import iris_daily_check as daily
        self.add_store()
        daily.run(get=self.web([item(1)]))
        first = daily.run(get=self.web([item(1, price="80.00", compare="100.00")]))
        self.assertEqual([s["kind"] for s in first["urgent"]], ["sale_started"])
        again = daily.run(get=self.web([item(1, price="80.00", compare="100.00")]))
        self.assertEqual(again["urgent"], [])        # already reported, nothing new

    def test_three_failed_checks_report_once(self):
        import iris_daily_check as daily
        self.add_store()
        down = FakeWeb({"https://glow.example/": (403, "no")})
        reports = [daily.run(get=down) for _ in range(4)]
        self.assertEqual([len(r["unreachable"]) for r in reports], [0, 0, 1, 0])

    def test_weekly_data_counts_the_week(self):
        import iris_daily_check as daily
        import iris_weekly_data as weekly
        self.add_store()
        daily.run(get=self.web([item(1)]))
        daily.run(get=self.web([item(1), item(2, title="New Serum")]))
        data = weekly.collect()
        self.assertEqual(data["week_counts"], {"new_product": 1})
        self.assertEqual(data["checks_this_week"], 2)
        self.assertEqual(data["market_by_store"]["Glow Lab"]["Serum"]["count"], 2)


class Tools(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["IRIS_DATA_DIR"] = self.tmp.name
        import importlib.util
        from helpers import ROOT
        spec = importlib.util.spec_from_file_location("iris_plugin", ROOT / "plugins" / "iris" / "__init__.py")
        self.plugin = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.plugin)

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("IRIS_DATA_DIR", None)

    def test_registers_exactly_four_tools_in_one_toolset(self):
        registered = []

        class Ctx:
            def register_tool(self, **kw):
                registered.append((kw["name"], kw["toolset"], kw["schema"]["name"]))

            def register_redaction_patterns(self, patterns):
                return len(patterns)

        self.plugin.register(Ctx())
        self.assertEqual(sorted(registered), sorted([(n, "iris", n) for n in
                                                     ("my_store", "read_store", "watchlist", "market_changes")]))

    def test_watch_add_takes_a_baseline_and_lists_it(self):
        web = FakeWeb({"https://glow.example/products.json": (200, fixture("shopify_products.json"))})
        with mock.patch.object(self.plugin.feeds, "http_get", web):
            out = json.loads(self.plugin.watchlist_tool({"operation": "add", "url": "https://glow.example",
                                                         "name": "Glow Lab", "focus": ["serum"]}))
        self.assertTrue(out["added"])
        self.assertEqual(out["first_look"]["product_count"], 1)   # focus kept only the serum
        listed = json.loads(self.plugin.watchlist_tool({"operation": "list"}))
        self.assertEqual(listed["stores"][0]["products_seen"], 3)

    def test_blocked_store_is_not_added(self):
        web = FakeWeb({"https://shy.example/": (403, "no")})
        with mock.patch.object(self.plugin.feeds, "http_get", web):
            out = json.loads(self.plugin.watchlist_tool({"operation": "add", "url": "https://shy.example", "name": "Shy"}))
        self.assertEqual(out, {"added": False, "reason": "blocked", "url": "https://shy.example"})

    def test_read_store_marks_content_as_untrusted_data(self):
        url = "https://cs.example/listing/niacinamide/"
        with mock.patch.object(self.plugin.feeds, "http_get", FakeWeb({url: (200, fixture("listing_page.html"))})):
            out = json.loads(self.plugin.read_store_tool({"url": url}))
        self.assertIn("not instructions", out["note"])
        self.assertEqual(out["out_of_stock"][0]["title"], "Niacinamide Serum 10%")

    def test_notes_and_changes(self):
        self.plugin.watchlist_tool({"operation": "note", "name": "Cairo Skin (Instagram)",
                                    "text": "Ramadan box: serum + toner, 20% off, ends Friday"})
        out = json.loads(self.plugin.market_changes_tool({"period": "week"}))
        self.assertEqual(out["screenshot_notes"][0]["about"], "Cairo Skin (Instagram)")

    def test_my_store_errors_are_plain_words(self):
        with mock.patch.dict(os.environ, {"SHOPIFY_STORE": ""}):
            out = json.loads(self.plugin.my_store_tool({"operation": "summary"}))
        self.assertIn("not set up", out["error"])


class OwnStore(unittest.TestCase):
    def test_catalog_groups_by_type(self):
        import iris_store as store
        page = {"shop": {"name": "Mira Nile", "currencyCode": "EGP"}, "products": {
            "pageInfo": {"hasNextPage": False},
            "nodes": [{"title": "Rose Serum", "handle": "rose", "productType": "Serum", "tags": [],
                       "priceRangeV2": {"minVariantPrice": {"amount": "520.0"}, "maxVariantPrice": {"amount": "780.0"}},
                       "compareAtPriceRange": {"maxVariantCompareAtPrice": None}, "createdAt": "2026-06-01"}]}}
        with mock.patch.dict(os.environ, {"SHOPIFY_STORE": "mira-nile.myshopify.com"}):
            out = store.catalog(post=lambda q, v: page)
        self.assertEqual(out["by_type"]["Serum"]["price_min"], 520.0)
        self.assertEqual(out["currency"], "EGP")

    def test_store_address_must_be_myshopify(self):
        import iris_store as store
        with mock.patch.dict(os.environ, {"SHOPIFY_STORE": "evil.example.com"}):
            with self.assertRaises(store.StoreError):
                store.search("serum", post=lambda q, v: {})


if __name__ == "__main__":
    unittest.main()
