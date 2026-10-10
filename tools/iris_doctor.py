#!/usr/bin/env python3
"""Checks an installed Iris profile on the Hermes host.

    python3 tools/iris_doctor.py --profile-home ~/.hermes/profiles/iris [--live]

Without --live it checks files and settings only. With --live it checks native Composio discovery
and reads each watched product once. It prints what's ready and what's missing, in plain words.
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
    owner_ids = [part.strip() for part in env.get("TELEGRAM_ALLOWED_USERS", "").split(",") if part.strip()]
    public_access = env.get("TELEGRAM_ALLOW_ALL_USERS", "").strip().lower() in {"true", "1", "yes"}
    public_demo = env.get("IRIS_PUBLIC_DEMO", "").strip().lower() in {"true", "1", "yes"}
    if public_demo:
        plugin_text = (home / "plugins/iris/__init__.py").read_text() if (home / "plugins/iris/__init__.py").exists() else ""
        good &= check("public demo with an identified operator and visitor access guard",
                      public_access and len(owner_ids) == 1 and owner_ids[0] != "*"
                      and 'ctx.register_hook("pre_tool_call", demo_access_guard)' in plugin_text,
                      "verify the demo guard, one operator ID and TELEGRAM_ALLOW_ALL_USERS=true")
    else:
        good &= check("only the owner can talk to Iris",
                      len(owner_ids) == 1 and owner_ids[0] != "*" and not public_access,
                      "set one owner ID in TELEGRAM_ALLOWED_USERS and TELEGRAM_ALLOW_ALL_USERS=false")
    import yaml
    try:
        cfg = yaml.safe_load((home / "config.yaml").read_text()) or {}
    except (OSError, yaml.YAMLError):
        cfg = {}
    composio = cfg.get("mcp_servers", {}).get("composio", {})
    if public_demo:
        telegram_policy = cfg.get("platforms", {}).get("telegram", {})
        good &= check("public demo administrative commands reserved for operator",
                      telegram_policy.get("allow_admin_from") == owner_ids
                      and telegram_policy.get("user_allowed_commands") == []
                      and telegram_policy.get("group_allow_admin_from") == owner_ids
                      and telegram_policy.get("group_user_allowed_commands") == [],
                      "reserve DM and group administrative commands for the operator")
        good &= check("public demo automatic shared-memory review disabled",
                      cfg.get("auxiliary", {}).get("background_review", {}).get("enabled") is False,
                      "set auxiliary.background_review.enabled: false for the shared demo")
    good &= check("Composio enabled", composio.get("enabled") is True,
                  "authorize with Hermes mcp login composio and enable the server")
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
    print("Hermes pieces Iris relies on")
    try:
        import tools.url_safety  # noqa: F401
        check("Hermes safe web client importable", True)
    except ImportError:
        check("Hermes safe web client importable", False,
              "run the doctor with Hermes' Python; Iris falls back to a basic address check without it")
    if a.live:
        os.environ["HERMES_HOME"] = str(home.resolve())
        os.environ.setdefault("IRIS_DATA_DIR", str(home / "iris"))
        sys.path.insert(0, str(home / "plugins" / "iris"))
        import iris_feeds
        from iris_watchlist import Watchlist
        print("Live")
        try:
            from tools.mcp_tool_discovery import discover_mcp_tools
            registered = discover_mcp_tools(["composio"])
            good &= check("native Composio tools available", bool(registered),
                          "check native MCP authentication; verify catalog reads in Telegram")
        except Exception:
            good &= check("native Composio tools available", False,
                          "run Hermes mcp test composio for native diagnostics")
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
