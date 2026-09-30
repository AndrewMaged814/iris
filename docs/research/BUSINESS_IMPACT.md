# Business impact: from market watching to an owner action

Research date: 2026-09-30. Primary sources only. Recommendations below are design
judgments, not verified Iris capabilities or proven revenue results.

## The problem worth solving

**An owner needs fewer things to check and a clearer next action, not another stream
of competitive alerts.** Iris can remove repeated public-market checking, explain
whether a change affects an actual product, and prepare an action the owner can use.
Revenue remains a hypothesis until an owner acts and measures the result.

There is evidence for time and skills constraints, but not for an Egypt-wide demand
claim. The OECD's 2025 D4SME survey reports lack of training time as a digitalisation
barrier for 39% of respondents; 51% of retail respondents prioritise digital marketing
and SEO skills. Its 1,009 respondents used digital platforms in ten OECD countries;
Egypt was absent and the authors explicitly warn that the sample is not representative
of all SMEs. These findings justify testing a low-effort workflow, not assuming local
adoption or estimating hours saved. [OECD policy highlights](https://www.oecd.org/content/dam/oecd/en/networks/oecd-digital-for-smes-global-initiative/D4SME-2025-Policy-Highlights.pdf/_jcr_content/renditions/original./D4SME-2025-Policy-Highlights.pdf),
[survey publication and country scope](https://www.oecd.org/en/publications/sme-digitalisation-for-competitiveness_197e3077-en.html).

Three concrete owner pains to validate in interviews and timed tasks:

- **Checking takes time:** visiting several stores, finding the relevant variant,
  reading promotion conditions, and remembering what was different last time.
- **A signal still leaves work:** deciding whether to react, protecting margin, and
  writing a credible Arabic post or customer reply.
- **Actions disappear into chat:** an idea is suggested, but nobody records whether
  it was used or helped. A better answer alone does not establish business impact.

These are hypotheses for Iris's small online-retailer audience. The sources below
demonstrate commercial workflow patterns, not prevalence among Egyptian merchants.

## What commercial products teach us

| Product and primary evidence | Transferable pattern | Boundary for Iris |
| --- | --- | --- |
| [Shopify Sidekick Pulse](https://help.shopify.com/en/manual/ai-powered-tools/sidekick/pulse) and [December 2025 announcement](https://changelog.shopify.com/posts/proactive-business-recommendations-from-sidekick) | Proactively surface a small set of recommendations; cite evidence; carry context into execution; learn from dismissals. Pulse help says changes require approval and eligibility includes recent sales activity. | Iris can carry a public-market finding into an owner-reviewed draft. It cannot infer sales performance from a product catalog or claim a recommendation increased revenue. |
| [Klaviyo Marketing Agent, September 2025](https://www.klaviyo.com/newsroom/marketing-agent), [Composer, June 2026](https://www.klaviyo.com/newsroom/CRM-agents), and [Composer audit guide](https://help.klaviyo.com/hc/en-us/articles/52308768764443) | Learn brand context, prioritise work, prepare useful campaign material, review results. Composer develops the earlier Marketing Agent approach. Its audit mode explains specific fixes and leaves the owner to apply them. | Adopt the preparation and review loop, not the CRM. Iris has no customer, campaign, order, or conversion data. Audit guidance is advisory even though separate creation capabilities can prepare drafts. |
| [Crayon Sparks](https://www.crayon.co/sparks) and [organisation workflow](https://www.crayon.co/product/organize) | Turn competitive evidence into usable deliverables; schedule recurring research; flag stale material; deliver where people work. | Borrow relevant-change-to-draft and freshness checks. Crayon's enterprise sales integrations and internal call data are outside Iris's retailer scope. Vendor testimonials and adoption numbers do not prove causal ROI. |

The common pattern is **evidence → prioritised action → useful deliverable → feedback**.
Scheduling alone is insufficient. None of these sources proves that adding an agent
to Iris's present catalog access will increase a merchant's sales.

## Three ranked additions within the existing architecture

Keep four tools and three business scripts. Use Hermes scheduling, memory, sessions,
vision, and Telegram delivery; keep every store connection read-only. Extend existing
data and skills only where a measured case needs it.

1. **One relevant opportunity, with an action ready to review.** Improve the existing
   daily/weekly workflow: connect a verified promotion, price move, stock change, or
   launch to a named owner product; explain match limits; recommend one feasible
   action; offer the corresponding draft. Quiet periods should stay quiet. A bundle
   stock-out is not a component shortage; an advertised offer is not a checkout price;
   a price cut needs costs and margin supplied by the owner. Use current watchlist,
   snapshots, product reads, and `draft-move`; no new notification subsystem.
   **Measure:** correct and relevant alerts, duplicates, owner acceptance, manual
   checking minutes, and time from alert to a usable draft.

2. **A focused product-page review.** On request, inspect one owner's product for
   factual gaps that an owner can fix: missing photo if image metadata is available,
   unclear size, missing currency, ambiguous variant or unsupported claim. Return
   the exact observed issue and a grounded suggested edit, rather than a generic SEO
   checklist. Re-read the product after the owner changes it. Extend `my_store` data
   only if required; do not edit Shopify or claim a missing field caused lost orders.
   **Measure:** owner-confirmed issues, useful edits accepted, review minutes saved,
   and verified corrections. Conversion impact needs separately supplied analytics.

3. **Close the loop on the owner's chosen action.** When the owner chooses a move,
   remember the product, action, date, and success measure; ask once in the existing
   weekly conversation whether it was done and what happened. Distinguish suggested,
   used, abandoned, and unknown. Avoid storing sensitive customer data or inventing
   outcomes; use Hermes memory and the existing weekly job before building a ledger.
   **Measure:** actions actually used and owner-reported time/outcomes. Revenue figures
   need a period, baseline, costs, and source; label them reported results, not causal
   uplift. A comparison or controlled test would provide stronger evidence.

## Positioning and proof

Recommended title: **Iris — your AI growth scout.**

Suggested hook: **She watches your competitors, spots opportunities for your products,
and helps you act in Arabic — right in Telegram.** “Growth” describes the intended
use, not a revenue guarantee. The concrete descriptor is an AI market intelligence
agent for small online retailers.

The repo should show one sourced alert, its associated owner product, the usable
Arabic draft, and the actual end-to-end evidence. Label simulated data and separate
implemented capabilities from proposed ones. Avoid “autonomous revenue agent,”
“finds lost sales,” or sales-growth percentages without corresponding evidence.

Definition of a successful pilot: an owner receives a correct relevant alert without
prompting, gets a usable draft, completes one chosen action, and records either
measured time saved or an honestly sourced business outcome. Telegram receipt must
be tested separately from isolated CLI replies. Testing a synthetic catalog can prove
the workflow; it cannot prove SME revenue impact.
