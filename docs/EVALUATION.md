# Evidence ledger

**Updated 10 October 2026.** Iris is evaluated as a market watcher: research across
competitors, connect findings to the store, investigate, prioritize, draft on request and
remember the chosen move. Completion is recorded separately from factual correctness.

## What the evidence can establish

| Evidence | What it shows | Limit |
| --- | --- | --- |
| Offline contracts | Reader, calculations, persistence, guards and reporting behave as specified. | No model or live sources. |
| Native private conversations | Actual Luna replies and native Hermes/Composio tool paths. | CLI startup is included; no Telegram delivery. |
| Frozen-source repetitions | Interpretation of the same archived pages/catalog fields. | No current retrieval; not a general accuracy rate. |
| Owner Telegram replies | What Iris actually said in the owner's chat. | A few questions, not the whole demo journey. |
| Langfuse readback | Execution counts, timing, attribution and canonical usage. | No proof of answer truth or complete actual charges. |

The Mira Nile connected catalog is staged for the demo. Goals, drafts and decisions in
rehearsals are controlled. Public competitor pages are live retrievals unless labeled frozen.
No verified merchant time saved, cost saved or revenue lift is established.

## Latest Cursor rehearsal

The private native run `market-brief-live-stock-20261010` completed six turns on Luna:

| Turn | Elapsed seconds | Main calls | Tool requests |
| --- | ---: | ---: | ---: |
| Three-business, two-family briefing | 108.95 | 13 | 26 |
| Investigate Infinity's wider offers | 41.05 | 4 | 9 |
| Choose this week's priority | 16.48 | 1 | 0 |
| Requested Egyptian Arabic draft | 9.62 | 2 | 1 |
| Save chosen move in private memory | 10.67 | 2 | 1 |
| Fresh-session recall | 7.70 | 1 | 0 |

The first reply retained sunscreen inventory **20** and separately reported the moisturizer's
**0/purchasable** conflict. These match the native catalog records. It preserved the owner's
unknown sunscreen format and NUT's unresolved size-price join. The Infinity follow-up used
product, collection and terms pages; its possible sales-push explanation was labeled as an
interpretation. It did not draft until asked. The chosen post remained planned, not published,
and fresh recall preserved unknown results/baseline.

Weaknesses remain: the first reply exceeds the requested 180–250-word target, ten searches
add work, and the “which texture fits me?” opening suggests a personalization angle while
own texture/skin-type benefits are unknown. The later priority/draft avoid those claims.
This is one encouraging rehearsal using earlier instructions, not proof of repeatability or
acceptance of a new release. [Sanitized replies and call path](evidence/cursor-latest.json).

## Publication candidate: first factual check failed

The cleaned-plugin broad rehearsal completed, but its first reply cited Cairo Drop's
Argento EGP329/50ml listing from search without extracting that product page. Its opening
also linked all competitors into a routine/hydration strategy not established by the read
sources. Stock20 and the moisturizer conflict were preserved, but those successes do not
make the briefing pass. It used 16 main calls, 33 tool requests and 15 searches; the first
reply took 133.43s. [Replies and call path](evidence/release-first-review.json).

The final source check now requires each material public fact to match a successful read
at its exact cited URL. Late search leads must be opened or their numbers omitted, and the
opening cannot invent a shared pattern. The next broad rerun improved the opening and read-source coverage, but its priority
follow-up fabricated an own-product URL despite `onlineStoreUrl` being null. Its first
reply took 99.34s with nine main calls and seven searches; this remains a failed factual
check, not an acceptance result. [Second broad sequence](evidence/release-grounding.json).
The final footer check explicitly preserves a null public URL across follow-ups. The
release result and remaining gaps are in [status](STATUS.md). The casual-overview rerun removed the unnecessary catalog route:
15.07s with two skill reads and one history read in that sample. Explicit detail still
returned product names/prices, and stock recall stayed **20** with unresolved moisturizer
availability. [Overview sequence](evidence/release-overview.json).

