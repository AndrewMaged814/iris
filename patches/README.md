# Hermes tracing fixes

These two small patches correct the Langfuse plugin in the tested Hermes runtime
(`c1488ac`). They support Iris’s observability layer; they do not change market research
or the model’s answers.

| Patch | Why it exists |
| --- | --- |
| [Token total](hermes-langfuse-token-total.patch) | Supplies the canonical total so reasoning tokens already included in output are not counted twice. |
| [User labels](hermes-langfuse-user-id.patch) | Carries the configured owner/evaluation label onto the trace and its model/tool observations, enabling usage review by user. |

Both corrections are applied to the tested runtime and checked by
[`check_langfuse_usage.py`](../tools/check_langfuse_usage.py). They are retained so another
operator can reproduce the tracing setup. They are only needed when the installed Hermes
version lacks these corrections; they are not applied automatically by the Iris profile.

Check the installed version and back up the plugin before applying a patch. See
[observability setup](../docs/OBSERVABILITY.md#two-pinned-runtime-corrections) for commands
and verification.
