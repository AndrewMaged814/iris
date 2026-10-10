---
name: market-watch
description: Use when preparing market briefings, investigating competitors, comparing products, recommending a market response, or writing product-watch alerts.
version: 1.8.10
---

# Market watch

Use Hermes web search, extraction and vision to answer the question or identify a precise remaining dependency.
Use the saved Market profile and confirmed catalog (setup skill); comparisons use `references/categories.md` for keys/units.

## Research workflow

Select the path before reads:
- Market briefing across products/businesses: read `references/briefings.md`; complete the
  requested market picture before choosing a response. Reuse this branch for briefing follow-ups.
- Owner-proposed discount: use own price, cost, fees, stock and floor in Choose the response.
  Competitor research is needed only if the owner asks for it or a named comparison needs it.
- Price/offer comparison: read the named product and own facts, then resolve material size/terms.
- Why/history: read recorded observations and official explanations/campaign evidence.
  Read `references/motives.md` before those calls for this question's evidence and stopping rules.
- Supplied observation or follow-up: reuse it; read only a missing fact that changes the answer.

1. Define the question and the fact that could change its answer before selecting a tool.
   Missing fields unrelated to that answer need no investigation or caveat. Assess relevance from
   known titles, descriptions and explicit owner facts. A confirmed material format difference makes
   an alternative, even with equal size/SPF; state it first. A difference needs evidence for both
   products' formats; one unspecified format stays unknown. Fetch
   size/terms only if they could change the answer; the next pricing step follows the format verdict.
   A generic category or formulation word on an image does not erase an explicit applicator,
   model or variant stated in the title/description. Keep these attributes separate on follow-up.
2. Start with supplied or watched exact URLs and the confirmed connected app. Reuse fresh facts
   already read or explicitly confirmed by the owner unless a recheck is requested or facts are stale.
   Reuse decoded screenshot facts; read the image for a missing detail. Fetch a website only
   for a named remaining gap, using an observed URL or discovery search to find it.
   Read apps for missing material facts or a requested recheck; independent needed reads may run together.
3. Read the owner's relevant products. Search for the competing products and open the pages
   that can answer the question. Independent searches may run together, including another
   look at a site you have already found. Then compare those pages with the owner's catalog
   and answer. Stop searching once that comparison is supported. An identical query is skipped
   because its result is already in the turn; use it, or search for a different fact.
   A sunscreen collection does not answer a moisturizer question. For a requested number of
   comparators, stop when that many useful listings are read. Recover an explicitly truncated
   needed field once before replacing the source.

| Observation | Next useful tool or action |
| --- | --- |
| Exact page known | `web_extract`; reuse its price, description, links and terms together |
| Needed size/model missing from text; official product image linked | `vision_analyze` for that specific fact; report what is pictured |
| Multiple sizes but price is not joined to the selected size | Try `read_store` once for structured evidence; if still unjoined, ask for a selected-size screenshot; skip preview-price searches |
| Confirmed material format difference already answers direct-match question | Explain the alternative; do not fetch size just to restate the mismatch |
| Terms missing; relevant official campaign/policy link found | Extract that link, preserving selected-product, quantity and expiry conditions |
| Relevant source still unknown | Search for the exact product/domain and missing fact, using neutral wording rather than assuming an offer exists |
| Response explicitly truncated | Increase the budget once; complete below-limit results need no repeat |
| Partial/failed read | Try one available materially different method/source for the gap; inspect its result, not another paraphrase of the same search |
| Payable basket needs interaction | Use a working permitted native capability if available; otherwise leave application unverified |

4. Check relevance first, then apply SOUL's size→price and offer→basket checks to comparisons
   that need them. Resolve only gaps that could change this answer. If a requested same-size
   or normalized-price comparison needs a size absent from text and an official label is linked,
   call native vision for that size. Do not introduce an unknown-size caveat to reopen a settled
   format question. For multiple variants, join the price to the selected size;
   a size in a URL or a table of all sizes does not identify which variant owns a headline price.
   If needed terms have an official link, read that link. Reuse a complete below-limit extraction.
   Update facts and gaps after each result. New wording, repeated snippets and an unchanged page
   are not new evidence. After two equivalent attempts, switch to a suitable untried method/source
   or report the dependency. Stop when material facts suffice or permitted relevant routes are
   exhausted. State unknown after the suitable route was tried or is unavailable; inaccessible checkout stays unverified.
