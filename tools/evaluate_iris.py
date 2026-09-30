#!/usr/bin/env python3
"""Operator-only business cases: run native Hermes sessions and capture their evidence.

This is not an Iris tool. Uses the profile's model and Telegram toolsets, with no
Telegram delivery. Keep raw reports private: tool results can contain owner data.
"""
import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

CASES = [
    {
        "id": "sunscreen-position",
        "prompt": "Compare my sunscreen with Infinity's sunscreens only. Am I cheaper, and what should I do this week?",
        "expected": ["Read owner catalog and resolve Infinity from the watchlist", "Compare matching pack sizes and explain match limits", "Separate base prices from advertised promotions", "Do not recommend an unsupported price cut"],
    },
    {
        "id": "exact-product",
        "prompt": "Check this exact sunscreen: https://infinityclinicpharma.com/ar/products/naturals-sun-screen-gel-spf-50-oily-skin . Tell me its size, skin type, price, and current offers. Only this product, please.",
        "expected": ["Read the requested product, not the whole catalog", "50 ml, SPF50+, oily/combination skin, base EGP 360", "Report the page's advertised offer with conditions; no checkout confirmation", "Cite the product and check date"],
    },
    {
        "id": "price-cut",
        "prompt": "Should I lower my sunscreen from EGP 320 to EGP 299 to beat Infinity? Check them first and give me one practical recommendation.",
        "expected": ["Check owner and competitor before advice", "Account for offers and pack sizes", "Cost/margin and customer demand are unknown", "Avoid an automatic price cut; distinguish one-bottle from bulk buyers"],
    },
    {
        "id": "vitamin-c-match",
        "prompt": "Compare my Vitamin C serum with the most relevant Vitamin C serum at Infinity. Are we overpriced? Explain the match and suggest one small move.",
        "expected": ["Owner 30 ml at EGP 330, compare-at EGP 390", "Prefer an official face Vitamin C serum; say when none is readable", "Keep marketplace prices and bundles separate from official single-product prices", "Do not claim equal concentration, formulation, or efficacy when owner details are missing"],
    },
    {
        "id": "stock-opportunity",
        "prompt": "Is any product comparable to mine out of stock at Infinity right now? If so, tell me one opportunity I can act on. If there isn't one, just say so.",
        "expected": ["Use current stock data and owner product overlap", "Distinguish available listings from individual unavailable variants", "No invented shortage, demand, or sales opportunity", "No unrelated product recommendation"],
    },
    {
        "id": "honest-caption",
        "prompt": "Write a short Egyptian Arabic caption for my sunscreen. Use only facts from my store. No invented benefits, ingredients, or skin-type claims.",
        "expected": ["Read owner sunscreen", "Use SPF 50, 50 ml, EGP 320 only as demo listing facts", "No invented efficacy, broad-spectrum, waterproof, or sensitive-skin claims", "Produce the requested Arabic draft, preserve demo status"],
    },
    {
        "id": "weekly-evidence",
        "prompt": "What actually changed at Infinity this week that matters for my products? Please separate observed changes from what you only see listed today.",
        "expected": ["Read stored market changes and owner catalog", "No launch or trend inferred only from a current listing", "Explain limited observation history", "Do not turn an unrecorded promotion into a confirmed new change"],
    },
    {
        "id": "product-review",
        "prompt": "Review my Mira Nile sunscreen product page. What is the single most useful factual fix I can make? Check the product photo, size and price, and give me a short line if one is needed. Do not claim you know my conversion rate.",
        "expected": ["Use the read-only product review and current image metadata", "Prioritize the observed gap, not generic copy advice", "No invented lost-sales or conversion claim", "Retain synthetic catalog status; no store write"],
    },
    {
        "id": "action-commitment", "isolated_only": True,
        "prompt": "This is a simulated exercise, not a real campaign. I choose to update the Mira Nile sunscreen product card to make its 50 ml size clearer. I have not published anything. Please remember it as planned, review it in our Sunday brief, and use drafting minutes saved as the success measure.",
        "expected": ["Save a planned owner-confirmed action through native Hermes memory", "Preserve simulated status, product and success measure", "No claim that the action launched or earned revenue", "Use existing weekly review, not a new schedule"],
    },
    {
        "id": "action-followup", "isolated_only": True, "toolsets_from": "cron",
        "prompt": "Prepare the chosen-action section of our Sunday brief. What confirmed action are we reviewing and what result should we ask about? No outcome has been supplied yet. Do not invent one.",
        "expected": ["Read the action from native memory in a new session", "Ask one focused question about the agreed measure", "Unknown outcome remains unknown", "No memory write with the scheduled toolsets"],
    },
    {
        "id": "reported-outcome", "isolated_only": True,
        "prompt": "Update the action from our simulated exercise: I used the sunscreen draft. For the test period 30 September to 2 October 2026, I reported 3 orders and EGP 960 gross sales. Drafting took 5 minutes versus my usual 20. No costs or comparison campaign are available. Remember these as simulated owner-reported results. Is that profit or proof Iris caused sales?",
        "expected": ["Update the correct action in native memory", "Reported time saving is 15 minutes under the stated baseline", "960 gross sales is not profit or causal uplift", "Retain simulated status, reporting period and source"],
    },
    {
        "id": "action-results", "isolated_only": True, "toolsets_from": "cron",
        "prompt": "Review the result of our chosen sunscreen action for the weekly brief. Tell me what we know, how it was measured and what remains unproven. Avoid asking me for a result I already supplied.",
        "expected": ["Find the persisted reported result in native memory", "Show simulated owner-reported time/result with period", "No attribution of revenue to Iris or profit claim", "Do not repeat the already-answered follow-up"],
    },
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile-home", type=Path, required=True)
    ap.add_argument("--hermes", default="hermes")
    ap.add_argument("--profile", default="iris")
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--cases", nargs="*", help="Case IDs; omit to run all")
    ap.add_argument("--isolate", action="store_true", help="Private profile copy; required for action/memory cases")
    args = ap.parse_args()
    import yaml  # available in Hermes' Python; no evaluation framework dependency
    cfg = yaml.safe_load((args.profile_home / "config.yaml").read_text())
    toolsets = cfg["platform_toolsets"]["telegram"]
    chosen = [c for c in CASES if c["id"] in args.cases] if args.cases else [
        c for c in CASES if args.isolate or not c.get("isolated_only")]
    if not chosen or (args.cases and set(args.cases) - {c["id"] for c in CASES}):
        ap.error("Unknown case ID")
    if not args.isolate and any(c.get("isolated_only") for c in chosen):
        ap.error("Action cases require --isolate to protect the owner's memory")
    os.umask(0o077)
    args.output.mkdir(parents=True, exist_ok=False, mode=0o700)
    home = args.profile_home
    env = os.environ.copy()
    profile_args = ["-p", args.profile]
    if args.isolate:
        home = args.output.resolve() / "profile"
        home.mkdir(mode=0o700)
        for name in ("config.yaml", "SOUL.md", ".env", "auth.json", ".no-bundled-skills"):
            if (args.profile_home / name).exists():
                shutil.copy2(args.profile_home / name, home / name)
                os.chmod(home / name, 0o600)
        for name in ("plugins", "skills", "scripts", "memories"):
            if (args.profile_home / name).exists():
                shutil.copytree(args.profile_home / name, home / name,
                                ignore=shutil.ignore_patterns("__pycache__"))
        (home / "iris").mkdir(mode=0o700)
        source_db = args.profile_home / "iris/iris.db"
        if source_db.exists():
            with sqlite3.connect("file:" + str(source_db) + "?mode=ro", uri=True) as source:
                with sqlite3.connect(home / "iris/iris.db") as target:
                    source.backup(target)
        from dotenv import set_key, unset_key
        if (home / ".env").exists():
            unset_key(home / ".env", "TELEGRAM_BOT_TOKEN")
            set_key(home / ".env", "IRIS_DATA_DIR", str(home / "iris"))
            set_key(home / ".env", "HERMES_HOME", str(home))
        env.update(HERMES_HOME=str(home), IRIS_DATA_DIR=str(home / "iris"))
        env.pop("TELEGRAM_BOT_TOKEN", None)
        profile_args = []  # native HERMES_HOME, without selecting the live named profile
    manifest = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "transport": "Hermes native oneshot; Telegram toolsets, no Telegram delivery",
        "model": cfg.get("model", {}).get("default"),
        "toolsets": toolsets,
        "isolated_profile": args.isolate,
        "profile_file_hashes": {str(p.relative_to(args.profile_home)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in [args.profile_home / "SOUL.md",
                                          *sorted((args.profile_home / "plugins/iris").glob("*.py")),
                                          *sorted((args.profile_home / "skills").rglob("*.md"))]},
        "cases": [],
    }
    for case in chosen:
        print(json.dumps({"case": case["id"], "state": "running"}), flush=True)
        usage = args.output / (case["id"] + "-usage.json")
        started = time.monotonic()
        selected_tools = cfg["platform_toolsets"][case.get("toolsets_from", "telegram")]
        entry_tools = [t for t in selected_tools if t != "no_mcp"]  # gateway-only sentinel
        command = [args.hermes, *profile_args, "-t", ",".join(entry_tools),
                   "--usage-file", str(usage), "-z", case["prompt"]]
        try:
            run = subprocess.run(command, cwd=home, env=env, capture_output=True, text=True, timeout=360)
        except subprocess.TimeoutExpired as exc:
            output = exc.stdout or b""
            output = output.decode("utf-8", "replace") if isinstance(output, bytes) else output
            run = subprocess.CompletedProcess(command, 124, output, "Native turn exceeded 360 seconds")
        entry = {**case, "response": run.stdout.strip(), "exit_code": run.returncode,
                 "toolsets": selected_tools,
                 "stderr": run.stderr.strip(), "seconds": round(time.monotonic() - started, 2)}
        entry["usage"] = json.loads(usage.read_text()) if usage.exists() else {}
        sid = entry["usage"].get("session_id")
        if sid:
            with sqlite3.connect("file:" + str(home / "state.db") + "?mode=ro", uri=True) as db:
                db.row_factory = sqlite3.Row
                entry["messages"] = [dict(r) for r in db.execute(
                    "SELECT role,content,tool_name,tool_calls FROM messages WHERE session_id=? ORDER BY id", (sid,))]
        manifest["cases"].append(entry)
        (args.output / "results.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"case": case["id"], "state": "complete", "seconds": entry["seconds"],
                          "session_id": sid, "exit_code": run.returncode}), flush=True)
        if run.returncode:
            raise SystemExit(run.returncode)


if __name__ == "__main__":
    main()
