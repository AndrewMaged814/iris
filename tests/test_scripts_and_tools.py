import io
import importlib.util
import json
import os
import sqlite3
import sys
import tempfile
import types
import unittest
from contextlib import closing, redirect_stdout
from pathlib import Path
from unittest import mock

from helpers import FakeWeb, fixture
import iris_feeds as feeds


def shop(products, currency="EGP"):
    return '<script type="application/ld+json">' + json.dumps([
        {"@type": "Product", "name": p["title"], "sku": str(p["id"]), "category": p["product_type"],
         "offers": {"price": p["variants"][0]["price"], "priceCurrency": currency,
                    "priceSpecification": {"price": p["variants"][0].get("compare_at_price"), "priceType": "ListPrice"},
                    "availability": "https://schema.org/" + ("InStock" if p["variants"][0]["available"] else "OutOfStock")}}
        for p in products]) + '</script>'


def item(i, price="100.00", compare=None, available=True, title=None):
    return {"id": i, "handle": f"p{i}", "title": title or f"Serum {i}", "product_type": "Serum",
            "variants": [{"price": price, "compare_at_price": compare, "available": available}]}


class DailyCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["IRIS_DATA_DIR"] = self.tmp.name
        import _iris_paths
        self.home = Path(self.tmp.name)
        self.profile = mock.patch.object(_iris_paths, "PROFILE_HOME", self.home)
        self.profile.start()

    def tearDown(self):
        self.profile.stop()
        self.tmp.cleanup()
        os.environ.pop("IRIS_DATA_DIR", None)

    def native_execution(self, status="running", delivery=None, execution_id="run-1"):
        cron = self.home / "cron"
        cron.mkdir(exist_ok=True)
        (cron / "jobs.json").write_text(json.dumps({"jobs": [
            {"id": "daily", "script": "iris_daily_check.py", "no_agent": False}]}))
        with closing(sqlite3.connect(cron / "executions.db")) as db, db:
            db.execute("CREATE TABLE IF NOT EXISTS executions "
                       "(id TEXT PRIMARY KEY,job_id TEXT,pid INTEGER,status TEXT,delivery_outcome TEXT)")
            db.execute("INSERT OR REPLACE INTO executions VALUES (?,?,?,?,?)",
                       (execution_id, "daily", os.getppid(), status, delivery))

    def queue_delivery(self, status, tombstone=False):
        with closing(sqlite3.connect(self.home / "cron/deliveries.db")) as db, db:
            if tombstone:
                db.execute("CREATE TABLE delivery_tombstones (execution_id TEXT, terminal_status TEXT)")
                db.execute("INSERT INTO delivery_tombstones VALUES ('run-1',?)", (status,))
            else:
                db.execute("CREATE TABLE deliveries (execution_id TEXT, status TEXT)")
                db.execute("INSERT INTO deliveries VALUES ('run-1',?)", (status,))

    def web(self, products):
        return FakeWeb({"https://glow.example/products/p1": (200, shop(products))})

    def add_store(self):
        import iris_watchlist
        wl = iris_watchlist.Watchlist()
        s = wl.add("Glow Lab", "https://glow.example/products/p1", kind="shopify", focus=["serum"])
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
        self.native_execution()
        first = daily.run(get=self.web([item(1, price="80.00", compare="100.00")]))
        self.assertEqual([s["kind"] for s in first["urgent"]], ["sale_started"])
        self.native_execution("completed", "delivered")
        again = daily.run(get=self.web([item(1, price="80.00", compare="100.00")]))
        self.assertEqual(again["urgent"], [])        # already reported, nothing new

    def test_missing_price_is_saved_without_a_false_sale_ended_signal(self):
        import iris_daily_check as daily
        from iris_watchlist import Watchlist
        store = self.add_store()
        daily.run(get=self.web([item(1, price="80.00", compare="100.00")]))
        report = daily.run(get=self.web([item(1, price=None)]))
        self.assertEqual(report["other_changes_today"], 0)
        with closing(Watchlist()) as watch:
            self.assertIsNone(watch.last_good_snapshot(store["id"])[0]["price"])
            self.assertEqual(watch.signals(), [])

    def test_currency_switch_does_not_alert_a_sale_but_preserves_stock_signal(self):
        import iris_daily_check as daily
        from iris_watchlist import Watchlist
        self.add_store()
        daily.run(get=self.web([item(1)]))
        changed = FakeWeb({"https://glow.example/products/p1":
                           (200, shop([item(1, "10.00", "20.00", available=False)], currency="USD"))})
        report = daily.run(get=changed)
        self.assertEqual([signal["kind"] for signal in report["urgent"]], ["out_of_stock"])
        self.assertEqual(report["other_changes_today"], 0)
        with closing(Watchlist()) as watch:
            self.assertEqual([signal["kind"] for signal in watch.signals()], ["out_of_stock"])

    def test_delivery_proof_acknowledges_only_that_runs_facts(self):
        import iris_daily_check as daily
        self.add_store()
        daily.run(get=self.web([item(1)]))
        self.native_execution()
        first = daily.run(get=self.web([item(1, price="80.00", compare="100.00")]))
        self.native_execution("completed", "delivered")
        next_report = daily.run(get=self.web([item(1, price="80.00", compare="100.00", available=False)]))
        self.assertEqual([s["kind"] for s in next_report["urgent"]], ["out_of_stock"])
        self.assertNotEqual(next_report["urgent"][0]["id"], first["urgent"][0]["id"])

    def test_failed_model_with_delivered_error_ping_retries_business_alert(self):
        import iris_daily_check as daily
        self.add_store()
        daily.run(get=self.web([item(1)]))
        self.native_execution()
        first = daily.run(get=self.web([item(1, available=False)]))
        self.native_execution("failed", "delivered")
        self.assertEqual(daily.run(get=self.web([item(1, available=False)]))["urgent"], first["urgent"])

    def test_failed_transport_retries_business_alert(self):
        import iris_daily_check as daily
        self.add_store()
        daily.run(get=self.web([item(1)]))
        self.native_execution()
        first = daily.run(get=self.web([item(1, available=False)]))
        self.native_execution("completed", "failed")
        self.assertEqual(daily.run(get=self.web([item(1, available=False)]))["urgent"], first["urgent"])

    def test_active_or_uncertain_send_is_held_without_consuming_facts(self):
        import iris_daily_check as daily
        from iris_watchlist import Watchlist
        self.add_store()
        daily.run(get=self.web([item(1)]))
        self.native_execution()
        first = daily.run(get=self.web([item(1, available=False)]))
        self.assertEqual(daily.run(get=self.web([item(1, available=False)]))["urgent"], [])
        self.native_execution("unknown", "unknown")
        self.assertEqual(daily.run(get=self.web([item(1, available=False)]))["urgent"], [])
        wl = Watchlist()
        self.assertEqual(wl.signals(days=None, unreported_only=True)[0]["id"], first["urgent"][0]["id"])
        wl.close()

    def test_deferred_delivery_waits_for_native_queue_proof(self):
        import iris_daily_check as daily
        from iris_watchlist import Watchlist
        self.add_store()
        daily.run(get=self.web([item(1)]))
        self.native_execution()
        daily.run(get=self.web([item(1, available=False)]))
        self.native_execution("completed", "queued")
        self.queue_delivery("pending")
        self.assertEqual(daily.run(get=self.web([item(1, available=False)]))["urgent"], [])
        with closing(sqlite3.connect(self.home / "cron/deliveries.db")) as db, db:
            db.execute("UPDATE deliveries SET status='delivered'")
        self.assertEqual(daily.run(get=self.web([item(1, available=False)]))["urgent"], [])
        wl = Watchlist()
        self.assertEqual(wl.signals(days=None, unreported_only=True), [])
        wl.close()

    def test_pruned_queue_delivery_tombstone_is_valid_proof(self):
        import iris_daily_check as daily
        from iris_watchlist import Watchlist
        self.add_store()
        daily.run(get=self.web([item(1)]))
        self.native_execution()
        daily.run(get=self.web([item(1, available=False)]))
        self.native_execution("completed", "queued")
        self.queue_delivery("delivered", tombstone=True)
        daily.run(get=self.web([item(1, available=False)]))
        wl = Watchlist()
        self.assertEqual(wl.signals(days=None, unreported_only=True), [])
        wl.close()

    def test_ambiguous_native_worker_is_not_correlated(self):
        import iris_delivery
        self.native_execution()
        self.native_execution(execution_id="run-2")
        self.assertIsNone(iris_delivery.current_execution(self.home))

    def test_unreported_facts_do_not_expire_during_an_outage(self):
        import iris_daily_check as daily
        from iris_watchlist import Watchlist
        self.add_store()
        daily.run(get=self.web([item(1)]))
        first = daily.run(get=self.web([item(1, available=False)]))
        wl = Watchlist()
        wl.db.execute("UPDATE signals SET created_at='2020-01-01T00:00:00Z'")
        wl.db.commit()
        wl.close()
        retry = daily.run(get=self.web([item(1, available=False)]))
        self.assertEqual(retry["urgent"][0]["id"], first["urgent"][0]["id"])
        self.assertEqual(retry["urgent"][0]["created_at"], "2020-01-01T00:00:00Z")

    def test_failed_generation_does_not_consume_alert(self):
        import iris_daily_check as daily
        self.add_store()
        daily.run(get=self.web([item(1)]))
        first = daily.run(get=self.web([item(1, price="80.00", compare="100.00")]))
        # No successful Hermes delivery occurred after the first script result.
        retry = daily.run(get=self.web([item(1, price="80.00", compare="100.00")]))
        self.assertEqual([s["id"] for s in retry["urgent"]], [s["id"] for s in first["urgent"]])

    def test_failed_generation_does_not_consume_store_problem(self):
        import iris_daily_check as daily
        self.add_store()
        down = FakeWeb({"https://glow.example/": (403, "no")})
        reports = [daily.run(get=down) for _ in range(4)]
        self.assertEqual(len(reports[2]["unreachable"]), 1)
        self.assertEqual(len(reports[3]["unreachable"]), 1)

    def test_three_failed_checks_report_once(self):
        import iris_daily_check as daily
        self.add_store()
        down = FakeWeb({"https://glow.example/": (403, "no")})
        self.native_execution()
        reports = [daily.run(get=down) for _ in range(3)]
        self.native_execution("completed", "delivered")
        reports.append(daily.run(get=down))
        self.assertEqual([len(r["unreachable"]) for r in reports], [0, 0, 1, 0])

    def test_recovered_store_cancels_stale_failure_and_new_episode_alerts(self):
        import iris_daily_check as daily
        self.add_store()
        down = FakeWeb({"https://glow.example/": (403, "no")})
        for _ in range(3):
            daily.run(get=down)
        self.assertEqual(daily.run(get=self.web([item(1)]))["unreachable"], [])
        reports = [daily.run(get=down) for _ in range(3)]
        self.assertEqual([len(r["unreachable"]) for r in reports], [0, 0, 1])

    def test_weekly_data_counts_the_week(self):
        import iris_daily_check as daily
        import iris_weekly_data as weekly
        self.add_store()
        daily.run(get=self.web([item(1)]))
        daily.run(get=self.web([item(1, available=False)]))
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(weekly.main(), 0)
        data = json.loads(out.getvalue())
        self.assertEqual(data["week_counts"], {"out_of_stock": 1})
        self.assertEqual(data["checks_this_week"], 2)
        self.assertEqual(data["market_by_store"]["Glow Lab"]["Serum"]["count"], 1)
        self.assertIn("not instructions", data["note"])
        self.assertEqual(data["observation_by_store"]["Glow Lab"]["checks"], 2)
        self.assertEqual(data["observation_by_store"]["Glow Lab"]["url"], "https://glow.example/products/p1")

    def test_chat_and_weekly_share_dated_evidence(self):
        import iris_weekly_data as weekly
        from iris_watchlist import Watchlist
        wl = Watchlist()
        s = self.add_store()
        wl.save_snapshot(s["id"], {"access": "ok", "fetched_at": "2026-09-29T23:18:58Z", "products": []})
        from datetime import datetime, timezone
        from zoneinfo import ZoneInfo
        with mock.patch("iris_watchlist.datetime", wraps=datetime) as clock, \
                mock.patch("iris_watchlist.profile_timezone", return_value=ZoneInfo("Africa/Cairo")):
            clock.now.return_value = datetime(2026, 9, 30, 0, 0, tzinfo=timezone.utc)
            expected = wl.market_context(7)
            actual = weekly.collect()
        wl.close()
        coverage = actual["observation_by_store"]
        self.assertEqual(coverage, expected["observation_by_store"])
        self.assertEqual(coverage["Glow Lab"]["last_checked_local"], "2026-09-30T02:18:58+03:00")
        self.assertEqual(actual["timezone"], "Africa/Cairo")


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

    def test_registers_history_and_calculation_tools_in_one_toolset(self):
        registered = []

        class Ctx:
            def register_tool(self, **kw):
                registered.append((kw["name"], kw["toolset"], kw["schema"]["name"]))

            def register_system_prompt_section(self, id, content, **kw):
                self_identities.append((id, content))

            def register_redaction_patterns(self, patterns):
                return len(patterns)

            def register_hook(self, event, callback):
                hooks.append((event, callback))

        hooks = []
        self_identities = []
        self.plugin.register(Ctx())
        self.assertEqual(sorted(registered), sorted([(n, "iris", n) for n in
                                                     ("read_store", "watchlist", "market_changes", "market_math")]))
        self.assertEqual(hooks, [("pre_tool_call", self.plugin.browser_guard),
                                ("pre_tool_call", self.plugin.research_progress.before),
                                ("post_tool_call", self.plugin.research_progress.after)])
        self.assertEqual(self_identities, [("iris.speaker", self.plugin.speaker_context)])

    def test_calculation_tool_is_json_and_rejects_invalid_input(self):
        result = json.loads(self.plugin.market_math_tool({"operation": "compare_baskets",
            "own": {"price": 320, "quantity": 50, "unit": "ml", "currency": "EGP"},
            "rival": {"totals": [570, 285], "quantity": 120, "unit": "ml", "currency": "EGP"}}))
        self.assertEqual(result["quantity_ratio_rival_to_own"], 2.4)
        self.assertIn("error", json.loads(self.plugin.market_math_tool({"operation": "execute"})))

    def test_sender_identity_uses_id_not_a_matching_display_name(self):
        session = {"HERMES_SESSION_PLATFORM": "telegram", "HERMES_SESSION_CHAT_TYPE": "dm",
                   "HERMES_SESSION_USER_ID": "owner-id", "HERMES_SESSION_USER_NAME": "Andrew"}
        context = types.ModuleType("gateway.session_context")
        context.get_session_env = session.get
        secret = types.ModuleType("agent.secret_scope")
        secret.get_secret = lambda key, default=None: "owner-id" if key == "TELEGRAM_ALLOWED_USERS" else default
        with mock.patch.dict(sys.modules, {"gateway.session_context": context, "agent.secret_scope": secret}):
            self.assertIn("configured Iris owner", self.plugin.speaker_context({}))
            session["HERMES_SESSION_USER_ID"] = "visitor-id"
            self.assertIn("Speaker identity is unconfirmed", self.plugin.speaker_context({}))
            session["HERMES_SESSION_CHAT_TYPE"] = "group"
            self.assertIn("Multiple speakers", self.plugin.speaker_context({}))
            session["HERMES_SESSION_PLATFORM"] = "local"
            self.assertEqual(self.plugin.speaker_context({}), "")

    def test_composio_uses_native_operations_without_custom_policy(self):
        guard = self.plugin.browser_guard
        for slug in ("GOOGLESHEETS_SEARCH_SPREADSHEETS", "REDDIT_SEARCH_ACROSS_SUBREDDITS",
                     "REDDIT_POST_REDDIT_COMMENT", "GOOGLESHEETS_BATCH_UPDATE",
                     "GOOGLEDRIVE_ADD_FILE_SHARING_PREFERENCE"):
            with self.subTest(slug=slug):
                self.assertIsNone(guard("mcp__composio__COMPOSIO_MULTI_EXECUTE_TOOL",
                                        {"tools": [{"tool_slug": slug, "arguments": {}}],
                                         "sync_response_to_workbench": False}))
        self.assertIsNone(guard("mcp__composio__COMPOSIO_MANAGE_CONNECTIONS",
                                {"toolkits": [{"name": "googlesheets", "action": "rename"}]}))

    def test_browser_guard_allows_reading_public_pages_only(self):
        guard = self.plugin.browser_guard
        feeds = self.plugin.feeds
        feeds._ROBOTS.clear()
        with mock.patch.object(feeds, "_basic_guard", lambda url: None), \
             mock.patch.object(feeds, "_fetch", lambda url: (200, "User-agent: IrisBot\nDisallow: /members/")):
            self.assertIsNone(guard(tool_name="browser_navigate", args={"url": "https://shop.example/product/a"}))
            self.assertEqual(guard(tool_name="browser_navigate",
                                   args={"url": "https://shop.example/members/prices"})["action"], "block")
        for blocked in ("browser_click", "browser_type", "browser_press", "browser_console", "browser_cdp",
                        "browser_vault_fill", "browser_exec", "browser_dialog"):
            self.assertEqual(guard(tool_name=blocked, args={})["action"], "block", blocked)
        self.assertEqual(guard(tool_name="browser_navigate", args={"url": "file:///etc/passwd"})["action"], "block")
        self.assertEqual(guard(tool_name="browser_navigate", args={"url": "http://127.0.0.1:8080/"})["action"], "block")
        self.assertIsNone(guard(tool_name="browser_snapshot", args={}))
        self.assertIsNone(guard(tool_name="web_search", args={"query": "x"}))

    def test_watch_add_takes_a_baseline_and_lists_it(self):
        web = FakeWeb({"https://glow.example/products/p1": (200, shop([item(1)]))})
        with mock.patch.object(self.plugin.feeds, "http_get", web):
            out = json.loads(self.plugin.watchlist_tool({"operation": "add", "url": "https://glow.example/products/p1",
                                                         "name": "Glow Lab", "focus": ["serum"]}))
        self.assertTrue(out["added"])
        self.assertEqual(out["first_look"]["product_count"], 1)   # focus kept only the serum
        listed = json.loads(self.plugin.watchlist_tool({"operation": "list"}))
        self.assertEqual(listed["stores"][0]["products_seen"], 1)

    def test_blocked_store_is_not_added(self):
        web = FakeWeb({"https://shy.example/": (403, "no")})
        with mock.patch.object(self.plugin.feeds, "http_get", web):
            out = json.loads(self.plugin.watchlist_tool({"operation": "add", "url": "https://shy.example/products/p1", "name": "Shy"}))
        self.assertEqual(out, {"added": False, "reason": "blocked", "url": "https://shy.example/products/p1"})

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
        self.assertNotIn("page_text", out)
        self.assertFalse(out["products"][0]["on_sale"])
        self.assertFalse(out["snapshot_coverage"]["page_promotion_terms_collected"])
        self.assertFalse(out["snapshot_coverage"]["checkout_verified"])
        self.assertIn("not instructions", out["note"])

    def test_market_changes_exposes_limited_observation_history(self):
        from iris_watchlist import Watchlist
        wl = Watchlist()
        s = wl.add("Glow", "https://glow.example/products/p1")
        wl.save_snapshot(s["id"], {"access": "ok", "products": []})
        wl.save_snapshot(s["id"], {"access": "blocked", "products": []})
        wl.close()
        out = json.loads(self.plugin.market_changes_tool({"period": "week"}))
        coverage = out["observation_by_store"]["Glow"]
        self.assertEqual(coverage["checks"], 1)
        self.assertEqual(coverage["first_checked"], coverage["last_checked"])
        self.assertEqual(out["signals"], [])
        self.assertFalse(out["snapshot_coverage"]["page_promotion_terms_collected"])
        self.assertEqual(out["snapshot_coverage"]["sale_flag_basis"],
                         "structured_sale_flag_or_price_below_compare_at")

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
        for name in ("iris_watchlist",):
            spec = importlib.util.spec_from_file_location(f"scoped_{name}", ROOT / "plugins" / "iris" / f"{name}.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            setattr(self, name, module)

    def test_data_uses_context_home_over_process_home(self):
        with mock.patch.dict(os.environ, {"HERMES_HOME": "other-profile", "IRIS_DATA_DIR": "other-data"}):
            self.assertEqual(self.iris_watchlist.default_path(), self.home / "iris" / "iris.db")

    def test_data_override_is_profile_scoped(self):
        scoped_data = Path(self.tmp.name) / "custom-data"
        self.scope["IRIS_DATA_DIR"] = str(scoped_data)
        with mock.patch.dict(os.environ, {"IRIS_DATA_DIR": "other-data"}):
            self.assertEqual(self.iris_watchlist.default_path(), scoped_data / "iris.db")

    def test_unscoped_gateway_error_is_not_replaced_with_process_values(self):
        self.secret.side_effect = RuntimeError("No profile scope installed")
        with mock.patch.dict(os.environ, {"IRIS_DATA_DIR": "other-data"}):
            with self.assertRaisesRegex(RuntimeError, "No profile scope"):
                self.iris_watchlist.default_path()

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
        (self.home / "config.yaml").write_text("mcp_servers:\n  composio:\n    enabled: true\n")

    def run_doctor(self, env_text):
        (self.home / ".env").write_text(env_text, encoding="utf-8")
        output = io.StringIO()
        with mock.patch.object(sys, "argv", ["iris_doctor", "--profile-home", str(self.home)]), redirect_stdout(output):
            result = self.doctor.main()
        return result, output.getvalue()

    @unittest.skipUnless(importlib.util.find_spec("dotenv"), "Hermes' python-dotenv is needed for parsing")
    def test_dotenv_quoted_profile_values_are_ready(self):
        result, output = self.run_doctor("TELEGRAM_BOT_TOKEN='bot-token'\nTELEGRAM_ALLOWED_USERS='123'\n"
                                         "AGENT_BROWSER_ARGS='--user-agent=IrisBot/1.0'\n")
        self.assertEqual(result, 0, output)
        self.assertIn("Ready.", output)

    @unittest.skipUnless(importlib.util.find_spec("dotenv"), "Hermes' python-dotenv is needed for parsing")
    def test_public_telegram_setting_overrides_owner_allowlist(self):
        result, output = self.run_doctor("TELEGRAM_BOT_TOKEN='bot-token'\nTELEGRAM_ALLOWED_USERS='123'\n"
                                         "TELEGRAM_ALLOW_ALL_USERS=true\n"
                                         "AGENT_BROWSER_ARGS='--user-agent=IrisBot/1.0'\n")
        self.assertEqual(result, 1)
        self.assertIn("MISSING only the owner can talk to Iris", output)

    @unittest.skipUnless(importlib.util.find_spec("dotenv"), "Hermes' python-dotenv is needed for parsing")
    def test_wildcard_is_not_an_owner_allowlist(self):
        result, output = self.run_doctor("TELEGRAM_BOT_TOKEN='bot-token'\nTELEGRAM_ALLOWED_USERS='*'\n"
                                         "AGENT_BROWSER_ARGS='--user-agent=IrisBot/1.0'\n")
        self.assertEqual(result, 1)
        self.assertIn("MISSING only the owner can talk to Iris", output)

    def test_missing_reader_dependency_prevents_readiness(self):
        with mock.patch.dict(sys.modules, {"extruct": None}):
            result, output = self.run_doctor("")
        self.assertEqual(result, 1)
        self.assertIn("MISSING extruct importable", output)

    def test_browser_argument_must_be_a_user_agent_flag(self):
        result, output = self.run_doctor("AGENT_BROWSER_ARGS='--other=--user-agent=IrisBot'\n")
        self.assertEqual(result, 1)
        self.assertIn("MISSING browser user agent", output)


    @unittest.skipUnless(importlib.util.find_spec("dotenv"), "Hermes' python-dotenv is needed for parsing")
    def test_dotenv_empty_quotes_and_bare_keys_are_missing(self):
        result, output = self.run_doctor("TELEGRAM_BOT_TOKEN=''\nTELEGRAM_ALLOWED_USERS=\"\"\n"
                                         "UNUSED_SETTING\n")
        self.assertEqual(result, 1)
        for label in ("Telegram bot token", "only the owner can talk to Iris"):
            self.assertIn("MISSING " + label, output)

    @unittest.skipUnless(importlib.util.find_spec("dotenv"), "Hermes' python-dotenv is needed for parsing")
    def test_dotenv_keeps_quoted_hash_characters(self):
        path = self.home / ".env"
        path.write_text("EXAMPLE_SECRET='secret#value' # comment\n", encoding="utf-8")
        self.assertEqual(self.doctor.read_env(path)["EXAMPLE_SECRET"], "secret#value")

    def test_missing_dotenv_reports_dependency_without_false_readiness(self):
        with mock.patch.dict(sys.modules, {"dotenv": None}):
            result, output = self.run_doctor("TELEGRAM_BOT_TOKEN='bot-token'\n")
        self.assertEqual(result, 1)
        self.assertIn("run the doctor with Hermes' Python", output)
        self.assertIn("Not ready yet", output)


if __name__ == "__main__":
    unittest.main()