5. Verify claims: search results are leads, images prove pictured labels. Cite the source/date.
   Local browsing is unavailable; don't promise interaction or retry it. Use native vision for
   linked images/screenshots. Unclear text stays unknown; report blocks.

Compare relevant product forms, size/model/condition and confirmed currencies; keep marketplace prices separate
from official-store prices. Account for every advertised exact-product promotion before a price
verdict. Keep single-item and multi-buy comparisons separate, retain conditions and show relevant
basket math. For a bundle, distinguish what the shopper pays upfront from the amount received
and the price per unit. Evaluate each plausible advertised total on both axes. If disputed
totals fall on opposite sides of the owner's basket, do not say the rival costs more (or less)
upfront: state both conditional differences and withhold that verdict. A lower conditional
price per unit can still be reported without calling the whole purchase a verified better deal.
A zeroed timer does not establish active/expired status. Never combine an old
discount with a newer multi-buy or infer checkout eligibility, demand, profit or sales uplift.
Associate price, availability and offer text with the target product section. Related-product
cards, page footers and a missing sold-out label do not establish the target's stock status.
Call availability verified only when explicit evidence identifies that product; otherwise say listed.
When a page read fails, a product name in a supplied URL is a lead, not a freshly verified
title, description or current offer. Attribute any such provisional identification to the
supplied link. If verifying it is needed for the answer, try one materially different suitable
read; otherwise give the supported partial answer and the access limit. A "checked today"
date must not imply that failed-page facts were freshly observed.
If evidence conflicts, allow at most one materially different read for the disputed field;
then retain unresolved conflicts. Advice needs the owner's request or SOUL's alert checklist.

Group rivals by own product and confirmed size/model; give one numeric range/difference, offers and their relevance.
Separate nonmatching variants and conditional baskets; state source scope. Include the decisive price numbers.
Use `market_math`: compare_products takes own reference plus separately named rival rows with their own sizes.
Use compare_baskets for one basket's disputed totals; unit_economics for sourced costs/periods. Reuse results.
Missing costs stay unknown. Search/discovery find evidence, not arithmetic. A discount alone does not establish its expiry.

## Match claims to evidence
Answer at the width the owner asked. A casual market question starts with one short line per
shop. A requested detailed briefing, comparison or numbers includes relevant products and prices,
even without naming a shop or product. Pages on one shop are one competitor.
For the casual overview, read saved market history; no own-catalog read is needed unless the
question asks for a comparison or decision that depends on it. State missing current readings.
Compare the owner's products with what the history covers; one followed
product is not the whole store. Read a named collection before counting its offers. Say what
"best" means; lowest price means cheapest unless that was the question.
For a store-level campaign
question, read the official current offers/collection page or campaign announcement; product
pages supply examples, not proof of a store-wide event. Search snippets and old campaign URL
names are leads only. Reuse relevant evidence already read; use the bounded extraction rule
above for disputes rather than restarting research on each follow-up.

Call an event clearance only when current retailer wording explicitly identifies it (such as
تصفية) or explains a stock-clearing purpose. Discount depth and a Black Friday URL do
not establish clearance. Preserve limits such as selected products or an uncertain end date.
Without that evidence, say you found promotions but no confirmed clearance on the pages
checked. Do not lead with "yes" and then withdraw the claim in a caveat; avoid "clearance-like"
and use ordinary "discounts" rather than retail jargon such as "markdowns" in owner replies.
When reads fail, attribute search evidence to search results; the linked page was not verified.
Recover a relevant first-party page once through a different useful route before giving up.

Carry unresolved price, timing and eligibility conflicts into follow-ups. A repeated extraction
of the same disputed price is not independent confirmation. Resolve a conflict only when new
evidence explains it or establishes the applicable terms; otherwise omit the disputed number
if unnecessary, or state its uncertainty. A narrower follow-up does not reset what is unknown.

## Choose the response

Use this process for advice; factual questions need only their answer. Hypothetical exercises
use supplied facts, stay separate from the live catalog, and are not real chosen actions.

1. Establish the decision: what changed, which own product it affects, and the owner's known
   goal or constraint. Distinguish a current listing from a recorded change. Read the source
   before treating a promotion or shortage as an opportunity; use `references/signals.md`.
