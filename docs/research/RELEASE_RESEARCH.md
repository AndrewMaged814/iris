# Iris release and demo research

Researched 2 October 2026. This note records primary sources supporting the next-release decision.
It is a planning artifact, not evidence that Iris has executed the proposed demo.

## Decision

Finish one continuous market-to-action story before adding another feature: Iris notices a
competitor offer, explains what it means for the owner's economics, prepares an appropriate
response, carries out one exact owner-requested connected-app write, verifies it, and remembers
what to review later. The improvement is completing and proving this existing workflow.

Preserve the owner's previously accepted flagship: a bounded response discount created in
Shopify through native Composio. A draft saved in Sheets could prove generic write/readback, but
is weaker than the accepted product outcome and should not silently replace it. The prior
[feature research](IRIS_FEATURE_PRIOR_ART.md) records this decision; its older implementation
claims about the removed bridge are historical, not current guarantees.

This is editorial judgment based on the existing product and proof gaps, not a researched
guarantee of audience reaction or a claim of market uniqueness.

## What the primary sources establish

| Source | Established capability | Consequence for Iris |
| --- | --- | --- |
| [Shopify Sidekick](https://help.shopify.com/en/manual/ai-powered-tools/sidekick) | Store-context assistance, content, tasks, third-party apps, personalization, voice and screen sharing | More integrations, voice, or memory alone will not establish a distinctive demo. These are already mainstream commerce-assistant capabilities. |
| [Sidekick Pulse](https://help.shopify.com/en/manual/ai-powered-tools/sidekick/pulse) | Proactive personalized recommendations based on store data, followed by tasks with approval before changes; currently described as early access for eligible merchants | Proactive insight plus action has prior art. Do not pitch Iris as the first agent to do it. Show a concrete, useful local merchant decision instead. |
| [Composio toolkits](https://docs.composio.dev/docs/toolkits) and [API overview](https://docs.composio.dev/reference) | Toolkits group app operations; agents discover operation schemas through meta tools. The overview advertises 1,000+ toolkits. | Say access to Composio's toolkit ecosystem; do not imply Iris has validated 1,000 integrations. A visible successful action demonstrates more than a connector count. |
| [Hermes scheduled tasks](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | Recurring and one-shot agent tasks can use skills and deliver to configured messaging targets | Reuse Hermes for proactive Telegram delivery and follow-up. No new Iris scheduler or notification subsystem is needed. Installed-version behavior still needs verification. |
| [Hermes memory](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) | Profile-scoped persistent memory and session recall; a verbal claim of remembering is not proof that a memory write occurred | Reuse native memory and verify recall in a fresh session. No new action database is justified just for this demo. |
| [Composio Shopify toolkit](https://docs.composio.dev/toolkits/shopify) | Lists discount-code creation/readback, price-rule operations and access-scope tools; explicitly says Composio-managed OAuth is unavailable | Discover the actual native connection requirements, schemas, permissions and supported exact terms before promising the offer demo. A catalog listing is not proof of an authenticated working operation. |

This is a focused comparison, not an exhaustive competitive survey. The sources do not establish
that Sidekick cannot do Iris's exact workflow, or that Iris has broader capabilities. Hermes
documentation describes upstream capabilities, not a verified guarantee for the installed version.

## Evidence in this repository

- [Product](../PRODUCT.md) already defines completion as observation, relevant comparison,
  requested draft or verified app action, and honest weekly review.
- [Demo](../DEMO.md) contains three useful but disconnected examples: competitor basket pricing,
  contribution math, and supported Egyptian Arabic copy. They are condensed business-case
  examples, not a continuous recorded interaction.
- [Status](../STATUS.md), updated 2 October, records native Composio Sheets discovery/reads,
  connected Reddit, and 59 offline tests. The catalog still needs owner confirmation in Telegram;
  no live write was tested. Simulated Telegram identity checks still need a second-account check.
- README still says 96 tests and four tools in its tree, while Status says 59 and three. Its next
  step still refers to an approved-create-stop offer flow after the dedicated bridge was removed.

## One 150–180 second demo

**Hook:** A cheaper sticker price can still lose to a competitor's basket offer—and blindly
cutting the price can cost the owner more than expected.

1. **0–20 seconds:** Open on a real Iris Telegram observation with a source and checked time.
   If the observation is replayed or a scheduled job manually triggered, label it. Do not invent
   a historical change without saved observations proving before/after.
2. **20–55 seconds:** Iris compares the relevant basket with the connected, owner-confirmed
   catalog. Existing sunscreen numbers are illustrative until freshly checked; preserve the
   promotion eligibility caveat. Show the source briefly, not tool traces.
3. **55–90 seconds:** The owner asks about a price cut. Iris explains its contribution tradeoff
   using confirmed cost inputs, without forecasting demand. Keep the existing 25.5% example
   only if its assumptions still match the demo catalog.
4. **90–145 seconds:** Iris proposes one economically feasible, product-specific response
   discount with exact value, eligible products, start/end times and usage limit. The owner
   requests those precise terms. Iris uses native Composio to create it and reads back the saved
   fields. Show the offer in the test store and a short accurate Egyptian Arabic announcement
   draft. The offer is a real checkout change, not an unpublished draft. If no feasible offer
   exists, respect that result rather than force a discount to fit the recording.
5. **145–175 seconds:** The owner asks Iris to remember the decision and what to review. Show
   verified fresh-session recall if time permits, or stop after the saved decision. Do not show
   fabricated future revenue or imply a week has passed without labeling a simulation.

The central payoff is that one agent connects external evidence, the owner's data, useful
judgment, native app execution and continuity in the same conversation. Egyptian Arabic is
part of serving this store, not a separate feature montage.

## Release gates and scope

First establish native Shopify connection and schema feasibility without rebuilding a client or
offer bridge. Before filming, confirm the demo catalog in Telegram; prove the exact offer
creation, readback and deactivation in a test store; repeat the complete sequence successfully;
and verify that blocked
pages, missing costs and failed writes produce honest responses. Review public visitor access
using the current Hermes controls before exposing the recording's connected demo environment.

Use one store, one product, one competitor comparison and one app write. Keep scheduling and
memory native. Exclude new dashboards, new providers, multi-owner onboarding, paid ads,
unsolicited messages, revenue attribution and custom approval/discount engines from this
release. Repository cleanup should follow the chosen demo path, preserving active tests,
fixtures and setup evidence while removing stale claims and obsolete artifacts.
