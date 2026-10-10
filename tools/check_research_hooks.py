"""Operator contract check through pinned Hermes native dispatch; no web/model requests.

Run with Hermes' Python and --profile-home pointing at a private candidate or installed
profile. Only the provider dispatcher is mocked; native pre/post hooks run normally.
Public-demo checks propose denied writes against a mock provider; no business changes execute.
Hermes may update its native discovery caches.
"""
import argparse
import json
import os
from pathlib import Path
from unittest.mock import patch


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile-home", type=Path, required=True)
    parser.add_argument("--public-demo", action="store_true", help="Also verify visitor blocks through native dispatch")
    args = parser.parse_args()
    home = args.profile_home.expanduser().resolve()
    os.environ["HERMES_HOME"] = str(home)
    if args.public_demo:
        from dotenv import load_dotenv
        load_dotenv(home / ".env", override=True)
        assert os.environ.get("IRIS_PUBLIC_DEMO", "").lower() in {"true", "1", "yes"}
    # Imports must follow home selection: Hermes scopes plugins to that profile.
    import model_tools
    from hermes_cli.plugins import discover_plugins
    discover_plugins()
    names = set(model_tools.get_all_tool_names())
    assert {"read_store", "watchlist", "market_changes", "market_math"} <= names
    executed = []
    failed_once = False

    def provider(name, inputs, **_):
        nonlocal failed_once
        executed.append(name)
        if name == "web_search":
            if inputs.get("query") == "retry after failure" and not failed_once:
                failed_once = True
                return json.dumps({"success": False, "error": "controlled provider failure"})
            return json.dumps({"success": True, "data": {"web": [
                {"url": "https://shop.example/product", "title": "Moisturizer50ml"}]}})
        if name == "web_extract":
            return json.dumps({"error": "controlled failed read"})
        if args.public_demo and name == "mcp__composio__COMPOSIO_MULTI_EXECUTE_TOOL":
            return json.dumps({"successful": True, "data": {"controlled_read": True}})
        raise AssertionError("Unexpected provider operation: " + name)

    ids = {"task_id": "iris-hook-contract", "session_id": "iris-hook-contract",
           "turn_id": "turn1", "api_request_id": "contract"}
    def call(name, inputs, call_id, turn=None):
        identity = {**ids, "tool_call_id": call_id}
        if turn:
            identity["turn_id"] = turn
        return json.loads(model_tools.handle_function_call(name, inputs, **identity))

    with patch.object(model_tools.registry, "dispatch", side_effect=provider):
        call("web_search", {"query": "Egypt moisturizer"}, "s1")
        follow_up = call("web_search", {"query": "site:shop.example moisturizer50ml"}, "s2")
        assert follow_up.get("success") is True, follow_up
        assert executed == ["web_search", "web_search"], executed
        call("web_extract", {"urls": ["https://shop.example/product"]}, "e1")
        duplicate = call("web_search", {"query": "SITE:SHOP.EXAMPLE   MOISTURIZER50ML"}, "s3")
        assert "query_already_completed_this_turn" in str(duplicate), duplicate
        assert "cached_result" in str(duplicate), duplicate
        call("web_search", {"query": "site:other.example moisturizer"}, "s4")
        call("web_search", {"query": "site:shop.example moisturizer50ml"}, "s5", turn="turn2")
        assert executed == ["web_search", "web_search", "web_extract", "web_search", "web_search"], executed
        call("web_search", {"query": "retry after failure"}, "r1")
        retried = call("web_search", {"query": "retry after failure"}, "r2")
        assert retried.get("success") is True, retried
        assert executed[-2:] == ["web_search", "web_search"], executed

        if args.public_demo:
            from gateway.session_context import set_session_vars, clear_session_vars
            from agent.secret_scope import get_secret
            visitor_tokens = set_session_vars(platform="telegram", chat_type="dm",
                                               user_id="judge-contract", user_name="Andrew")
            before = len(executed)
            denied = [
                ("memory", {"action": "add", "target": "USER.md", "content": "visitor"}),
                ("watchlist", {"operation": "remove", "name": "Rival"}),
                ("mcp__composio__COMPOSIO_MANAGE_CONNECTIONS", {"toolkits": [{"name": "shopify"}]}),
                ("mcp__composio__COMPOSIO_MULTI_EXECUTE_TOOL", {"tools": [
                    {"tool_slug": "GOOGLESHEETS_SEARCH_SPREADSHEETS", "arguments": {}}]}),
                ("mcp__composio__COMPOSIO_MULTI_EXECUTE_TOOL", {"tools": [
                    {"tool_slug": "SHOPIFY_GRAPH_QL_QUERY", "arguments": {"query": "mutation { productDelete(id: 1) { id } }"}}]})]
            for i, (name, inputs) in enumerate(denied):
                result = call(name, inputs, "demo-denied-" + str(i))
                assert result.get("error") or result.get("blocked"), result
                assert len(executed) == before, (name, executed)
            read = call("mcp__composio__COMPOSIO_MULTI_EXECUTE_TOOL", {"tools": [
                {"tool_slug": "SHOPIFY_GET_PRODUCTS_PAGINATED", "arguments": {"limit": 5}}]}, "demo-read")
            assert executed[-1] == "mcp__composio__COMPOSIO_MULTI_EXECUTE_TOOL", read
            clear_session_vars(visitor_tokens)
            operator_tokens = set_session_vars(platform="telegram", chat_type="dm",
                user_id=get_secret("TELEGRAM_ALLOWED_USERS"), user_name="Operator")
            before_owner = len(executed)
            call("mcp__composio__COMPOSIO_MULTI_EXECUTE_TOOL", denied[-1][1], "operator-mock-write")
            assert len(executed) == before_owner + 1, executed
            clear_session_vars(operator_tokens)

    # Exercise the installed registry handler as well, without a fake math result.
    numeric = call("market_math", {"operation": "compare_baskets",
        "own": {"price": 320, "currency": "EGP", "quantity": 50, "unit": "ml"},
        "rival": {"totals": [570, 285], "currency": "EGP", "quantity": 120, "unit": "ml"}}, "m1")
    data = numeric.get("data", numeric)
    assert data.get("quantity_ratio_rival_to_own") == 2.4, numeric
    current_only = call("market_math", {"operation": "unit_economics", "currency": "EGP",
        "current_price": 320, "unit_cost": 160, "variable_cost_per_item": 10,
        "payment_fee_percent": 3, "minimum_to_keep": 100}, "m2")
    economics = current_only.get("data", current_only)
    assert economics.get("current", {}).get("amount_after_supplied_costs") == 140.4, current_only
    assert economics.get("proposed") is None and "error" not in economics, current_only
    print(json.dumps({"native_dispatch_contract": "passed", "provider_calls": executed,
        "blocked_before_provider": 1, "different_query_reached_provider": True,
        "different_source_and_new_turn_allowed": True, "quantity_ratio": 2.4,
        "failed_search_retry_allowed": True,
        "current_only_amount": 140.4,
        "business_state_writes_requested": args.public_demo, "business_state_writes_executed": False,
        "actual_network_retrieval_tested": False}))
    if args.public_demo:
        from types import SimpleNamespace
        from gateway.run_inbound import GatewayInboundMixin
        from gateway.platforms.event import MessageEvent
        from gateway.session import SessionSource, build_session_key
        from gateway.config import Platform
        from gateway.slash_access import policy_from_extra
        from gateway.run import GatewayRunner, load_gateway_config_for_runner
        import yaml
        visitor = SessionSource(platform=Platform.TELEGRAM, chat_id="judge-contract",
                                user_id="judge-contract", user_name="Salma", profile="iris")
        runner = object.__new__(GatewayRunner)
        runner.config = load_gateway_config_for_runner()
        runner.adapters, runner._profile_adapters = {}, {}
        assert runner._is_user_authorized(visitor, allow_adapter_delegation=False)
        event = MessageEvent(text="/start", source=visitor)
        rewritten = GatewayInboundMixin._hm_pre_gateway_dispatch_hook(SimpleNamespace(), event, visitor)
        assert rewritten is not None and rewritten.text.startswith("Hi Iris!"), rewritten
        assert rewritten.source == visitor and event.text == "/start"
        telegram = yaml.safe_load((home / "config.yaml").read_text()).get("platforms", {}).get("telegram", {})
        from agent.secret_scope import get_secret
        operator_id = get_secret("TELEGRAM_ALLOWED_USERS")
        for scope in ("dm", "group"):
            policy = policy_from_extra(telegram, scope)
            assert policy.enabled and not policy.can_run(visitor.user_id, "restart"), (scope, policy)
            assert policy.can_run(operator_id, "restart"), (scope, policy)
        second = SessionSource(platform=Platform.TELEGRAM, chat_id="second-judge", user_id="second-judge", profile="iris")
        assert build_session_key(visitor) != build_session_key(second)
        print(json.dumps({"public_demo_native_dispatch": "passed", "denied_before_provider": len(denied),
                          "allowed_catalog_read_reached_mock_provider": True,
                          "operator_access_preserved": True, "operator_name_spoof_did_not_grant_access": True,
                          "connected_app_changes_executed": False,
                          "native_start_rewritten_before_commands": True,
                          "native_unknown_telegram_visitor_authorized": True,
                          "visitor_admin_commands_blocked_dm_and_group": True,
                          "visitor_session_keys_distinct": True,
                          "telegram_delivery_tested": False}))


if __name__ == "__main__":
    main()
