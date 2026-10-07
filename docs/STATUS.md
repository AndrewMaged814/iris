# Status

## Current snapshot — 7 October 2026

- The owner's active goal is to substantially improve Iris's chance of winning the Agents at
  Work hackathon. The working cutoff is Friday 9 October around midday Cairo; the organizer's
  extended submission deadline is Saturday 10 October at 11:59 PM Cairo. Reassess dates before
  acting on this time-sensitive note.
- [Official judging guidance](https://ai.untap.us/) calls for a live agent a judge can run end
  to end and measurable SME impact through time saved, costs saved or revenue generated. The
  [program requirements](https://ai.untap.us/programs/aaw-1st-edition) include a repository and
  README a judge can run in under five minutes, impact slides and a 2–3 minute demo video.
  Criterion weights and the exact measurement method are not published. Treat projected impact
  as projected, not measured.
- Product direction remains open. A full market-signal → owner-specific decision → approved
  action → verified result workflow is a recommendation from the 7 October discussion, not an
  approved build plan. The owner has not yet answered whether to pursue that direction or whether
  Mira Nile can serve as a real SME impact pilot. Do not default to a discount feature.
- Iris is an owner-operated market analyst for selected competitor products. The live profile has
  five watched products and three active scheduled jobs. The daily and offer checks last ran on
  7 October; the weekly brief last ran on 4 October. All reported completion, which alone does
  not prove an owner received a useful alert.
- Native Composio reports active Apify, Google Sheets, Reddit and Shopify connections. A live
  read matched Mira Nile's 50 ml SPF 50 product in Shopify at EGP 320, with 20 available units
  and EGP 160 recorded item cost. A separate owner-confirmed Sheets catalog was not found.
  Connected-app writes have not been verified.
- The owner profile previously admitted public Telegram users despite an owner allowlist.
  `TELEGRAM_ALLOW_ALL_USERS` was set to `false` on 7 October; one owner ID remains configured.
  Hermes reads this access setting for each inbound turn. A second-account denial test is still
  needed. Prompt-based speaker identity is not an access control.
- No measured merchant outcomes have been recorded; published impact claims are estimates.
- The main repository passes 61 offline tests and the repository validator. The installed
  profile has not been updated from the repository's latest preparation commit. See
  [Testing](TESTING.md) for commands.

The dated sections below record earlier implementation and evaluation work. They are history,
not a current feature decision or proof of the installed profile's present behavior.

## Earlier updates — through 2 October 2026

Composio was authenticated through native Hermes MCP in the live Iris profile. Google Sheets
and Reddit were connected, and the owner reported Reddit reads working.

## Recommendation update — 2 October 2026

Deployed the shared Choose the response process in market-watch, linked from SOUL, response
offers and weekly briefs. Recommendations now explicitly compare holding course with feasible
responses, read only decision-relevant connected facts, account for stock/contribution/goal,
ask one direct question for a missing material input, and propose one measurable next step.
Replaced signal-to-action shortcuts that implied demand from competitor stockouts.

Four isolated native Luna cases used hypothetical supplied facts. The first candidate correctly
held price under scarce stock/thin contribution and suggested a bounded test with ample stock
and margin. Missing-stock advice initially stayed conditional instead of asking the count;
the simulated cron case unnecessarily discovered app tools. After tightening these branches,
both reruns used only skill reads: one asked the available count and withheld the promotion;
the other advised holding price, with EGP1.60 versus EGP40.40 contribution correctly calculated.
The bounded-test case calculated EGP111.60 per unit at EGP280, versus EGP150.40 at EGP320,
and three test sales to exceed two baseline sales on total contribution. No sales forecast.

Two baseline runs already gave sound economic choices. These samples support the intended
behavior and targeted correction, not a quantified improvement over the previous version.
Some answers exceed the usual 70-word target. Real connected-data joins, live recommendation
quality and the next scheduled Telegram message remain user/transport checks.

The deployment backed up runtime files, job definitions and session state. Updated the existing
daily job prompt without recreating jobs; all three identities, schedules and destinations were
preserved. Native prompt refresh retained 886 messages. Configuration, authorization files,
memories and the public-demo identity preamble were unchanged. The shared gateway restarted.
The offline suite remains 59 passing tests; repository validation passes. Evaluation prompts
are in the repository evaluator and instructions in [Testing](TESTING.md#recommendation-checks).

## Campaign evidence update — 2 October 2026

Deployed market-watch's evidence rules for store promotions and clearance. Store-level campaign
questions require current official campaign/collection evidence; product discounts, deep cuts
and old Black Friday URLs do not establish clearance. Replies retain unresolved price and
eligibility conflicts across follow-ups and use ordinary language with the scope checked.

Three isolated native Hermes cases passed manual answer/tool-trace review: ordinary promotions
were not classified as clearance, explicit discontinued-stock clearance retained its selected-item
limits, and a resumed follow-up did not turn a repeated disputed extraction into a confirmed price.
Only the skill was read; no connected-app calls or writes occurred. These supplied-fact checks
verify sampled reasoning, not live extraction accuracy or a semantic enforcement guarantee.

The skill-only rollout backed up the previous skill and session database, refreshed native prompt
state and preserved all 957 messages. Configuration, SOUL, memory, authorization, jobs and watch
storage were unchanged. The shared gateway restarted. All 59 offline tests and repository
validation pass. The next owner-initiated Telegram question remains the live workflow check.

## Current runtime

### Browser retry incident — 2 October 2026

The owner's 17:46 Cairo recommendation completed around 17:57 after two native browser failures
(about 95 seconds, then 334 seconds). The daemon remained unresponsive and its close commands
timed out; native navigation included retries. Telegram network errors were also logged. The
Composio calls were discovery, schema lookup, catalog/shop reads and a matched inventory-cost
read, rather than repeated attempts to execute one business action.

The prior instruction made browser verification too eager whenever extraction lacked freshness
metadata. Removed that instruction and temporarily removed the browser toolset from Iris's
Telegram configuration using Hermes's native toolset controls. Native web extraction, vision and
Composio remain available. For conflicting page evidence, one extra relevant extraction is the
limit; remaining uncertainty becomes the answer rather than URL/language/search retries. App
facts already read successfully are reused even if competitor research fails.

An isolated connected-data replay finished in about 42 seconds with no browser calls, using
one discovery and two app read batches. A supplied-fact conflict check finished in about 20
seconds and retained price/eligibility uncertainty. These timings are samples, not a latency
guarantee. Extraction can still return incomplete or different page versions; the precise origin
of the price disagreement and the browser daemon's resource failure remain unresolved. The
local browser is contained, not repaired. Rendered-layout questions currently need a screenshot.

Deployed with backups and native prompt refresh. All 932 messages, memories, OAuth and jobs
were preserved; the gateway restarted. Offline suite: 59 passing tests; repository validator
passes. No connected-app writes or owner-facing test messages were performed during the fix.

### Reading and display update — 2 October 2026

Own-product reads now explicitly use the confirmed app through native Composio. A successful
catalog read needs no public-storefront validation or citation fetch; missing attributes/links
are read through the app. Rendered-site review remains an explicit separate task. This addresses
the observed 29-second visit to a password page after successful inventory/cost reads.

Recommendations use a bold verdict, short evidence bullets and a separate next step. Native
Telegram progress is enabled with `all`, `accumulate`, argument preview length zero, and cleanup
after successful delivery. Config changes preserve the configured provider/model and other
settings. Runtime/state backups preceded rollout; 906 messages, memory, auth and jobs were
preserved. The gateway restarted and Telegram reconnected. Native display resolution was checked;
real progress rendering still needs the next user-initiated Telegram turn. Upstream pytest checks
could not run because pytest is absent from the installed Hermes environment.

A representative isolated connected-data replay took about 60 seconds, read product facts through
Composio, made no owner-storefront/browser visit, and returned the structured recommendation with
EGP320/EGP160/20 units, EGP360 competitor price and uncertain multi-buy eligibility. A separate
supplied-fact conflict case retained the EGP216-versus-EGP360 disagreement and withheld a discount.
The earlier candidate missed the multi-buy and formatting; the shared skill was tightened before
the final run. These observations do not establish a latency improvement or enforcement guarantee.

Fresh native Parallel extraction and a direct explicit-user-agent HTTP200 read agreed on EGP360
and an advertised buy-two-get-two offer. The earlier EGP216 extraction was cached at the request's
time, not an established old local-cache hit. Provider/page-version changes remain possible;
the precise origin of the older content is unproven. Conflict handling now requires fresh native
verification or an explicit unresolved result, without combining offers from different readings.
Neither a zeroed timer nor page advertising verifies checkout eligibility.

- App authorization, discovery, catalog reads and owner-requested writes use Composio directly.
  No custom Shopify client, token cache, catalog fallback, normalization adapter or offer bridge.
- Three Iris tools remain: `read_store`, `watchlist`, `market_changes`. They retain selected
  competitor product snapshots, history and deterministic change detection. Hermes supplies
  research, browser, memory, Telegram and scheduling.
- Setup asks where product facts live, reads the connected source and confirms field meanings.
  All three existing jobs refer to the confirmed connected catalog and read apps only.
- Composio reads and writes have no Iris action allowlist for this owner-authorized demo. The
  removed native discount confirmation and code-enforced margin/expiry rules are not guarantees
  of this version. Requested writes must be verified by readback; no live write was tested.

## Verification

- 59 offline tests and the repository validator pass. Tests for the removed Shopify transport
  and offer bridge were deleted; watch/history, delivery and profile isolation contracts remain.
- Native Composio dispatch discovered a real spreadsheet, read its metadata (four tabs) and
  five rows from a small range. No spreadsheet data was changed or saved as the owner's catalog.
- Five native Composio connection/discovery/execution tools are registered; no custom app tool.
  After a graceful gateway restart, native authentication still succeeds and Iris is served.
  The live doctor reports Ready, including the active competitor product read.
- Runtime, private settings and databases were backed up before deployment. Owner messages,
  memory, watch history, native OAuth and existing job identities were preserved. Watch storage
  counts match before/after: five rows, 20 snapshots and 40 signals (including retired watches).

## Public-demo identity — 2 October, superseded

At that time, the public Telegram profile was open, with shared connected-app reads and writes. The stale
claim of a native owner-only discount approval gate has been removed. Iris uses Hermes's native
plugin prompt section and task-local sender ID to identify the configured operator; display names
and typed claims do not establish operator identity. Visitors keep names/preferences in their chat.
Andrew's shared user memory records his known role as creator of Iris and Mira Nile demo operator.

Native concurrent-context checks distinguish owner and visitor, including a visitor named Andrew.
Isolated Luna sessions greet Andrew by name and role and ask a visitor what to call them; shared
USER.md remains unchanged. The gateway restarted successfully. These checks simulate Telegram
context and do not replace an actual second-account Telegram exchange. Public access was disabled
on 7 October; see the current snapshot above.

## Remaining proof

The owner still needs to confirm the catalog source and ambiguous field meanings in Telegram.
Read access does not verify every toolkit operation; discount create/readback/deactivation and
real write workflows remain untested. Unsupported app capabilities must be reported honestly.
