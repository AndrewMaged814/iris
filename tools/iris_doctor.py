#!/usr/bin/env python3
"""Checks an installed Iris profile on the Hermes host.

    python3 tools/iris_doctor.py --profile-home ~/.hermes/profiles/iris [--live]

Without --live it checks files and settings only. With --live it also reads the owner's store
and each watched store once. It prints what's ready and what's missing, in plain words.
"""
import argparse
import importlib
import json
import os
import sys
from pathlib import Path


def check(label, ok, fix=""):
    print(("  ok    " if ok else "  MISSING ") + label + ("" if ok or not fix else f"  → {fix}"))
    return ok


def read_env(path: Path) -> dict[str, str]:
    from dotenv import dotenv_values
    return {key: value for key, value in dotenv_values(path, interpolate=False).items() if value is not None}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile-home", required=True)
    ap.add_argument("--live", action="store_true")
    a = ap.parse_args()
    home = Path(a.profile_home).expanduser()
    good = True
    print("Files")
    for rel in ("SOUL.md", "config.yaml", "plugins/iris/__init__.py", "scripts/iris_daily_check.py",
                "scripts/iris_weekly_data.py", "skills/market-watch/SKILL.md"):
        good &= check(rel, (home / rel).exists(), "reinstall the distribution")
    env = {}
    if (home / ".env").exists():
        try:
            env = read_env(home / ".env")
        except ImportError:
            good &= check(".env parser", False, "run the doctor with Hermes' Python (includes python-dotenv)")
    print("Settings")
    good &= check("Telegram bot token", bool(env.get("TELEGRAM_BOT_TOKEN")), "set TELEGRAM_BOT_TOKEN in .env")
    good &= check("only the owner can talk to Iris", bool(env.get("TELEGRAM_ALLOWED_USERS")), "set TELEGRAM_ALLOWED_USERS")
    good &= check("store address", (env.get("SHOPIFY_STORE") or "").endswith(".myshopify.com"), "set SHOPIFY_STORE")
    good &= check("store credentials", bool(env.get("SHOPIFY_ADMIN_TOKEN") or
                                             (env.get("SHOPIFY_CLIENT_ID") and env.get("SHOPIFY_CLIENT_SECRET"))),
                  "set the Shopify app credentials")
    good &= check("competitor search (SearXNG)", bool(env.get("SEARXNG_URL")),
                  "set SEARXNG_URL in .env; see docs/SETUP.md")
    good &= check("browser user agent", any(arg.strip().startswith("--user-agent=IrisBot")
                  for arg in env.get("AGENT_BROWSER_ARGS", "").split(",")),
                  "set AGENT_BROWSER_ARGS with --user-agent=IrisBot/1.0; see docs/SETUP.md")
    print("Product reader dependencies")
    for module in ("extruct", "price_parser"):
        try:
            importlib.import_module(module)
            good &= check(module + " importable", True)
        except ImportError:
            good &= check(module + " importable", False,
                          "install extruct and price-parser with Hermes' Python")
    monitor_url, monitor_key = env.get("CHANGEDETECTION_URL"), env.get("CHANGEDETECTION_API_KEY")
    if monitor_url or monitor_key:
        good &= check("optional product monitor credentials", bool(monitor_url and monitor_key),
                      "set both CHANGEDETECTION_URL and CHANGEDETECTION_API_KEY, or leave both empty")
    print("Hermes pieces Iris relies on")
    try:
        import tools.url_safety  # noqa: F401
        check("Hermes safe web client importable", True)
    except ImportError:
        check("Hermes safe web client importable", False,
              "run the doctor with Hermes' Python; Iris falls back to a basic address check without it")
    if a.live:
        os.environ.update({k: v for k, v in env.items() if k.startswith(("SHOPIFY_", "CHANGEDETECTION_"))})
        os.environ.setdefault("IRIS_DATA_DIR", str(home / "iris"))
        sys.path.insert(0, str(home / "plugins" / "iris"))
        import iris_feeds
        import iris_store
        from iris_watchlist import Watchlist
        print("Live")
        if monitor_url and monitor_key:
            import iris_monitor
            try:
                watches = iris_monitor._call("GET", "/api/v1/watch")
                good &= check("optional product monitor reachable with key", isinstance(watches, dict),
                              "check the monitor URL and API key")
            except iris_monitor.MonitorError as exc:
                good &= check("optional product monitor reachable with key", False, str(exc))
        try:
            cat = iris_store.catalog(max_pages=1)
            check(f"own store readable ({cat['shop']}, {cat['product_count']} products)", True)
        except iris_store.StoreError as exc:
            good &= check("own store readable", False, str(exc))
        wl = Watchlist()
        for s in wl.stores():
            r = iris_feeds.read_store(s["url"], kind=s["kind"])
            good &= check(f"watched: {s['name']} ({r['access']}, {len(r['products'])} products)", r["access"] == "ok",
                          "the store may block Iris or have moved")
        wl.close()
    print("\nReady." if good else "\nNot ready yet — fix the items marked MISSING.")
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
