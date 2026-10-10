"""Read back native Langfuse traces for evaluation sessions; no raw content."""
import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path


def trace_requests(report, variant):
    """Compare native sessions once, including every resumed turn in their Cloud roots."""
    grouped = {}
    if "cases" in report:
        calls = [(case["id"], index, turn) for case in report["cases"]
                 for index, turn in enumerate(case["turns"])]
        for case_id, index, turn in calls:
            session_id = turn["usage"]["session_id"]
            item = grouped.setdefault(session_id, {"variant": variant, "case": case_id,
                "session_id": session_id, "turn_indices": [], "native_calls": 0,
                "native_tools": 0, "expected_roots": 0})
            item["turn_indices"].append(index)
            item["expected_roots"] += 1
            count = turn["usage"].get("api_calls")
            item["native_calls"] = (item["native_calls"] + count
                if item["native_calls"] is not None and count is not None else None)
            item["native_tools"] += turn["trace_summary"]["tool_calls"]
        return list(grouped.values())
    raise ValueError("Expected a native evaluate_iris cases report")


def reconcile_observations(request, roots, rows):
    """CLI api_calls counts completions; failed attempts remain visible separately.

    Empty usage on an ERROR generation is unknown, not a free/billable completion.
    Known usage on failed attempts is retained in token totals.
    """
    generations = [row for row in rows if row.get("type") == "GENERATION"]
    failures = [row for row in generations if row.get("level") == "ERROR"]
    successes = [row for row in generations if row.get("level") != "ERROR"]
    tools = [row for row in rows if row.get("type") == "TOOL"]
    known = [row.get("usageDetails") for row in generations if row.get("usageDetails")]
    usage_complete = bool(successes) and all(row.get("usageDetails") for row in successes)
    canonical_known = sum(sum(usage.get(key, 0) for key in
        ("input", "output", "cache_read_input_tokens", "cache_creation_input_tokens")) for usage in known)
    cloud_known = sum(usage.get("total", 0) for usage in known)
    return {**request, "cloud_roots": len(roots), "cloud_calls": len(generations),
        "cloud_successful_calls": len(successes), "cloud_failed_attempts": len(failures),
        "failed_attempts_with_unknown_usage": sum(not row.get("usageDetails") for row in failures),
        "cloud_tools": len(tools), "counts_match": len(roots) == request["expected_roots"]
            and len(successes) == request["native_calls"] and len(tools) == request["native_tools"],
        "canonical_totals_match": bool(usage_complete) and all(usage.get("total") == sum(
            usage.get(key, 0) for key in ("input", "output", "cache_read_input_tokens", "cache_creation_input_tokens"))
            for usage in known),
        "cloud_known_total_tokens": cloud_known,
        "canonical_known_total_tokens": canonical_known,
        "reported_total_difference": cloud_known - canonical_known,
        "actual_charge": "unknown",
        "environments": sorted({row.get("environment") or "unknown" for row in rows}),
        "capture_modes": sorted({(row.get("metadata") or {}).get("capture_mode", "") for row in rows
                                  if row.get("name") == "Hermes turn"}),
        "trace_ids": sorted({root.trace_id for root in roots})}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile-home", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    from dotenv import dotenv_values
    from langfuse import Langfuse
    env = dotenv_values(args.profile_home / ".env")
    client = Langfuse(public_key=env["HERMES_LANGFUSE_PUBLIC_KEY"],
                      secret_key=env["HERMES_LANGFUSE_SECRET_KEY"],
                      base_url=env["HERMES_LANGFUSE_BASE_URL"])
    baseline, candidate = json.loads(args.baseline.read_text()), json.loads(args.candidate.read_text())
    requests = trace_requests(baseline, "baseline") + trace_requests(candidate, "candidate")
    now = datetime.now(timezone.utc)
    checks = []
    try:
        for request in requests:
            roots = client.api.observations.get_many(fields="core,basic,usage,metadata",
                session_id=request["session_id"], name="Hermes turn", limit=30,
                from_start_time=now-timedelta(hours=6), to_start_time=now).data
            if len(roots) >= 30:
                raise ValueError("Session reaches the root limit; complete accounting is unproved")
            observations = {}
            for trace_id in {root.trace_id for root in roots}:
                response = client.api.observations.get_many(fields="core,basic,usage,metadata",
                    trace_id=trace_id, limit=100,
                    from_start_time=now-timedelta(hours=6), to_start_time=now)
                if len(response.data) >= 100:
                    raise ValueError("Trace reaches the readback limit; complete accounting is unproved")
                observations.update({row.id: row.model_dump(mode="json", by_alias=True)
                                     for row in response.data})
            rows = list(observations.values())
            checks.append(reconcile_observations(request, roots, rows))
        result = {"checked_at": now.isoformat(), "scope": "Native main-call/tool trace readback; not actual charges",
                  "checks": checks}
        with args.output.open("x") as handle:
            json.dump(result, handle, indent=2)
        print(json.dumps({"output": str(args.output), "sessions": len(checks),
                          "all_counts_match": all(check["counts_match"] for check in checks)}))
    finally:
        client.shutdown()


if __name__ == "__main__":
    main()
