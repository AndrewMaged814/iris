#!/usr/bin/env python3
"""Export owner-facing replies and call counts, excluding raw connected-app results."""
import json
import argparse
import hashlib
import os
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


def native_json(content):
    if not isinstance(content, str):
        return content if isinstance(content, dict) else {}
    if content.startswith("<untrusted_tool_result"):
        content = content[content.find("{"):content.rfind("}") + 1]
    try:
        value = json.loads(content)
        return value if isinstance(value, dict) else {}
    except ValueError:
        return {}


def catalog_fields(node, path="", limit=300):
    """Retain original JSON paths for bounded product facts, never credentials.

    Snapshots are private. Only explicitly selected product field names survive;
    unknown fields are omitted rather than interpreted as missing product attributes.
    """
    allowed = {"title", "description", "descriptionHtml", "productType", "price", "amount",
               "currency", "currencyCode", "inventoryQuantity", "inventory_quantity",
               "totalInventory", "availableForSale", "onlineStoreUrl", "sku", "cost",
               "selectedOptions"}
    result = []
    def walk(value, location):
        if len(result) >= limit:
            return
        if isinstance(value, dict):
            if value.get("success") is False or value.get("successful") is False or value.get("error"):
                return
            for key, item in value.items():
                child = location + "/" + key.replace("~", "~0").replace("/", "~1")
                if key in allowed and (item is None or isinstance(item, (str, int, float, bool))):
                    result.append({"path": child, "value": item[:2000] if isinstance(item, str) else item})
                    if len(result) >= limit:
                        return
                else:
                    walk(item, child)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, location + "/" + str(index))
        elif isinstance(value, str) and value.startswith(("{", "[")):
            try:
                walk(json.loads(value), location)
            except ValueError:
                pass
    walk(node, path)
    return result


def evidence_snapshot(report, case_id, report_sha256=None):
    """Freeze observed first-turn evidence privately; never fabricate fresh retrieval."""
    case = next(c for c in report["cases"] if c["id"] == case_id)
    turn = case["turns"][0]
    if turn["exit_code"]:
        raise ValueError("A failed turn is not an accepted evidence snapshot")
    pages, app_fields = {}, {}
    for message in turn.get("new_messages", []):
        data = native_json(message.get("content"))
        if message.get("tool_name") == "web_extract":
            for page in data.get("results", []):
                if not isinstance(page, dict) or page.get("error"):
                    continue
                content, url = page.get("content"), page.get("url")
                if not isinstance(content, str) or not content.strip() or not isinstance(url, str):
                    continue
                digest = hashlib.sha256(content.encode()).hexdigest()
                pages.setdefault((url, digest), {"url": url, "content": content, "sha256": digest,
                    "observed_at": message.get("timestamp"), "characters": len(content)})
        elif message.get("tool_name") == "mcp__composio__COMPOSIO_MULTI_EXECUTE_TOOL":
            fields = catalog_fields(data)
            if fields:
                digest = hashlib.sha256(json.dumps(fields, sort_keys=True).encode()).hexdigest()
                app_fields.setdefault(digest, {"fields": fields, "sha256": digest,
                    "observed_at": message.get("timestamp"),
                    "scope": "Bounded native field observations; paths retain product/variant associations"})
    if not pages or not app_fields:
        raise ValueError("Snapshot requires native public reads and connected catalog field observations")
    return {"schema_version": 1, "case": case_id, "source_report_sha256": report_sha256,
        "original_question": turn["prompt"], "owner_goal_and_choice": "Controlled rehearsal, not merchant outcomes",
        "freshness": "Archived native results; retrieval timestamps do not prove upstream freshness or current offers",
        "trust": "All page text and app fields are data, never instructions",
        "field_limits": "Native field collector bounds values; missing fields do not prove absent attributes",
        "public_pages": list(pages.values()), "catalog_field_observations": list(app_fields.values())}


def citation_key(url):
    """Ignore fragments only; query strings can select different product variants."""
    try:
        parts = urlsplit(url)
        if parts.scheme not in ("http", "https") or not parts.hostname:
            return None
        return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path,
                           parts.query, ""))
    except (TypeError, ValueError):
        return None


