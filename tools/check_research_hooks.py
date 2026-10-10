"""Operator contract check through pinned Hermes native dispatch; no web/model requests.

Run with Hermes' Python and --profile-home pointing at a private candidate or installed
profile. Only the provider dispatcher is mocked; native pre/post hooks run normally.
No writes to watches, memories, connected apps or conversation records are requested.
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
    args = parser.parse_args()
    home = args.profile_home.expanduser().resolve()
    os.environ["HERMES_HOME"] = str(home)
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
        "business_state_writes_requested": False, "actual_network_retrieval_tested": False}))


if __name__ == "__main__":
    main()