[Cloud readback](evidence/cloud-first-review.json) reconciled all 18 turns across the first
candidate and Cursor rehearsal: roots, successful main calls, tools, canonical usage and
private evaluation labels. This verifies execution accounting, not factual acceptance.

## A material failure retained

An earlier installed-profile journey incorrectly reported sunscreen stock as **0**, although
the connected catalog returned **20**. It corrected itself in a later follow-up. The run
completed, but its first briefing failed factual review.
[Actual replies](evidence/deployed-live.json) · [Source-to-answer review](evidence/deployed-review.json).

Previous controlled replays also showed unsupported format differences, an uncertain size
attached to a headline price and unrequested copy. Instruction changes improved some cases
without proving broad reliability. Product/variant facts must stay attached to their record;
unknown format is not evidence of a difference, and a successful page read does not prove
which size its price belongs to.

## Research architecture decision

The normal path is **Hermes native search and extraction**, followed by source comparison
and an Iris-written answer. Distinct searches run; an identical completed query in the same
turn returns its prior result, and a failed query can retry. There is no unread-page gate or
opening-wave quota. See [native contracts](TESTING.md#native-dispatch-and-cloud-readback).

The private investigation controller and LangGraph composition trials did not meet their
acceptance gates. Some exhausted the native call limit; repeated graph trials produced no
accepted reply and more work. They are retired from the shipped profile. Full trial artifacts
and the pre-publication repository snapshot are retained privately; their failures remain part
of this decision. A new research engine is not justified by those trials.

## Owner Telegram evidence

On 9 October, the owner asked the supplied-cost question and its EGP280 follow-up. Iris
answered **140.40** and **101.60**, a **38.80** difference; both are numerically correct for
unit cost160, packaging10 and fee3%. This verifies that exchange, not market intelligence.

On 10 October after the voice revision, “Hello iris” received a simple greeting (gateway
4.8s, one successful main call). “whats happening today iris” received a short shop-level
report (13.3s, four calls), distinguishing fresh Infinity readings from absent readings for
Likemoon, Source Beauty and Deoora. It used saved history, not new web research. Gateway
logs show final sends; these timings are backend measurements, not a measured user stopwatch.

## Observability evidence

[The earlier reconciled sample](evidence/run-summary.json) contains ten turns, 24 main calls
and 14 tools. [User labels](evidence/langfuse-users.json) establish operator/evaluation
attribution on two CLI probes. Subsequent Telegram replies exist; their Cloud attribution
has not been separately checked in that earlier sample.

[The retained retry](evidence/deployed-cloud-retry.json) has one ERROR generation with empty
usage and one successful completion with 11,208 canonical tokens. The reporting regression
now compares the completion to native `api_calls=1` and keeps the failed attempt visible.
No failed attempt is silently treated as free or as a completed billable call.
[Observability and limits](OBSERVABILITY.md).

## Release verification

The final six-turn run removed the fabricated owner URL and preserved stock **20** and private
memory. Its Infinity follow-up still reported a 40% moisturizer discount without reading
that specific listing; the initial brief also omitted the purchasable side of the stock
conflict. It does not pass the broad factual acceptance gate.
[Final sequence](evidence/release-final.json) · [Cloud execution reconciliation](evidence/cloud-release-final.json).
The current release's private conversation, native dispatch and Cloud readback are recorded
in [status](STATUS.md). Source/reply inspection remains required for acceptance; no automated
judge turns these cases into a blanket accuracy claim.

## Highest-value remaining proof

1. Record the multi-source demo in the actual interface; use its real trace and elapsed time.
2. Verify an isolated judge access route and time the run/setup; the owner bot stays restricted.
3. Measure one SME task against the manual workflow, including correction time.
4. Repeat the product/variant and availability cases when those instructions change.

These are evidence tasks for the submission, not a reason to add another architecture.
