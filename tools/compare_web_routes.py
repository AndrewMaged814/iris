"""Operator-only matched retrieval check through native Hermes public-web tools.

Uses an empty private profile, anonymous endpoints and a single-provider ring. No owner
credentials, model calls, store state or delivery. Native cache/rescue are disabled for
attribution; this does not bypass an upstream cache or prove page facts are fresh.
Run each provider in a separate process with Hermes' Python and its pinned checkout.
"""
import argparse
import asyncio
import hashlib
import io
import json
import logging
import os
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hermes-root", type=Path, required=True)
    parser.add_argument("--provider", choices=("firecrawl", "keenable", "exa", "parallel"), required=True)
    parser.add_argument("--phase", choices=("search", "extract"), required=True)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("Use a new output path; preserve earlier evidence")
    os.umask(0o077)
    spec_bytes = args.spec.read_bytes()
    spec = json.loads(spec_bytes)
    calls = spec["queries" if args.phase == "search" else "pages"]
    sys.path.insert(0, str(args.hermes_root.expanduser().resolve()))
    import yaml
    with tempfile.TemporaryDirectory(prefix="iris-route-check-") as temporary:
        os.environ["HERMES_HOME"] = temporary
        tiers = {name: "free" if name == args.provider else "paid"
                 for name in ("firecrawl", "keenable", "exa", "parallel", "tavily")}
        Path(temporary, "config.yaml").write_text(yaml.safe_dump({
            "web": {"search_backend": args.provider, "extract_backend": args.provider,
                    "provider_tier": tiers, "keyless_fallback": False,
                    "keyless_rescue": False, "cache_enabled": False},
            "plugins": {"enabled": []}}), encoding="utf-8")
        from tools.web_tools import web_search_tool, web_extract_tool
        from plugins.web.keyless_mcp import _ring_order
        ring = _ring_order(args.provider)
        if ring != [args.provider]:
            raise RuntimeError("Single-provider attribution failed: " + repr(ring))
        report = {"provider_requested": args.provider, "phase": args.phase,
                  "ring_order": ring, "native_cache_enabled": False,
                  "native_rescue_enabled": False, "owner_profile_used": False,
                  "source_freshness": "unknown", "spec_sha256": hashlib.sha256(spec_bytes).hexdigest(),
                  "observations": []}
        args.out.parent.mkdir(parents=True, exist_ok=True)
        for call in calls:
            logs = io.StringIO()
            handler = logging.StreamHandler(logs)
            root_logger = logging.getLogger()
            root_logger.addHandler(handler)
            root_logger.setLevel(logging.INFO)
            started = time.monotonic()
            observation = {**call, "requested_at": datetime.now(timezone.utc).isoformat()}
            try:
                raw = (web_search_tool(call["query"], limit=5) if args.phase == "search"
                       else asyncio.run(web_extract_tool([call["url"]], char_limit=20000)))
                observation["result"] = json.loads(raw)
                observation["result_sha256"] = hashlib.sha256(raw.encode()).hexdigest()
            except Exception as exc:
                observation["exception"] = str(exc)[:1500]
            finally:
                root_logger.removeHandler(handler)
            observation["seconds"] = round(time.monotonic() - started, 3)
            observation["returned_at"] = datetime.now(timezone.utc).isoformat()
            observation["native_log"] = logs.getvalue()
            report["observations"].append(observation)
            args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps({"provider": args.provider, "phase": args.phase,
                              "id": call["id"], "seconds": observation["seconds"]}), flush=True)


if __name__ == "__main__":
    main()
