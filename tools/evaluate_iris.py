#!/usr/bin/env python3
"""Operator-only business cases: run native Hermes sessions and capture their evidence.

This is not an Iris tool. Uses the profile's model and Telegram toolsets, with no
Telegram delivery. Keep raw reports private: tool results can contain owner data.
"""
import argparse
import hashlib
import json
import os
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
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile-home", type=Path, required=True)
    ap.add_argument("--hermes", default="hermes")
    ap.add_argument("--profile", default="iris")
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--cases", nargs="*", help="Case IDs; omit to run all")
    args = ap.parse_args()
    import yaml  # available in Hermes' Python; no evaluation framework dependency
    cfg = yaml.safe_load((args.profile_home / "config.yaml").read_text())
    toolsets = cfg["platform_toolsets"]["telegram"]
    chosen = [c for c in CASES if not args.cases or c["id"] in args.cases]
    if not chosen or (args.cases and set(args.cases) - {c["id"] for c in CASES}):
        ap.error("Unknown case ID")
    os.umask(0o077)
    args.output.mkdir(parents=True, exist_ok=False, mode=0o700)
    manifest = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "transport": "Hermes native oneshot; Telegram toolsets, no Telegram delivery",
        "model": cfg.get("model", {}).get("default"),
        "toolsets": toolsets,
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
        run = subprocess.run([args.hermes, "-p", args.profile, "-t", ",".join(toolsets),
                              "--usage-file", str(usage), "-z", case["prompt"]],
                             cwd=args.profile_home, capture_output=True, text=True, timeout=360)
        entry = {**case, "response": run.stdout.strip(), "exit_code": run.returncode,
                 "stderr": run.stderr.strip(), "seconds": round(time.monotonic() - started, 2)}
        entry["usage"] = json.loads(usage.read_text()) if usage.exists() else {}
        sid = entry["usage"].get("session_id")
        if sid:
            with sqlite3.connect("file:" + str(args.profile_home / "state.db") + "?mode=ro", uri=True) as db:
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
