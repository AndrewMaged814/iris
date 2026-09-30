# Business cases: expected versus actual

Manual review on 30 September 2026, with the installed Luna provider and native Hermes runtime.
These cases test whether Iris gives a useful, evidence-based answer; an attractive answer alone
doesn't establish business impact. The reusable prompts and expected criteria live in
[`tools/evaluate_iris.py`](../tools/evaluate_iris.py). Raw responses, tool evidence, timings and
configuration hashes stay in private operator reports because they can contain owner data.

Mira Nile's catalog and reported action results are synthetic. Public competitor reads are dated
observations. The oneshot evaluator sends no Telegram messages; scheduled delivery and continuity
are separate checks.

## Review matrix

| Case | Expected | Observed result and limit |
| --- | --- | --- |
| Known demo, Vitamin C match | Useful matches after acknowledging the demo once | Baseline repeated synthetic/demo labels and withheld practical advice; revised Luna reply gave matches and verified EGP prices without repeating the disclaimer |
| Vitamin C promotions and currency | Confirm currency, distinguish markdowns, multi-buy and bundles | All three watched collection feeds returned EGP with first-party metadata and matching product-price evidence; Luna separated offers and flagged conflicting stock evidence |
| Sunscreen position | Compare relevant packs and base prices versus offers | Improved offer separation and demo labels; some English pages did not expose confirmed pack size; advice remained generic |
| Exact product | Read that official product, including size and offers | Reader correction returned 50 ml, skin-type evidence, LE 360 and the advertised 2+2 offer; no checkout verification |
| Price cut | Check saved competitor and offers; account for unknown margin | Resolved saved URL and avoided an unsupported cut; demand and full formulation match unknown |
| Vitamin C match | Find a facial-serum equivalent or decline a verdict | Rejected underarm spray as a fair match and declined overpricing; calling it the closest match was still misleading |
| Stock opportunity | Comparable shortage, not bundle-component inference | Latest found no comparable recorded shortage; an earlier reply overinterpreted a sold-out bundle, so this remains a targeted regression case |
| Honest caption | Supported Egyptian Arabic copy | Produced a demo-labelled caption without invented benefits; an early isolated reply used the wrong gender of address |
| Weekly evidence | Stored changes, dated coverage and source; no invented trend | Latest gave two checks over 90 minutes in Cairo time, no week-long conclusion, no currency guess or face-only category assumption |
| Product review | Inspect real image metadata and find one factual gap | Read the existing image with native vision and found missing saved alt text; no conversion or rendered-layout claim |
| Planned action | Remember owner commitment, status and measure | Persisted a simulated, unpublished plan using native memory |
| Action follow-up | Recall plan in a new scheduled-toolset session | Recalled it and asked about drafting minutes; no invented outcome or memory write |
| Reported outcome | Retain source, period and arithmetic | Stored simulated three orders, EGP 960 gross sales and 15 reported minutes saved; rejected profit and causality claims |
| Action results | Recall result without asking again | Recalled source/period and kept attribution and profit unknown |
| Bulk-offer position | Compare one versus four bottles before a cheaper claim | EGP 360 single; advertised four for EGP 720 if eligible, versus EGP 1280 for four demo Mira bottles; rejected the broad claim and retained size/checkout limits |
| Margin break-even | Contribution arithmetic, not price-drop arithmetic | EGP 100.40 → 80.03 contribution, EGP 20.37 loss and about 25.5% extra units needed; assumptions retained, no extra demand inferred |
| Unsupported ad claims | Reject unproven claims while still drafting | Excluded waterproof, baby safety, dermatologist approval and universal cheaper wording; supplied a short Arabic draft using supported demo facts |

## Small changes driven by failures

- Exact product links now return the requested product and bounded page evidence rather than the
  entire catalog. This uncovered advertised promotions missed by the catalog feed.
- Shared history adds observation coverage, source URLs, currencies and local dates. Thin history
  no longer needs a generic price ranking or an invented move.
- Read-only product review exposes images and missing metadata instead of requesting a screenshot
  for information already in Shopify.
- Owner-confirmed actions use native Hermes memory and the existing weekly brief. Suggested moves
  aren't commitments, and reported gross sales aren't profit or attributed uplift.
- Daily facts stay pending until native delivery evidence confirms the business answer arrived.
  Failed generation and delivery no longer consume the alert before it can be retried.
- Native Hermes delivery mirroring carries scheduled reports into the owner's chat context;
  weekly instructions distinguish a chosen-action question from a generic draft offer.
- Routine comparisons retain demo provenance internally after the owner knows it. Material
  publishing and simulated-result caveats remain; the tested ad reply put its caveat outside the draft.
- Existing conversations restore a frozen Hermes system prompt. Updating SOUL alone does not
  update those sessions: deployments must refresh the stored prompt through native session storage
  and evict the running agent cache while retaining the conversation and owner memory.
- Shopify feed currency requires store metadata plus one first-party product page agreeing on
  price and currency. Collection and localized links are covered. Missing or conflicting evidence
  leaves currency unknown without losing the readable catalog; historical snapshots are not relabeled.

## Reliability evidence and limits

Two deterministic regressions reproduced alerts being consumed before generation or delivery,
including the three-failed-check store warning. Eleven isolated native scheduler runs then covered
model failure, transport failure, retry and subsequent quiet checks. The script subprocess and
execution ledger were real; model and send boundaries were simulated. A delivered error notice
did not acknowledge the business facts. Offline tests also cover deferred queue delivery,
uncertainty, ambiguous worker correlation and receipts surviving queue pruning.

Unknown sends are held for investigation rather than blindly replayed. If Hermes removes a
receipt before Iris reconciles it, delivery can't be inferred. Compatibility of native ledger
schemas and direct script parent-worker correlation must be rechecked after runtime upgrades.
This is evidence of the tested recovery paths, not an exactly-once transport guarantee.

The native weekly continuity check used two actual Luna scheduled turns before and two after
the instruction adjustment, in a private profile with local output only. Previous output was
injected on the second run. The latest pair kept the plan and unknown measure, and omitted the
generic draft offer. It also omitted the intended first measure question: follow-up wording is
still a partial result. This doesn't establish long-term retention or a complete updated
Telegram action conversation.

The live weekly report was confirmed delivered at 04:27 Cairo, and the updated daily check
completed quietly at 08:00. Explicit Telegram destinations require per-job `attach_to_session`
as well as the native mirroring configuration. Both existing jobs now qualify. Hermes mirrored
the already-delivered weekly text into the active owner transcript without resending a message;
this is a verified backfill, not a fabricated owner turn or a test of the next scheduled send.

Real-owner adoption, measured time saving and revenue impact remain unverified. A useful next
pilot is one merchant choosing one action, reporting whether it was used and measuring the
agreed task time or business result. [Current deployment evidence](STATUS.md).
