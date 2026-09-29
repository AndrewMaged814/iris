#!/usr/bin/env python3
"""Checks an installed Iris profile on the Hermes host.

    python3 tools/iris_doctor.py --profile-home ~/.hermes/profiles/iris [--live]

Without --live it checks files and settings only. With --live it also reads the owner's store
and each watched store once. It prints what's ready and what's missing, in plain words.
"""
import argparse
import json
import os
import sys
from pathlib import Path


def check(label, ok, fix=""):
    print(("  ok    " if ok else "  MISSING ") + label + ("" if ok or not fix else f"  → {fix}"))
    return ok


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
        for line in (home / ".env").read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.split("#", 1)[0].strip()
    print("Settings")
    good &= check("Telegram bot token", bool(env.get("TELEGRAM_BOT_TOKEN")), "set TELEGRAM_BOT_TOKEN in .env")
    good &= check("only the owner can talk to Iris", bool(env.get("TELEGRAM_ALLOWED_USERS")), "set TELEGRAM_ALLOWED_USERS")
    good &= check("store address", env.get("SHOPIFY_STORE", "").endswith(".myshopify.com"), "set SHOPIFY_STORE")
    good &= check("store credentials", bool(env.get("SHOPIFY_ADMIN_TOKEN") or
                                             (env.get("SHOPIFY_CLIENT_ID") and env.get("SHOPIFY_CLIENT_SECRET"))),
                  "set the Shopify app credentials")
    print("Hermes pieces Iris relies on")
    try:
        import tools.url_safety  # noqa: F401
        check("Hermes safe web client importable", True)
    except ImportError:
        check("Hermes safe web client importable", False,
              "run the doctor with Hermes' Python; Iris falls back to a basic address check without it")
    if a.live:
        os.environ.update({k: v for k, v in env.items() if k.startswith("SHOPIFY_")})
        os.environ.setdefault("IRIS_DATA_DIR", str(home / "iris"))
        sys.path.insert(0, str(home / "plugins" / "iris"))
        import iris_feeds
        import iris_store
        from iris_watchlist import Watchlist
        print("Live")
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
