# Hermes native progress display

Research date: 2026-10-02. Initial research was read-only; the subsequent owner-authorized update
enabled native progress. See the implementation note below.
Purpose: record the native Telegram progress settings so Iris can expose tool activity without custom messaging code.

## Finding and recommendation

Iris explicitly disables Telegram tool progress in `~/.hermes/profiles/iris/config.yaml`:

```yaml
display:
  interim_assistant_messages: true
  platforms:
    telegram:
      tool_progress: off
```

Use the existing Hermes settings, scoped to Telegram:

```yaml
display:
  interim_assistant_messages: true
  platforms:
    telegram:
      tool_progress: all
      tool_progress_grouping: accumulate
      tool_preview_length: 60
      cleanup_progress: true
```

This is a proposal, not an applied change. It shows actual tool activity while the owner waits, edits progress into a compact bubble, and clears temporary progress after successful final delivery. It does not reduce computation time or guarantee continuous updates while the model is working between tool calls.

## Exact behavior in the installed code

- `off`: no tool breadcrumbs. This is also the current built-in Telegram default.
- `new`: suppresses consecutive calls to the same tool, even when their arguments differ. It means tool-name changes, not every distinct query. This can hide repeated web research, so prefer `all` here.
- `all`: renders tool-start events with a concise argument preview. Consecutive identical rendered lines collapse into a repetition counter.
- `verbose`: displays raw argument keys and JSON. Unnecessary and noisy for an owner-facing demo; use only for debugging.
- `log`: writes tool-call logging instead of chat breadcrumbs.
- `accumulate`: edits a progress bubble in place. Overflow and intervening content can start another bubble. Telegram edits are throttled to at least 1.5 seconds apart.
- `separate`: sends one message per tool; noisier.
- `tool_preview_length`: bounds argument preview length; built-in Telegram default is 40. The proposed 60 is a readability choice, not required.
- `cleanup_progress: true`: deletes tracked progress, heartbeat and status bubbles after successful final response delivery. Failed runs preserve breadcrumbs. It does not mean all interim assistant prose is deleted.
- `interim_assistant_messages`: independent from tool progress; retains Iris's own useful brief commentary.

Built-in tools have friendly labels such as “Reading skill”, “Searching the web”, and “Reading”. Custom/plugin/MCP tools, including Composio operations, fall back to tool names and previews. Native progress therefore meets the transparency request, but it is not a polished business-language stage tracker. No additional infrastructure is necessary for the initial improvement.

The relevant normal configuration precedence is per-platform value, global display value, platform default, global default. Legacy `tool_progress_overrides` remains a fallback between platform and global configuration. Explicit YAML wins over the deprecated environment fallback.

`_run_agent_display_settings()` reloads the effective config at the start of each turn. These display changes should apply on the next turn without restarting the gateway; they do not retroactively reconfigure a running turn. This is source-backed behavior, not a live mutation test.

## Evidence

Installed Hermes checkout: `~/.hermes/hermes-agent`, commit `c1488ac947c9bc33fd65ec464548dc9d8edd6122`.

- `gateway/display_config.py`: defaults, normalization and resolution order.
- `gateway/run_turn.py:2898`: per-turn display settings and config reload.
- `gateway/run.py:2846`: effective config loader.
- `gateway/run_turn_runner.py:155`: event filtering and `new` suppression.
- `gateway/run_turn_runner.py:261`: normal versus verbose formatting.
- `gateway/run_turn_runner.py:302`: repeated-line deduplication.
- `gateway/run_turn_runner.py:542`: accumulation and grouping.
- `gateway/run_turn_runner.py:705`: Telegram edit cadence.
- `gateway/run_turn.py:4030`: post-success temporary message cleanup.
- `agent/display.py:482`: friendly built-in tool labels and custom-tool fallback.
- `website/docs/user-guide/messaging/index.md`: native progress and cleanup documentation.

Official references, opened during this research:

- [Hermes messaging: tool progress notifications](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/#tool-progress-notifications)
- [Hermes messaging: progress bubble cleanup](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/#progress-bubble-cleanup-opt-in)
- [Hermes display configuration](https://hermes-agent.nousresearch.com/docs/user-guide/configuration/#display-settings)
- [Pinned installed source](https://github.com/NousResearch/hermes-agent/tree/c1488ac947c9bc33fd65ec464548dc9d8edd6122)

Unverified: real Telegram rendering of the proposed settings, exact progress labels for Iris's current Composio calls, and impact on perceived response time. Verify in one user-initiated Telegram turn after implementation.

## Implemented after owner approval

Enabled `all`, `accumulate`, `cleanup_progress: true`, with `tool_preview_length: 0` rather
than the initially proposed 60. This exposes activity names without raw argument previews.
Verified the installed native resolver returns these effective Telegram settings. Config/model,
OAuth, memory and messages were preserved; the gateway restarted and Telegram reconnected.
The next owner-initiated Telegram turn is the remaining visible rendering check.

Added an explicit connected-app reading boundary in setup: app facts and links come from Composio;
the owner's public browser page is needed only for a rendered-presentation question. The observed
detour followed successful app reads and a constructed handle URL, rather than a Composio
authentication failure. A final isolated replay used connected reads with no own-page visit.

An uncached native extraction through Parallel and a direct HTTP200 read both now returned EGP360
and advertised buy-two-get-two. The original provider response was written to local cache during
the 16:45 request, so the evidence does not establish an old Hermes-cache hit as the cause.
Different upstream content versions remain possible. The updated market skill preserves conflicts,
separates single-unit from basket comparisons and requires fresh verification or an uncertain verdict.

## Response audit that prompted this request

Subsequent live incident: progress exposed two failing browser calls (about 95 and 334 seconds)
in a 17:46 Cairo turn. The final response arrived around 17:57. Removed compulsory browser
verification and temporarily excluded the browser toolset from Iris through native configuration.
Progress itself remains enabled. See [current incident status](../STATUS.md#browser-retry-incident--2-october-2026).

The owner's 16:45 Cairo turn on 2 October took about 86 seconds from the saved user message
to final answer. Actual Composio reads confirmed the sunscreen's EGP320 price, 50 ml variant,
EGP160 tracked unit cost and 20 available units. The saved native web extraction showed EGP216
and 40% off EGP360. A subsequent browser visit to the owner's password-protected storefront
took about 29 seconds and supplied no additional product evidence.

A direct HTTP200 read with an explicit IrisBot user agent at 17:04 Cairo, and a separate web
read, instead showed EGP360 and an advertised buy-two-get-two offer on the
[same official product page](https://infinityclinicpharma.com/ar/products/naturals-sun-screen-gel-spf-50-oily-skin).
The direct HTML's Product/Offer structured data also said EGP360; checkout eligibility was not
tested. This establishes conflicting observations, not the cause: stale extraction, different
page versions and a intervening change were not distinguished. The EGP216 answer followed its
tool evidence but should not be signed off as independently verified current pricing.

At the quoted EGP216, price minus recorded unit cost is EGP56, versus EGP160 at EGP320—a 65%
reduction before all other variable costs. Holding temporarily is defensible; neither the full
contribution nor the optimal price is established. Twenty available units alone establishes
neither scarcity nor excess stock. A better answer makes this arithmetic and its limit visible,
and gives a concrete review criterion rather than just “watch orders”.

Presentation recommendation: a bold verdict, two short evidence bullets and a separate next-step
line, with the source outside the main prose. SOUL currently discourages headings/bullets, so
that instruction should be revised deliberately if implementing this change. No presentation
or runtime change was made in this research pass.
