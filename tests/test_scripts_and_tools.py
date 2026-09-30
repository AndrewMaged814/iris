import io
import importlib.util
import json
import os
import sys
import tempfile
import types
import unittest
from contextlib import redirect_stdout
from pathlib import Path
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
        lines = out.getvalue().strip().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[0]), {"stores_checked": 1, "urgent": 0, "other_changes_today": 0})
        self.assertEqual(json.loads(lines[1]), {"wakeAgent": False})

    def test_urgent_daily_stdout_is_only_json_data(self):
        import iris_daily_check as daily
        self.add_store()
        daily.run(get=self.web([item(1)]))
        changed = self.web([item(1, price="80.00", compare="100.00")])
        out = io.StringIO()
        with mock.patch.object(daily, "read_store", lambda url, get=None, kind="auto": feeds.read_store(url, get=changed, kind=kind)):
            with redirect_stdout(out):
                self.assertEqual(daily.main(), 0)
        report = json.loads(out.getvalue())
        self.assertEqual([signal["kind"] for signal in report["urgent"]], ["sale_started"])
        self.assertIn("not instructions", report["note"])
        self.assertNotIn("wakeAgent", report)

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
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(weekly.main(), 0)
        data = json.loads(out.getvalue())
        self.assertEqual(data["week_counts"], {"new_product": 1})
        self.assertEqual(data["checks_this_week"], 2)
        self.assertEqual(data["market_by_store"]["Glow Lab"]["Serum"]["count"], 2)
        self.assertIn("not instructions", data["note"])


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

    def test_product_page_evidence_reaches_iris_without_a_sale_claim(self):
        result = {"url": "https://glow.example/products/gel", "source": "page", "access": "ok",
                  "scope": "product", "page_text": "Buy 2 get 2 free; eligible products only",
                  "products": [{"title": "Gel", "description": "50 ml for oily skin", "price": 360}]}
        with mock.patch.object(self.plugin.feeds, "read_store", return_value=result):
            out = json.loads(self.plugin.read_store_tool({"url": result["url"]}))
        self.assertEqual(out["scope"], "product")
        self.assertEqual(out["products"][0]["description"], "50 ml for oily skin")
        self.assertIn("eligible products", out["page_text"])
        self.assertFalse(out["products"][0]["on_sale"])
        self.assertIn("page_text", out["note"])

    def test_market_changes_exposes_limited_observation_history(self):
        from iris_watchlist import Watchlist
        wl = Watchlist()
        s = wl.add("Glow", "https://glow.example")
        wl.save_snapshot(s["id"], {"access": "ok", "products": []})
        wl.save_snapshot(s["id"], {"access": "blocked", "products": []})
        wl.close()
        out = json.loads(self.plugin.market_changes_tool({"period": "week"}))
        coverage = out["observation_by_store"]["Glow"]
        self.assertEqual(coverage["checks"], 1)
        self.assertEqual(coverage["first_checked"], coverage["last_checked"])
        self.assertEqual(out["signals"], [])

    def test_my_store_errors_are_plain_words(self):
        with mock.patch.dict(os.environ, {"SHOPIFY_STORE": ""}):
            out = json.loads(self.plugin.my_store_tool({"operation": "summary"}))
        self.assertIn("not set up", out["error"])


class OwnStore(unittest.TestCase):
    def test_catalog_groups_by_type(self):
        import iris_store as store
        page = {"shop": {"name": "Mira Nile", "currencyCode": "EGP"}, "products": {
            "pageInfo": {"hasNextPage": False},
            "nodes": [{"title": "Rose Serum", "handle": "rose", "productType": "Serum", "tags": ["iris-demo"],
                       "priceRangeV2": {"minVariantPrice": {"amount": "520.0"}, "maxVariantPrice": {"amount": "780.0"}},
                       "compareAtPriceRange": {"maxVariantCompareAtPrice": None}, "createdAt": "2026-06-01"}]}}
        with mock.patch.dict(os.environ, {"SHOPIFY_STORE": "mira-nile.myshopify.com"}):
            out = store.catalog(post=lambda q, v: page)
        self.assertEqual(out["by_type"]["Serum"]["price_min"], 520.0)
        self.assertEqual(out["currency"], "EGP")
        self.assertEqual(out["by_type"]["Serum"]["products"][0]["tags"], ["iris-demo"])

    def test_store_address_must_be_myshopify(self):
        import iris_store as store
        with mock.patch.dict(os.environ, {"SHOPIFY_STORE": "evil.example.com"}):
            with self.assertRaises(store.StoreError):
                store.search("serum", post=lambda q, v: {})