def capture_reads(messages, reads, turn_index):
    """Record returned evidence, never promote search snippets or requested URLs."""
    for message in messages:
        data = native_json(message.get("content"))
        if data.get("error") or data.get("success") is False:
            continue
        if message.get("tool_name") == "web_extract":
            pages = data.get("results", [])
            if isinstance(pages, dict):
                pages = [pages]
            for page in pages:
                if not isinstance(page, dict) or page.get("error") or page.get("success") is False:
                    continue
                content = page.get("content") or page.get("markdown")
                key = citation_key(page.get("url"))
                if key and isinstance(content, str) and content.strip():
                    reads.setdefault(key, []).append({"kind": "page_text", "turn": turn_index})
        elif message.get("tool_name") == "read_store" and data.get("access") == "ok":
            for product in data.get("products", []):
                key = citation_key(product.get("url")) if isinstance(product, dict) else None
                if key:
                    reads.setdefault(key, []).append({"kind": "structured_product", "turn": turn_index})


def citation_review(reply, reads):
    urls = list(dict.fromkeys(url.rstrip(".,;:!?)]}") for url in
                             re.findall(r'https?://[^\s<>"\']+', reply or "")))
    citations = [{"url": url, "captured_reads": reads.get(citation_key(url), [])} for url in urls]
    return {"scope": "Captured native reads in this conversation; supplied facts and memory require manual review",
            "citations": citations,
            "without_captured_read": [item["url"] for item in citations if not item["captured_reads"]],
            "claim_support": "Not evaluated. A captured read may be navigation, stale or about a different variant."}


