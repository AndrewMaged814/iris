"""Verify the installed native Hermes plugin's disjoint token accounting; no network."""
import argparse
import importlib.util
from pathlib import Path
import sys
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hermes-root', type=Path, required=True)
    parser.add_argument('--plugin-file', type=Path, help='Test a candidate copy before changing the native plugin')
    args = parser.parse_args()
    sys.path.insert(0, str(args.hermes_root))
    path = args.plugin_file or args.hermes_root / 'plugins/observability/langfuse/__init__.py'
    spec = importlib.util.spec_from_file_location('iris_native_langfuse_contract', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    from agent.usage_pricing import CanonicalUsage
    cases = [dict(input_tokens=3, output_tokens=444, cache_read_tokens=13240,
                  cache_write_tokens=2894, reasoning_tokens=319),
             dict(input_tokens=100, output_tokens=20, reasoning_tokens=10), dict()]
    for values in cases:
        usage = CanonicalUsage(**values)
        exported, _ = module._canonical_usage_and_cost(
            usage, provider='azure-foundry', model='gpt-6-luna', base_url='')
        if exported.get('total') != usage.total_tokens:
            raise SystemExit('FAIL: total must include cache buckets once and reasoning only within output')
    events = []
    @contextmanager
    def attributes(**kwargs):
        events.append(kwargs)
        yield
    class Span:
        def update_trace(self, **kwargs):
            pass
        def start_observation(self, **kwargs):
            return SimpleNamespace()
    class Context:
        def __enter__(self):
            return Span()
    client = SimpleNamespace(create_trace_id=lambda **_: "trace", start_as_current_observation=lambda **_: Context())
    with patch.object(module, 'propagate_attributes', attributes):
        for identity in ("andrew-maged", "iris-evaluation", ""):
            with patch.object(module, '_secret', return_value=identity):
                state = module._start_root_trace("turn", task_id="task", session_id="session", platform="telegram",
                    provider="native", model="luna", api_mode="responses", messages=[], client=client)
                assert state.user_id == identity
                assert events[-1].get('user_id', '') == identity
                before = len(events)
                module._start_child_observation(state, name="tool", as_type="tool", input_value=None)
                if identity:
                    assert events[-1]['user_id'] == identity and len(events) == before + 1
                else:
                    assert len(events) == before  # no invented identity
    print('ok: 3 native token cases; owner/evaluation/unconfigured user attribution on root and children')


if __name__ == '__main__':
    main()
