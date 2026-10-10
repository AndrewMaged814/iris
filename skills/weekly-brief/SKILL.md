---
name: weekly-brief
description: Use when reviewing reported results of an owner's chosen action, answering market history questions, or writing the Sunday weekly market brief.
version: 1.3.0
---

# This week in your market

## Choose the branch

For a chosen-action result, go directly to Follow up on the owner's action below. Use the
owner's report and saved action/baseline already in memory. Fetch market or catalog facts only
when a changed fact is needed for the next decision. A result-only question has no market-history
or product-matching prerequisite. Simple changes in enquiries/orders are count differences;
market_math is for product quantities, prices and cost economics, not this count review.

For a market-history question or the scheduled Sunday market brief, use the market inputs
and shape below. A scheduled brief can also review a due chosen action from supplied memory.

## Market inputs

- Scheduled run: the week's data is in your prompt. Your previous weekly message is also there;
  don't repeat what you already said unless it changed.
- Owner asks about market history in chat: call `market_changes` with `week`.
- Use the saved Market profile's comparison keys and unit of measure; for a product match, read
  `../market-watch/references/categories.md` for the category.
- Read the confirmed connected catalog through Composio (setup skill),
  to connect findings to the owner's own products.
- Saved category price summaries may omit currency. Do not label them with the owner's currency
  or compare prices until the competitor's currency is confirmed.
- Use each store's evidence URL and local check date. A saved snapshot is not a fresh read.
- Check the observation coverage in `market_changes`. One snapshot establishes a baseline, not
  a quiet week. With limited history, say how many checks you have and that changes cannot yet
  be established. Keep today's listings separate from recorded changes.
  With fewer than two successful checks, stop after explaining the baseline and the next check;
  a weekly change question doesn't need a current price ranking or a marketing move. This does
  not prevent the separate owner-confirmed action follow-up below.
- Two or more checks cover their first-to-last interval, not automatically a whole week. State
  that interval when it is shorter than the requested period; do not call the entire week quiet.
- A short baseline with no recorded changes needs no category price list or invented next move.
  If a price list is requested, retain the source's category names: a broad accessories group
  doesn't establish that every product is a phone case.

## Follow up on the owner's action

- Read owner-confirmed moves from Hermes memory and the previous weekly message. Review one due
  action even when the market is quiet: was it used, and what happened to its agreed success measure?
- Suggested moves aren't commitments. If there are no confirmed actions, don't invent a task.
- Ask once; don't repeat an unanswered question from the previous weekly message unless the owner
  updated the action. An unknown outcome is unknown, not zero sales or a failed campaign.
- Apply SOUL's baseline requirement before judging the move. Compare equivalent periods and
  measures; report absolute changes before percentages when counts are small. Then choose one
  next decision: repeat, adjust, stop, or resolve a decisive missing fact. Base it on the owner's
  goal, observed results, known cost/effort and available stock. If no spending is authorized,
  do not scale spend. A small increase can support repeating a low-effort action for another
  comparable period; it does not establish causation or a successful campaign. Specify what
  will be measured next. A caveat about causality alone does not finish an action review.
- Keep owner-reported periods and simulated results explicit. Orders are not units: revenue
  needs known units/prices and is not profit. Scheduled runs cannot write memory; save action
  status and results only from the owner's chat report.
- In chat, record supplied results and any newly supplied baseline against the same chosen
  action in Hermes memory, with their period and owner-reported or simulated status. Keep a
  recommended next test separate from the owner's confirmed choice. Finish once the comparison,
  next decision and reported-result record are complete.

## Market brief shape

For new actionable market findings, use Choose the response in `../market-watch/SKILL.md`. Prioritize one
supported move across the findings, accounting for known chosen or dismissed actions. A quiet
week or thin history does not require a new campaign. Preserve the coverage limits above.

1. One opening line: the week in one sentence.
2. Up to 3 items that pass the checklist in SOUL. Each: what changed (store, product, numbers, when)
   → what it means for the owner's products → justified response or hold.
3. One line on anything from the owner's screenshots, if it adds something.
4. When reviewing a chosen action with an unknown result, end with its one agreed-measure
   question if it hasn't already been asked. Include source links for the findings; write a draft
   only when the owner asks.

If nothing passes the checklist, say no changes were recorded in the observed period. Call the
market quiet only when repeated checks support it. Today's listings, if the owner requests them,
are separate evidence and must retain their missing-currency and product-match limitations.

If a store failed checks all week, mention it once in plain words.