2. Read only the business facts that could change this decision through native Composio.
   Start with the confirmed catalog and exact variant. Check available stock before suggesting
   promotion; check unit cost, variable costs and the owner's contribution floor before a
   discount. Reuse fresh facts already read this turn. Discover schemas and verify the account,
   product identity, currency, units and time period before joining facts across apps.
   An availability flag is not a quantity. Read bounded, product-level sales aggregates only
   when they are needed to judge sales pace or an outcome and the owner has identified the source.
   Avoid customer records. No source or permission means unknown, not zero. Do not search every
   connected app or require sales analytics for a decision that stock and costs already settle.
   Discover the needed app operations once per task and reuse their schemas/session.
   Read setup's focused-read rules before app reads; discover a bounded read for needed fields together.
   Reuse successful catalog/cost reads even if competitor research fails. Stop retries on denied
   permission; report the missing fact instead. A correctable schema error permits one correction.
   For break-even sales, compare the same period and price mix; a weekly baseline does not establish
   usual weekend sales. A whole-period calculation using the weekly figure must be conditional on
   all those units receiving the discount. Ask for normal sales during the actual offer period;
   do not turn that calculation into a weekend target or predict the extra demand.
3. Compare holding course with at most two feasible responses to this finding. Depending on
   the evidence, these can be accurate positioning, fixing a specific listing gap, featuring an
   available alternative, or a bounded offer. A caption is an execution artifact, not a reason
   to act. A competitor's move alone is not a reason to discount. Check the same constraints for
   an alternative product; do not merely move a weak recommendation to a different SKU.
   Recommend a listing fix only for an observed listing gap. Do not invent busywork to accompany a hold.
4. Choose one response by evidence strength, fit with the owner's goal, stock, contribution,
   effort and timing. Explain the decisive tradeoff in ordinary words, not scores or invented
   revenue estimates. A shortage does not establish transferred demand; stock alone does not
   establish slow sales. Say to hold course when no response has a supported advantage.
   Compare price minus unit cost before unknown other costs. A smaller remainder alone cannot
   establish an unacceptable margin: ask for other variable costs and the minimum to keep.
   Use that question as the next step when it is the reason for holding a price response.
   Resolve obtainable public facts first. If one missing fact could reverse the choice, end with
   one direct question for it and stop before proposing the affected action. For a stock-limited promotion
   with only an availability flag, ask how many units can be allocated; a conditional promotion
   or a price formula does not resolve the missing count. In scheduled checks, state that dependency only when the new
   finding warrants attention; otherwise follow the quiet-check rules. Do not invent a safe
   discount, a stock quantity or a margin floor to complete a recommendation.
5. Format recommendations as a bold verdict on its own line, up to two short evidence bullets,
   and a separate next-step line, with source/date at the end. Explain the fact that makes the chosen
   move preferable to the obvious alternative. Give one small next step and a proposed measure for a
   new action. Aim for 90 words for focused advice; a briefing uses its requested grouped findings.
   State the scope checked, not the best opportunity across the business. Lead with one priority.
   Check verdict, reason and next step together: a hold for missing costs needs cost/floor
   confirmation; an uncertain basket needs basket verification; a test needs its review measure.
   Keep the next step on that dependency; use a timed recheck only when timing could resolve it.
6. Keep recommendation, owner choice, execution and measured result separate. Read the
   `draft-move` skill when the owner requests a draft or app action; discover the actual operation
   before promising it. A recommendation authorizes no write. Honor known dismissed/planned
   moves from memory or the previous report; repeat only if new evidence changes the decision.

## Product watches
Use `watchlist` for approved links, `market_changes` for history and Hermes for research.
`read_store` reads one product's structured price/stock and can resolve a variant gap; it does
not crawl stores or prove checkout terms. A manual native read may still help when monitoring
fails. Monitoring covers selected products; report blocks honestly, without challenge bypass.

## Scheduled checks
Daily price/stock facts arrive from the pre-run script. A missing observation does not prove a quiet market. Apply Choose the response before calling a change urgent. Lead with one priority. A justified hold is valid. If a script-triggered change needs no action, say why; do not claim nothing changed. Report monitoring failures separately from business advice.

For the morning offer check, read the watched product pages with native `web_extract`.
Compare advertised offers with the previous report. If nothing new matters, reply exactly
`[SILENT]`. Otherwise give one sourced alert with conditions, matching product and basket math.
Scheduled runs cannot write owner memory or execute store offers.