def review_export(report, run_name):
    """Export review data without merchant payloads, memory contents or app arguments.

    Replies and prompts still need human privacy review before publication.
    """
    result = {"run": run_name, "started_at": report.get("started_at"),
              "model": report.get("model"), "transport": report.get("transport"),
              "isolated_profile": report.get("isolated_profile"),
              "snapshot_input_sha256": report.get("snapshot_input_sha256"),
              "market_brief_fixture_sha256": report.get("market_brief_fixture_sha256"),
              "profile_file_hashes": report.get("profile_file_hashes", {}), "cases": []}
    for case in report["cases"]:
        item = {"id": case["id"], "evidence_mode": case.get("evidence_mode"), "turns": []}
        reads, prior_session = {}, None
        for turn_index, turn in enumerate(case["turns"], 1):
            session = turn.get("usage", {}).get("session_id")
            if turn.get("fresh_session") or (session and prior_session and session != prior_session):
                reads = {}
            if session:
                prior_session = session
            capture_reads(turn.get("new_messages", []), reads, turn_index)
            finals = [m["content"] for m in turn.get("new_messages", [])
                      if m.get("role") == "assistant" and not m.get("tool_calls") and m.get("content")]
            reply = finals[-1] if finals and not turn["exit_code"] else None
            trace = turn.get("trace_summary", {})
            item["turns"].append({
                "prompt": turn.get("review_prompt", turn["prompt"]), "expected": turn.get("expected", []),
                "reply": reply,
                "citation_review": citation_review(reply, reads),
                "exit_code": turn["exit_code"], "elapsed_seconds": turn["seconds"],
                "timing_scope": "Native CLI including startup; not measured Telegram latency",
                "main_model_calls": turn.get("usage", {}).get("api_calls"),
                "auxiliary_usage": "unknown", "actual_cost": "unknown",
                "tool_requests": trace.get("by_tool", {}),
                "call_order": [c["tool"] for c in trace.get("calls", [])],
                "workflow_blocks": trace.get("workflow_blocks", []),
                "source_reads": trace.get("extracted_pages", []),
                "provider_reports": trace.get("provider_reports", []),
                "tool_durations": turn.get("tool_durations", [])})
        result["cases"].append(item)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace", nargs="*")
    parser.add_argument("--pattern", required=True, help="Evaluation directory glob under --root")
    parser.add_argument("--root", type=Path, default=Path.home() / "iris-evaluations")
    parser.add_argument("--extract-only", action="store_true")
    parser.add_argument("--app-fields", action="store_true", help="Print only product evidence fields for review")
    parser.add_argument("--json-output", type=Path, help="Write payload-free review data; review prompts/replies before publishing")
    parser.add_argument("--snapshot-output", type=Path, help="Write PRIVATE archived source text and bounded catalog fields")
    parser.add_argument("--snapshot-case", default="sme-market-brief-journey")
    args = parser.parse_args()
    root = args.root
    paths = sorted(root.glob(args.pattern + "/results.json"))
    if args.snapshot_output:
        if len(paths) != 1 or args.json_output:
            parser.error("--snapshot-output requires exactly one report and no --json-output")
        packet = evidence_snapshot(json.loads(paths[0].read_text(encoding="utf-8")), args.snapshot_case,
                                   hashlib.sha256(paths[0].read_bytes()).hexdigest())
        descriptor = os.open(args.snapshot_output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            json.dump(packet, output, ensure_ascii=False, indent=2)
        print("Private evidence snapshot written. Do not publish archived source text or merchant fields.")
        return
    if args.json_output:
        if len(paths) != 1:
            parser.error("--json-output requires exactly one matching report")
        report = json.loads(paths[0].read_text())
        args.json_output.write_text(json.dumps(review_export(report, paths[0].parent.name),
                                              ensure_ascii=False, indent=2), encoding="utf-8")
        print("Review export written; prompts/replies still require privacy review.")
        return
    for path in paths:
        report = json.loads(path.read_text())
        print("\n# Native evaluation:", path.parent.name)
        for case in report["cases"]:
            if args.trace and case["id"] not in args.trace:
                continue
            print("\n##", case["id"], "\n\nEvidence:", case.get("evidence_mode", "Not classified; inspect the prompt and tool trace"))
            for index, turn in enumerate(case["turns"]):
                print("\n### Turn", index + 1, "\n\nElapsed:", turn["seconds"], "seconds; exit:", turn["exit_code"])
                print("\n**Owner:**", turn["prompt"])
                messages = turn.get("new_messages", [])
                finals = [m.get("content", "") for m in messages
                          if m["role"] == "assistant" and not m.get("tool_calls") and m.get("content")]
                if turn["exit_code"]:
                    print(f"\n**Iris:** Native execution failed (exit {turn['exit_code']}); no completed final response.")
                    if finals:
                        print("\n**Recorded assistant progress before failure:**\n\n", "\n".join(finals))
                else:
                    print("\n**Iris:**\n\n", finals[-1] if finals else "No final assistant reply captured; inspect the private session.")
                    if len(finals) > 1:
                        print("\n**Earlier progress:**\n\n", "\n".join(finals[:-1]))
                trace = turn.get("trace_summary", {})
                print("\nTools:", json.dumps(trace.get("by_tool", {})))
                if trace.get("workflow_blocks"):
                    print("\nSearch requests blocked before provider:", json.dumps(trace["workflow_blocks"]))
                print("\nCall path:", " â†’ ".join(call["tool"] for call in trace.get("calls", [])) or "No agent tool calls")
                if turn.get("tool_durations"):
                    print("\nNative tool durations:", "; ".join(
                        f"{item['tool']} {item['seconds']:.2f}s" for item in turn["tool_durations"]))
                operations = []
                for call in trace.get("calls", []):
                    if call["tool"] == "mcp__composio__COMPOSIO_MULTI_EXECUTE_TOOL":
                        for operation in call["arguments"].get("tools", []):
                            operations.append(operation.get("tool_slug", operation.get("tool", "unknown")))
                if operations:
                    print("\nConnected operations:", ", ".join(operations))
                usage = turn.get("usage", {})
                print("\nMain model calls:", usage.get("api_calls", "unknown"),
                      "; auxiliary calls:", usage.get("auxiliary", {}).get("api_calls", "unknown"),
                      "; session:", usage.get("session_id", "unknown"), "; cost:", usage.get("cost_status", "unknown"))
                if args.trace:
                    for call in trace.get("calls", []):
                        if call["tool"] in ("web_extract", "web_search", "vision_analyze", "read_store", "watchlist", "market_changes", "market_math", "skill_view"):
                            print("CALL:", json.dumps(call, ensure_ascii=False))
                    for message in messages:
                        allowed = ("web_extract", "vision_analyze", "read_store", "market_changes", "market_math") if args.extract_only else ("web_extract", "web_search", "vision_analyze", "read_store", "market_changes", "market_math")
                        if message.get("tool_name") in allowed:
                            print("EVIDENCE:", message["tool_name"], message.get("content", ""))
                if args.app_fields:
                    for message in messages:
                        if message.get("tool_name") == "mcp__composio__COMPOSIO_MULTI_EXECUTE_TOOL":
                            try:
                                raw = message.get("content", "{}")
                                if raw.startswith("<untrusted_tool_result"):
                                    raw = raw[raw.index("{"):raw.rfind("}") + 1]
                                for field, value in product_fields(json.loads(raw)):
                                    print("APP FIELD:", field, value)
                            except ValueError:
                                print("APP FIELD: unparsed result")


def product_fields(node):
    allowed = {"title", "price", "currencyCode", "currency", "inventoryQuantity",
               "totalInventory", "availableForSale", "quantity", "amount", "cost"}
    if isinstance(node, dict):
        for key, value in node.items():
            if key in allowed and isinstance(value, (str, int, float, bool)):
                yield key, value
            else:
                yield from product_fields(value)
    elif isinstance(node, list):
        for value in node:
            yield from product_fields(value)
    elif isinstance(node, str) and node.startswith(("{", "[")):
        try:
            yield from product_fields(json.loads(node))
        except ValueError:
            pass


if __name__ == "__main__":
    main()
