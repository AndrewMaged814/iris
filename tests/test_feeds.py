import json
import unittest

from helpers import FakeWeb, fixture
import iris_feeds as feeds

feeds.PAGE_DELAY_S = 0


class ShopifyFeed(unittest.TestCase):
    def test_reads_products_prices_sales_and_stock(self):
        web = FakeWeb({"https://glow.example/products.json": (200, fixture("shopify_products.json"))})
        r = feeds.read_store("glow.example", get=web)
        self.assertEqual((r["access"], r["source"], len(r["products"])), ("ok", "shopify", 3))
        serum, sunscreen, toner = r["products"]
        self.assertEqual(serum["price"], 450.0)
        self.assertFalse(serum["on_sale"])
        self.assertEqual(sunscreen["tags"], ["spf", "summer"])  # comma string tags
        self.assertEqual((toner["price"], toner["compare_at"], toner["on_sale"]), (300.0, 350.0, True))
        self.assertTrue(toner["available"])  # one variant in stock is enough

    def test_static_host_repeating_page_one_stops(self):
        big = {"products": [{"id": i, "handle": f"p{i}", "title": f"P{i}", "variants": [{"price": "10"}]} for i in range(250)]}
        web = FakeWeb({"https://static.example/shop/products.json": (200, big)})
        r = feeds.read_store("https://static.example/shop/", get=web)
        self.assertEqual(len(r["products"]), 250)
        self.assertEqual(len(web.calls), 2)  # page 2 repeated page 1, so reading stopped

    def test_store_under_a_path_like_github_pages(self):
        web = FakeWeb({"https://me.github.io/world/glow/products.json": (200, fixture("shopify_products.json"))})
        r = feeds.read_store("https://me.github.io/world/glow/", get=web)
        self.assertEqual(r["source"], "shopify")

    def test_blocked_is_reported_not_worked_around(self):
        web = FakeWeb({"https://shy.example/": (403, "Forbidden")})
        r = feeds.read_store("https://shy.example", get=web)
        self.assertEqual(r["access"], "blocked")
        self.assertEqual(len(web.calls), 1)


class WooAndPages(unittest.TestCase):
    def test_woocommerce_minor_units_and_sale(self):
        web = FakeWeb({"https://nile.example/wp-json/wc/store/v1/products": (200, fixture("woo_products.json"))})
        r = feeds.read_store("https://nile.example", get=web)
        self.assertEqual(r["source"], "woocommerce")
        rose, cream = r["products"]
        self.assertEqual((rose["price"], rose["compare_at"], rose["on_sale"], rose["currency"]), (399.0, 499.0, True, "EGP"))
        self.assertFalse(cream["available"])

    def test_json_ld_listing_page(self):
        url = "https://cs.example/listing/niacinamide/"
        web = FakeWeb({url: (200, fixture("listing_page.html"))})
        r = feeds.read_store(url, get=web)
        self.assertEqual(r["source"], "page")
        (p,) = r["products"]
        self.assertEqual((p["title"], p["price"], p["compare_at"], p["on_sale"]), ("Niacinamide Serum 10%", 420.0, 480.0, True))
        self.assertFalse(p["available"])
        self.assertIn("Size: 30 ml", p["tags"])

    def test_missing_page(self):
        r = feeds.read_store("https://gone.example/listing/x", get=FakeWeb({}))
        self.assertEqual(r["access"], "not_found")

    def test_wrong_content_type_json_still_parses(self):
        self.assertIsInstance(feeds._json_or_none(fixture("woo_products.json")), list)


class Guard(unittest.TestCase):
    def test_private_addresses_refused_by_fallback_guard(self):
        for url in ("http://127.0.0.1/", "http://169.254.169.254/latest", "file:///etc/passwd"):
            with self.assertRaises(feeds.FetchError):
                feeds._basic_guard(url)


if __name__ == "__main__":
    unittest.main()
