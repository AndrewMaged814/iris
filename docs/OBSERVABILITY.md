# Observability: follow an investigation

**Updated 10 October 2026.** Hermes's bundled Langfuse plugin records the model/tool timeline.
Iris uses Luna and native Composio; tracing adds no research engine or model call.

## What you can inspect

| Evidence | Where | What it helps answer |
| --- | --- | --- |
| Model/tool order, timing, usage and failures | Native Langfuse timeline | What ran, how long it took, whether it retried. |
| Questions, final replies, arguments and source results | Private Hermes session/evaluation report | Which source supports the answer. |
| URLs, content hashes, tool durations and provider logs | Native evaluation reports | Whether a follow-up reused evidence and where retrieval slowed. |
| Source-to-claim review | [Evidence ledger](EVALUATION.md) | Which claims were supported, uncertain or wrong. |
| Provider invoice | Billing reconciliation, still pending | Actual cost rather than a token-only estimate. |

This shows execution and lets operators review Iris's stated business rationale against its
sources. It does not expose hidden chain-of-thought or establish that a claim is true.
Parallel tool durations must not be summed into owner waiting time.

## Recorded proof

[The earlier reconciled sample](evidence/run-summary.json) covers ten turns across six
sessions: two owner Telegram turns and eight private turns, **24 main calls / 14 tools**.
Counts and canonical usage matched; no duplicate observation IDs appeared in that sample.
[The latest release verification](STATUS.md) records subsequent checks separately.

[The user-label probe](evidence/langfuse-users.json) checked two CLI sessions: owner/operator
label `andrew-maged`, evaluation label `iris-evaluation`. That probe did not establish
Telegram attribution. The label is attribution; the Telegram allowlist is access control.

[The retained retry](evidence/deployed-cloud-retry.json) contains one rate-limit ERROR
attempt with no usage and one successful completion with 11,208 canonical tokens. Native
CLI counts one successful call. `tools/check_workflow_cloud.py` now separates attempts from
completions, retains known failure usage and marks absent usage unknown. Regression tests
exercise the actual recorded shape. A failed attempt is neither erased nor silently treated
as a billable success.

## Reproducible operator review

Run [native cases](TESTING.md) in an isolated profile. Reports retain the configured model,
runtime file hashes, case questions, source reads, call sequence, durations and replies.
A private frozen packet can separate composition from retrieval; neither replaces a live run.
Export a reviewed public record without raw app payloads:

```sh
python tools/report_iris_cases.py --root PRIVATE_EVALUATIONS --pattern RUN_NAME --json-output REVIEW.json
```

The export removes app arguments, memory and raw transport data. Prompts/replies still need
a privacy review. Raw evidence stays private. A successful tool call is not an accuracy score.

Exports now include `citation_review`: cited URLs without a captured native read are flagged,
and page text is distinguished from structured product data. Follow-ups reuse reads from the
same conversation; a fresh session starts a new read inventory. Failed/empty extracts and
search snippets do not establish a read. Native traces label failed, empty and content-returned
extractions separately. Query strings are retained because they may select a product variant.

This is an operator review aid, not an agent search gate or a factual verdict. A link may be
supplied by the owner or cited to report a failed fetch. Returned text may contain only
navigation or the wrong product facts. Check the actual claim against the private source.

## Setup and privacy

The tested runtime is Hermes `c1488ac`, Python Langfuse SDK 4.17.0. Use Hermes's Python:

```sh
python -m pip install 'langfuse==4.17.0'
hermes -p iris plugins enable observability/langfuse
```

Keep credentials in the private profile; [.env.EXAMPLE](../.env.EXAMPLE) contains variable
names only. On this pinned revision credentials use profile-scoped lookup, while capture
mode comes from the process environment. The shared gateway uses this non-secret drop-in:

```ini
[Service]
Environment=HERMES_LANGFUSE_CAPTURE=metadata
```

Metadata capture omits raw prompts, replies, memory, app data and tool results from Cloud.
Names, IDs, timing and usage remain visible. Reload the existing gateway after changing
its environment; preserve configured owners, OAuth, sessions and schedules.

Langfuse links require project access. For judges, publish a reviewed sanitized export or
screenshot belonging to the demonstrated run, not credentials or raw merchant payloads.

## Two pinned-runtime corrections

The [token-total patch](../patches/hermes-langfuse-token-total.patch) prevents reasoning
already included in output from being counted again. The
[user-ID patch](../patches/hermes-langfuse-user-id.patch) propagates the profile's
`HERMES_LANGFUSE_USER_ID` to root and child observations. Private copies override the label
with `iris-evaluation`; unconfigured profiles do not invent an identity.

Back up the native plugin and profile environment. Check patches against the actual
revision before applying; upstream may already include a fix. For each patch:

```sh
git -C PATH_TO_HERMES apply --check PATH_TO_PATCH
git -C PATH_TO_HERMES apply PATH_TO_PATCH
python tools/check_langfuse_usage.py --hermes-root PATH_TO_HERMES
```

This native check is separate from Iris's offline suite. Earlier Cloud observations are not
retroactively repaired or relabeled. Disable tracing with
`hermes -p iris plugins disable observability/langfuse` if rollback is needed.

## Remaining limits

- Complete auxiliary usage and actual provider charges are unreconciled; unknown is not free.
- SDK context-detach warnings have occurred despite successful exports. Broader failure and
  parallel-correlation coverage remains open.
- Metadata capture needs the private source report to explain a business claim.
- A timestamp, URL or repeated hash does not prove upstream freshness or variant association.
- No general accuracy rate or latency distribution is established.

Use the SDK observations API, inspecting children by trace ID. The legacy trace-list API
returned HTTP410 for the inspected organization. The checker bounds its time window and
refuses response-limit truncation rather than claiming complete accounting.

Sources: [pinned native plugin](https://github.com/NousResearch/hermes-agent/tree/c1488ac947c9bc33fd65ec464548dc9d8edd6122/plugins/observability/langfuse),
[SDK](https://langfuse.com/docs/observability/sdk/overview),
[public API](https://langfuse.com/docs/api-and-data-platform/features/public-api).
