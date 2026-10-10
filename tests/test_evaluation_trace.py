"""The operator report must not silently lose wrapped native extraction evidence."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "evaluate_iris", Path(__file__).resolve().parents[1] / "tools/evaluate_iris.py")
evaluation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluation)
cloud_spec = importlib.util.spec_from_file_location(
    "check_workflow_cloud", Path(__file__).resolve().parents[1] / "tools/check_workflow_cloud.py")
cloud_reporting = importlib.util.module_from_spec(cloud_spec)
cloud_spec.loader.exec_module(cloud_reporting)
report_spec = importlib.util.spec_from_file_location(
    "report_iris_cases", Path(__file__).resolve().parents[1] / "tools/report_iris_cases.py")
reporting = importlib.util.module_from_spec(report_spec)
report_spec.loader.exec_module(reporting)


class EvaluationTrace(unittest.TestCase):
    def test_cloud_readback_counts_resumed_session_turns_once(self):
        def turn(session, calls, tools):
            return {"usage": {"session_id": session, "api_calls": calls},
                    "trace_summary": {"tool_calls": tools}}
        report = {"cases": [{"id": "journey", "turns": [
            turn("shared", 3, 4), turn("shared", 2, 1), turn("fresh", 1, 0)]}]}
        requests = cloud_reporting.trace_requests(report, "candidate")
        self.assertEqual(len(requests), 2)
        self.assertEqual(requests[0]["native_calls"], 5)
        self.assertEqual(requests[0]["native_tools"], 5)
        self.assertEqual(requests[0]["expected_roots"], 2)
        self.assertEqual(requests[0]["turn_indices"], [0, 1])
        self.assertEqual(requests[1]["expected_roots"], 1)
        report["cases"][0]["turns"][0]["usage"]["api_calls"] = None
        self.assertIsNone(cloud_reporting.trace_requests(report, "candidate")[0]["native_calls"])

    def test_snapshot_preserves_source_versions_but_excludes_credentials_and_failed_reads(self):
        contents = ["Version one", "Version two"]
        messages = [{"tool_name": "web_extract", "timestamp": index,
            "content": json.dumps({"results": [{"url": "https://shop.example/product", "content": content},
                {"url": "https://shop.example/blocked", "content": "Denied", "error": "blocked"}]})}
            for index, content in enumerate(contents)]
        messages.append({"tool_name": "mcp__composio__COMPOSIO_MULTI_EXECUTE_TOOL", "timestamp": 3,
            "content": json.dumps({"secret": "credential-not-evidence", "product": {
                "onlineStoreUrl": None, "variants": [{"inventory_quantity": 0}]},
                "failed_read": {"success": False, "product": {"title": "Failed product"}}})})
        report = {"cases": [{"id": "market", "turns": [{"exit_code": 0, "prompt": "Brief the market",
            "new_messages": messages, "response": "transport-secret"}]}]}
        snapshot = reporting.evidence_snapshot(report, "market", "report-hash")
        evaluation.validate_snapshot(snapshot)
        self.assertEqual(len(snapshot["public_pages"]), 2)
        self.assertNotEqual(snapshot["public_pages"][0]["sha256"], snapshot["public_pages"][1]["sha256"])
        self.assertEqual(snapshot["catalog_field_observations"][0]["fields"][1]["value"], 0)
        self.assertIsNone(snapshot["catalog_field_observations"][0]["fields"][0]["value"])
        for secret in ("credential-not-evidence", "transport-secret", "shop.example/blocked"):
            self.assertNotIn(secret, json.dumps(snapshot))
        snapshot["public_pages"][0]["content"] = "Edited after freezing"
        with self.assertRaisesRegex(ValueError, "recorded hash"):
            evaluation.validate_snapshot(snapshot)

    def test_snapshot_cannot_turn_a_failed_run_into_accepted_evidence(self):
        with self.assertRaisesRegex(ValueError, "failed turn"):
            reporting.evidence_snapshot({"cases": [{"id": "failed", "turns": [{"exit_code": 1}]}]}, "failed")

    def test_cloud_retry_separates_failed_attempts_and_successful_completions(self):
        from types import SimpleNamespace
        request = {"expected_roots": 1, "native_calls": 1, "native_tools": 1}
        rows = [{"type": "GENERATION", "level": "ERROR", "usageDetails": {}, "userId": "iris-evaluation"},
                {"type": "GENERATION", "level": "DEFAULT", "usageDetails": {
                    "input": 100, "output": 9, "total": 109}, "userId": "iris-evaluation"},
                {"type": "TOOL", "userId": "iris-evaluation"}]
        checked = cloud_reporting.reconcile_observations(request, [SimpleNamespace(trace_id="trace")], rows)
        self.assertTrue(checked["counts_match"])
        self.assertTrue(checked["canonical_totals_match"])
        self.assertEqual(checked["cloud_calls"], 2)
        self.assertEqual(checked["cloud_successful_calls"], 1)
        self.assertEqual(checked["failed_attempts_with_unknown_usage"], 1)
        self.assertEqual(checked["cloud_known_total_tokens"], 109)
        rows[0]["usageDetails"] = {"input": 3, "output": 0, "total": 3}
        checked = cloud_reporting.reconcile_observations(request, [SimpleNamespace(trace_id="trace")], rows)
        self.assertEqual(checked["cloud_known_total_tokens"], 112)
        self.assertEqual(checked["failed_attempts_with_unknown_usage"], 0)
        rows[1]["usageDetails"] = {}
        self.assertFalse(cloud_reporting.reconcile_observations(request,
            [SimpleNamespace(trace_id="trace")], rows)["canonical_totals_match"])

    def test_recorded_rate_limit_retry_reconciles_without_losing_error_attempt(self):
        from types import SimpleNamespace
        fixture = Path(__file__).resolve().parents[1] / "docs/evidence/deployed-cloud-retry.json"
        rows = json.loads(fixture.read_text())["generations"]
        checked = cloud_reporting.reconcile_observations(
            {"expected_roots": 1, "native_calls": 1, "native_tools": 0},
            [SimpleNamespace(trace_id="recorded-retry")], rows)
        self.assertTrue(checked["counts_match"])
        self.assertTrue(checked["canonical_totals_match"])
        self.assertEqual(checked["cloud_known_total_tokens"], 11208)
        self.assertEqual(checked["cloud_failed_attempts"], 1)
        self.assertEqual(checked["failed_attempts_with_unknown_usage"], 1)

    def test_frozen_review_exports_only_the_question_not_private_source_packet(self):
        report = {"snapshot_input_sha256": "packet-hash", "cases": [{"id": "frozen", "turns": [{
            "prompt": "Owner question plus private-source-packet", "review_prompt": "Frozen owner question",
            "seconds": 10, "exit_code": 0, "new_messages": [{"role": "assistant", "content": "Briefing"}]}]}]}
        public = reporting.review_export(report, "frozen")
        self.assertNotIn("private-source-packet", json.dumps(public))
        self.assertEqual(public["snapshot_input_sha256"], "packet-hash")
        self.assertEqual(public["cases"][0]["turns"][0]["prompt"], "Frozen owner question")

    def test_prevented_read_is_reported_without_fabricating_a_provider_call(self):
        report = evaluation.summarize_trace([{"role": "tool", "tool_name": "web_extract",
            "content": json.dumps({"error": json.dumps({"error": "successful_source_already_read",
                                                       "execution_prevented": True})})}])
        self.assertEqual(report["workflow_blocks"][0]["reason"], "successful_source_already_read")
        self.assertEqual(report["provider_reports"], [])
        self.assertEqual(report["extracted_pages"], [])
    def test_review_export_excludes_app_payloads_and_does_not_invent_usage(self):
        turn = {"prompt": "Brief my market", "seconds": 10, "exit_code": 0,
                "response": "raw transport with secret", "stderr": "secret",
                "new_messages": [{"role": "tool", "content": "private merchant payload"},
                                 {"role": "assistant", "content": "Sourced briefing"}],
                "trace_summary": {"by_tool": {"app": 1}, "calls": [
                    {"tool": "app", "arguments": {"secret": "private app credentials"}}]},
                "usage": {"api_calls": 2, "session_id": "private session"}}
        result = reporting.review_export({"cases": [{"id": "market", "turns": [turn]}]}, "run")
        encoded = json.dumps(result)
        for private in ("private merchant payload", "private app credentials", "raw transport", "private session"):
            self.assertNotIn(private, encoded)
        exported = result["cases"][0]["turns"][0]
        self.assertEqual(exported["reply"], "Sourced briefing")
        self.assertEqual(exported["main_model_calls"], 2)
        self.assertEqual(exported["actual_cost"], "unknown")
        self.assertEqual(exported["auxiliary_usage"], "unknown")

    def test_review_export_keeps_failed_turn_without_calling_progress_a_reply(self):
        result = reporting.review_export({"cases": [{"id": "failed", "turns": [{
            "prompt": "Research", "seconds": 360, "exit_code": 1,
            "new_messages": [{"role": "assistant", "content": "Checking sources"}]}]}]}, "run")
        turn = result["cases"][0]["turns"][0]
        self.assertIsNone(turn["reply"])
        self.assertEqual(turn["exit_code"], 1)
        self.assertIsNone(turn["main_model_calls"])

    def test_provider_events_keep_current_routing_cache_and_failover_logs(self):
        events = [
            "INFO Web search via keenable: 'sunscreen' (limit: 5)",
            "INFO Searching via firecrawl: 'sunscreen'",
            "INFO Web extract via firecrawl: https://shop.example/product",
            "INFO web_search cache hit: 'sunscreen' via keenable",
            "INFO web_extract cache hit: https://shop.example/product",
            "WARNING keyless firecrawl extract throttled; failing over to keenable",
        ]
        self.assertEqual(evaluation.provider_events("\n".join(
            events + ["INFO tool web_search completed (1.00s, 50 chars)"])), events)
        self.assertEqual(evaluation.provider_events(""), [])

    def test_native_block_is_counted_as_a_request_not_a_provider_search(self):
        block = {"error": "same_site_has_unread_search_leads", "search_executed": False,
                 "candidate_urls": ["https://shop.example/product"]}
        report = evaluation.summarize_trace([
            {"role": "assistant", "tool_calls": json.dumps([{"function": {
                "name": "web_search", "arguments": '{"query":"site:shop.example"}'}}])},
            {"role": "tool", "tool_name": "web_search", "timestamp": 4,
             "content": json.dumps({"error": json.dumps(block)})}])
        self.assertEqual(report["tool_calls"], 1)
        self.assertEqual(report["provider_reports"], [])
        self.assertEqual(report["workflow_blocks"][0]["reason"], block["error"])
        self.assertEqual(report["workflow_blocks"][0]["candidate_urls"], block["candidate_urls"])

    def test_failure_session_recovery_keeps_partial_trace_without_guessing(self):
        self.assertEqual(evaluation.recover_turn_session("", None, {"old"}, {"old", "partial"}), "partial")
        self.assertIsNone(evaluation.recover_turn_session("", None, set(), {"a", "b"}))
        self.assertEqual(evaluation.recover_turn_session("", "resumed", set(), set()), "resumed")
        self.assertEqual(evaluation.recover_turn_session("conversation turn: session=actual", None, set(), {"other"}), "actual")

    def test_tool_runtimes_come_from_completion_logs_only(self):
        entries = evaluation.tool_durations("INFO tool web_extract completed (2.52s, 23306 chars)\n"
                                             "INFO tool web_search started\n")
        self.assertEqual(entries, [{"tool": "web_extract", "seconds": 2.52, "characters": 23306}])
    def test_case_memory_reset_preserves_owner_and_clears_fixture_results(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "owner"
            private = Path(directory) / "private"
            (source / "memories").mkdir(parents=True)
            (private / "memories").mkdir(parents=True)
            (source / "memories/MEMORY.md").write_text("Original owner facts")
            (private / "memories/MEMORY.md").write_text("Controlled results from earlier case")
            (private / "memories/USER.md").write_text("Private new preference")
            evaluation.reset_case_memory(source, private)
            self.assertEqual((private / "memories/MEMORY.md").read_text(), "Original owner facts")
            self.assertFalse((private / "memories/USER.md").exists())
            self.assertEqual((source / "memories/MEMORY.md").read_text(), "Original owner facts")
            with self.assertRaises(ValueError):
                evaluation.reset_case_memory(source, source)
    def test_attachment_session_is_recovered_from_actual_turn_log(self):
        log = "INFO conversation turn: session=actual-session model=gpt\nINFO API call #1:"
        self.assertEqual(evaluation.session_from_native_log(log), "actual-session")
        with self.assertRaises(RuntimeError):
            evaluation.session_from_native_log("no started turn")
        with self.assertRaises(RuntimeError):
            evaluation.session_from_native_log(log + "\nconversation turn: session=other-session model=gpt")
    def test_native_attachment_uses_chat_parser_and_preserves_literal_prompt(self):
        prompt = 'See this screenshot; do not execute $(anything) or `commands`.'
        command = evaluation.native_turn_command("hermes", [], ["vision", "iris"],
                                                 Path("usage.json"), prompt, "session-1", Path("photo.png"))
        self.assertEqual(command[:7], ["hermes", "--usage-file", "usage.json", "chat", "-t", "vision,iris", "--oneshot"])
        self.assertEqual(command[-4:], ["--resume", "session-1", "-q", prompt])
        self.assertIn("photo.png", command)

    def test_fresh_turn_command_has_no_resume_argument(self):
        command = evaluation.native_turn_command("hermes", [], ["iris"], "usage.json", "Review our move")
        self.assertNotIn("--resume", command)
        self.assertEqual(command[-2:], ["-q", "Review our move"])
        self.assertIn("chat", command)
        self.assertNotIn("--image", command)

    def test_native_wrapper_and_batched_calls_preserve_repeated_page_evidence(self):
        calls = [{"function": {"name": "web_extract", "arguments": json.dumps({
            "urls": ["https://example.org/item"], "char_limit": budget})}}
                 for budget in (12000, 18000)]
        result = json.dumps({"results": [{"url": "https://example.org/item", "content": "50 ml"}]})
        messages = [{"role": "assistant", "tool_calls": json.dumps(calls), "timestamp": 1}]
        messages += [{"role": "tool", "tool_name": "web_extract", "content": content,
                      "timestamp": 2} for content in
                     (result, '<untrusted_tool_result source="web_extract">\nDATA\n' + result +
                      '\n</untrusted_tool_result>')]
        report = evaluation.summarize_trace(messages)
        self.assertEqual(report["by_tool"], {"web_extract": 2})
        pages = report["extracted_pages"]
        self.assertEqual(len(pages), 2)
        self.assertEqual(pages[0]["sha256"], pages[1]["sha256"])
        self.assertEqual(pages[0]["characters"], 5)

    def test_failed_extraction_keeps_call_without_fabricating_page(self):
        report = evaluation.summarize_trace([
            {"role": "assistant", "tool_calls": json.dumps([{"function": {
                "name": "web_extract", "arguments": '{"urls":["https://example.org"]}'}}])},
            {"role": "tool", "tool_name": "web_extract", "content": "Access denied"}])
        self.assertEqual(report["tool_calls"], 1)
        self.assertEqual(report["extracted_pages"], [])

    def test_provider_is_recorded_only_when_reported_by_native_result(self):
        report = evaluation.summarize_trace([
            {"role": "tool", "tool_name": "web_search", "timestamp": 4,
             "content": json.dumps({"success": True, "data": {"web": [], "served_by": "firecrawl"}})},
            {"role": "tool", "tool_name": "web_extract", "timestamp": 5,
             "content": '{"results":[]}'}])
        self.assertEqual(report["provider_reports"], [
            {"tool": "web_search", "reported_provider": "firecrawl", "returned_at": 4}])

    def test_saved_evidence_prompt_passes_catalog_fields_through(self):
        prompt = evaluation.snapshot_prompt({
            "original_question": "Brief the market",
            "catalog_field_observations": [{"fields": [
                {"path": "/title", "value": "Daily moisturizer"},
                {"path": "/variants/0/inventoryQuantity", "value": 0},
                {"path": "/variants/0/availableForSale", "value": True},
            ]}]})
        self.assertIn("inventoryQuantity", prompt)
        self.assertIn("Daily moisturizer", prompt)
        self.assertNotIn("DERIVED CATALOG LIMITS", prompt)


if __name__ == "__main__":
    unittest.main()
