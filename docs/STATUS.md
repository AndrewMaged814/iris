# Current status

**10 October 2026.** This is the current verification record, not a development diary.
Iris is an **AI market watcher**: competitor activity, market research and store context
connected into investigations, priorities, drafts and remembered decisions in Telegram.

## Release preparation

- Hermes, **Luna** and native Composio remain the stack. No new research engine or paid reviewer.
- Distribution **1.2.0** / Iris plugin **1.3.1**; the rejected investigation controller and graph trials
  are removed from the shipped profile. Four Iris tools remain.
- Market-watch **1.8.10** distinguishes casual overviews from requested detailed briefings,
  avoids irrelevant own-catalog reads, binds stock to its exact product/variant, and checks
  cited facts against successful reads. Null catalog public URLs stay null in follow-up footers.
- The Cloud checker separates failed attempts from successful model completions and retains
  unknown failure usage. Native token/user-label checks pass on the pinned Hermes runtime.
- **116 offline tests pass**, with no skips. Repository validation and whitespace checks pass.
  The existing GitHub Actions workflow runs the suite, validator and shell syntax check.
- README, architecture, setup, demo plan and evidence/observability guides are consolidated.
  Obsolete planning diaries, rejected engines, repeated trial exports and old video/slide
  drafts are archived privately. Earlier material failures remain in public evidence.

### README and evidence review

The README now leads with owner time, cost and revenue opportunities using owner-approved
wording. The hypothetical morning story and repeated benefit section are removed; the
headline, product promise and distribution description use **Your AI market watcher**.
Telegram remains documented as the tested conversation channel. The owner confirmed they
have not yet used a recommendation; no measured savings or income are claimed.

Operator exports now flag cited URLs without a captured read in that conversation and
distinguish page text from structured product data. New native traces label failed, empty
and content-returned extracts. Four regression checks include the retained unread promotion
citation, failed reads, variant queries and fresh-session boundaries. Re-exporting the final
journey preserves its original replies, timings and counts and flags the unread moisturizer
URL. This improves review visibility; it does **not** repair the agent's answer. No runtime
behavior or live profile was changed in this follow-up.

The private production plan defines a paired task
comparison including source checking and correction time. Controlled demo trials, merchant
outcomes and hypothetical revenue opportunities have separate labels.

The public README now uses generic competitor examples, explains the Composio authorization
flow, and presents the Langfuse integration as an **observability layer**. The architecture
SVG and PNG use the same wording. The production storyboard and measurement worksheet are
preserved outside the public repository; public links to the internal plan are removed.
The two pinned-runtime tracing patches remain documented under `patches/`; their token and
owner/evaluation user-label checks still pass on the tested Hermes installation.

## What has been observed

The latest Cursor six-turn native rehearsal retains sunscreen inventory **20**, moisturizer
inventory **0/purchasable** conflict, unknown owner format, campaign uncertainty, requested drafting
and fresh-session memory. [Record and critique](EVALUATION.md#latest-cursor-rehearsal).

The release overview rehearsal keeps casual history reads separate from an explicitly
requested detailed price briefing. Its casual answer used two skill reads and one history
read, taking 15.07s including CLI startup. Product facts persisted across follow-ups; the
moisturizer was not declared definitely sold out. The CLI speaker lacked trusted Telegram
identity, so Iris asked its name rather than assuming Andrew. [Sequence](evidence/release-overview.json).

The first release broad rehearsal failed source review: one search-only competitor price and
an unsupported shared strategy. The next preserved read-source coverage but invented an own
storefront URL in a later footer. Both are retained; neither is counted as a factual pass.
[Evidence ledger](EVALUATION.md#publication-candidate-first-factual-check-failed).
The final native journey completed all six turns. Its first reply took 106.67s, with 12 main
calls, eight searches and 26 tool requests; the Infinity follow-up took 63.06s. Stock20, the
missing owner URL, requested drafting and fresh recall were retained. However, the follow-up
claimed a moisturizer discount from an unread listing, and the initial brief did not explain
the purchasable flag behind the stock conflict. Broad briefing reliability remains **open**;
this is a completed rehearsal, not a factual acceptance pass.
[Final replies and call path](evidence/release-final.json).

Cloud readback reconciled 18 turns across the first candidate and Cursor rehearsal, including
successful main calls, tool counts, roots, canonical totals and evaluation labels.
[Readback](evidence/cloud-first-review.json). Actual provider charges and complete auxiliary
usage remain unknown. These are private CLI evaluations, not delivered Telegram journeys. The final overview and
broad journey also reconcile: 12 turns across three sessions, with all root/completion/tool
counts, canonical totals and evaluation labels matching.
[Final Cloud readback](evidence/cloud-release-final.json).

## Live profile updated

Updated at **15:28 Cairo on 10 October**. The 24 distribution-owned runtime files match the
release bundle hashes. Backup: `~/iris-backups/publish-runtime-20261010T122821Z`.
Configuration, environment, OAuth, memory and job files were unchanged; the owner database
remained 86 sessions/1,653 messages through deployment and verification. The retired
controller file and its bytecode were removed after backup.

The existing shared gateway restarted successfully and is active as PID 428439. The profile
doctor passes, owner-only access remains configured, native tool discovery/dispatch passes,
and completed-result reuse plus failed-search retry still work. Luna's configuration is
preserved. Native Composio OAuth connectivity passes after restart; the server discovers
11 tools and the profile restricts the exposed Connect inventory to its five selected tools. [Deployment readback](evidence/deployment.json).

Earlier actual owner greetings and a casual market overview after the voice revision are
recorded: 4.8s/one main call and 13.3s/four calls. Gateway logs show final sends. Those are
backend timings, and they predate this release. A new broad owner Telegram journey and its
trace still need verification. [Telegram evidence](EVALUATION.md#owner-telegram-evidence).

## Needs attention

- **Broad-briefing grounding:** remaining unsupported promotion claims show that prompt
  changes alone have not established reliability. Keep the source-to-claim review, and use
  the retained failures to design the next focused correction before calling the demo accepted.
- **Efficiency and brevity:** some research repeats and briefings exceed the requested length.
  A shorter sample is not a guaranteed latency improvement; no search gate was reintroduced.
- **Live verification:** a new broad owner Telegram journey, complete auxiliary/cost accounting
  and connected-app writes remain unverified. Quiet watch checks cover selected pages only.

## Submission work still requiring evidence

1. Record the **2–3 minute working demo**: market briefing, competitor investigation,
   store priority, requested copy and fresh-session recall.
2. Verify a separate judge run/access route and time it; the owner bot stays restricted.
3. Measure a real SME workflow against the manual task, including correction time, then
   prepare the impact slides. No verified time/cost/revenue improvement is claimed.
4. Check the registered participant's submission round and upload the required artifacts.

The organizer homepage was rechecked at15:16 Cairo: deadline remains **10 October, 11:59 PM
Cairo**. Portal availability and successful submission are unverified.
[Official requirements](HACKATHON_RULES.md).

## Product priorities after the submission

Stronger cross-competitor product grouping, richer campaign/catalog/policy history,
repeatable source interpretation and measured owner outcomes. These are next steps, not
features already delivered. [Product promise](PRODUCT.md) · [Testing](TESTING.md) ·
[Observability](OBSERVABILITY.md).