class ProfileIsolation(unittest.TestCase):
    def setUp(self):
        from helpers import ROOT
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.scope = {}
        self.secret = mock.Mock(side_effect=lambda name, default=None: self.scope.get(name, default))
        secret_module = types.ModuleType("agent.secret_scope")
        secret_module.get_secret = self.secret
        self.home = Path(self.tmp.name) / "active-profile"
        home_module = types.ModuleType("hermes_constants")
        home_module.get_hermes_home = lambda: self.home
        modules = {"agent": types.ModuleType("agent"), "agent.secret_scope": secret_module,
                   "hermes_constants": home_module}
        patcher = mock.patch.dict(sys.modules, modules)
        patcher.start()
        self.addCleanup(patcher.stop)
        for name in ("iris_store", "iris_watchlist"):
            spec = importlib.util.spec_from_file_location(f"scoped_{name}", ROOT / "plugins" / "iris" / f"{name}.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            setattr(self, name, module)

    def test_missing_scoped_credentials_cannot_borrow_process_values(self):
        other_profile = {"SHOPIFY_STORE": "other.myshopify.com", "SHOPIFY_ADMIN_TOKEN": "other-token",
                         "SHOPIFY_CLIENT_ID": "other-id", "SHOPIFY_CLIENT_SECRET": "other-secret"}
        with mock.patch.dict(os.environ, other_profile):
            with self.assertRaises(self.iris_store.StoreError):
                self.iris_store._store()
            with self.assertRaises(self.iris_store.StoreError):
                self.iris_store._token("active.myshopify.com")
            self.scope.update({name: "" for name in other_profile})
            with self.assertRaises(self.iris_store.StoreError):
                self.iris_store._store()
            with self.assertRaises(self.iris_store.StoreError):
                self.iris_store._token("active.myshopify.com")

    def test_store_token_and_api_version_follow_each_request_scope(self):
        response = mock.MagicMock()
        response.__enter__.return_value.read.return_value = b'{"data": {"shop": {"name": "Scoped"}}}'
        with mock.patch.object(self.iris_store.urllib.request, "urlopen", return_value=response) as fetch:
            for name, version in (("first", "2026-07"), ("second", "2026-10")):
                self.scope.update({"SHOPIFY_STORE": f"{name}.myshopify.com", "SHOPIFY_ADMIN_TOKEN": name,
                                   "SHOPIFY_API_VERSION": version})
                self.iris_store._graphql("query { shop { name } }", {})
                request = fetch.call_args.args[0]
                self.assertEqual(request.full_url, f"https://{name}.myshopify.com/admin/api/{version}/graphql.json")
                self.assertEqual(request.get_header("X-shopify-access-token"), name)

    def test_data_and_token_cache_use_context_home_over_process_home(self):
        with mock.patch.dict(os.environ, {"HERMES_HOME": "other-profile", "IRIS_DATA_DIR": "other-data"}):
            self.assertEqual(self.iris_watchlist.default_path(), self.home / "iris" / "iris.db")
            self.assertEqual(self.iris_store._cache_path("active.myshopify.com"),
                             self.home / "iris" / ".shopify-token-active.myshopify.com.json")

    def test_data_override_is_profile_scoped(self):
        scoped_data = Path(self.tmp.name) / "custom-data"
        self.scope["IRIS_DATA_DIR"] = str(scoped_data)
        with mock.patch.dict(os.environ, {"IRIS_DATA_DIR": "other-data"}):
            self.assertEqual(self.iris_watchlist.default_path(), scoped_data / "iris.db")
            self.assertEqual(self.iris_store._cache_path("active.myshopify.com"),
                             scoped_data / ".shopify-token-active.myshopify.com.json")

    def test_unscoped_gateway_error_is_not_replaced_with_process_values(self):
        self.secret.side_effect = RuntimeError("No profile scope installed")
        with mock.patch.dict(os.environ, {"SHOPIFY_STORE": "other.myshopify.com", "IRIS_DATA_DIR": "other-data"}):
            with self.assertRaisesRegex(RuntimeError, "No profile scope"):
                self.iris_store._store()
            with self.assertRaisesRegex(RuntimeError, "No profile scope"):
                self.iris_watchlist.default_path()

    def test_standalone_native_resolver_can_read_process_environment(self):
        self.secret.side_effect = os.environ.get
        with mock.patch.dict(os.environ, {"SHOPIFY_STORE": "standalone.myshopify.com",
                                          "SHOPIFY_ADMIN_TOKEN": "standalone-token"}):
            self.assertEqual(self.iris_store._store(), "standalone.myshopify.com")
            self.assertEqual(self.iris_store._token("standalone.myshopify.com"), "standalone-token")


class Doctor(unittest.TestCase):
    def setUp(self):
        from helpers import ROOT
        spec = importlib.util.spec_from_file_location("iris_doctor", ROOT / "tools" / "iris_doctor.py")
        self.doctor = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.doctor)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        for rel in ("SOUL.md", "config.yaml", "plugins/iris/__init__.py", "scripts/iris_daily_check.py",
                    "scripts/iris_weekly_data.py", "skills/market-watch/SKILL.md"):
            path = self.home / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()

    def run_doctor(self, env_text):
        (self.home / ".env").write_text(env_text, encoding="utf-8")
        output = io.StringIO()
        with mock.patch.object(sys, "argv", ["iris_doctor", "--profile-home", str(self.home)]), redirect_stdout(output):
            result = self.doctor.main()
        return result, output.getvalue()

    @unittest.skipUnless(importlib.util.find_spec("dotenv"), "Hermes' python-dotenv is needed for parsing")
    def test_dotenv_quoted_profile_values_are_ready(self):
        result, output = self.run_doctor("TELEGRAM_BOT_TOKEN='bot-token'\nTELEGRAM_ALLOWED_USERS='123'\n"
                                         "SHOPIFY_STORE='active.myshopify.com' # owner store\n"
                                         "SHOPIFY_CLIENT_ID='app-id'\nSHOPIFY_CLIENT_SECRET='app-secret'\n")
        self.assertEqual(result, 0, output)
        self.assertIn("Ready.", output)

    @unittest.skipUnless(importlib.util.find_spec("dotenv"), "Hermes' python-dotenv is needed for parsing")
    def test_dotenv_empty_quotes_and_bare_keys_are_missing(self):
        result, output = self.run_doctor("TELEGRAM_BOT_TOKEN=''\nTELEGRAM_ALLOWED_USERS=\"\"\n"
                                         "SHOPIFY_STORE\nSHOPIFY_ADMIN_TOKEN=''\n"
                                         "SHOPIFY_CLIENT_ID='app-id'\nSHOPIFY_CLIENT_SECRET=''\n")
        self.assertEqual(result, 1)
        for label in ("Telegram bot token", "only the owner can talk to Iris", "store address", "store credentials"):
            self.assertIn("MISSING " + label, output)

    @unittest.skipUnless(importlib.util.find_spec("dotenv"), "Hermes' python-dotenv is needed for parsing")
    def test_dotenv_keeps_quoted_hash_characters(self):
        path = self.home / ".env"
        path.write_text("SHOPIFY_CLIENT_SECRET='secret#value' # comment\n", encoding="utf-8")
        self.assertEqual(self.doctor.read_env(path)["SHOPIFY_CLIENT_SECRET"], "secret#value")

    def test_missing_dotenv_reports_dependency_without_false_readiness(self):
        with mock.patch.dict(sys.modules, {"dotenv": None}):
            result, output = self.run_doctor("TELEGRAM_BOT_TOKEN='bot-token'\n")
        self.assertEqual(result, 1)
        self.assertIn("run the doctor with Hermes' Python", output)
        self.assertIn("Not ready yet", output)


if __name__ == "__main__":
    unittest.main()
