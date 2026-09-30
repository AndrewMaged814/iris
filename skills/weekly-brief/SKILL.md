---
name: weekly-brief
description: Use when the owner asks what changed this week, asks about market history, or when writing the Sunday weekly market brief.
version: 1.0.0
---

# This week in your market

## Inputs

- Scheduled run: the week's data is in your prompt. Your previous weekly message is also there;
  don't repeat what you already said unless it changed.
- Owner asks in chat: call `market_changes` with `week`.
- Always call `my_store` `summary` to connect findings to the owner's own products.
- Saved category price summaries may omit currency. Do not label them with the owner's currency
  or compare prices until the competitor's currency is confirmed.
- Check the observation coverage in `market_changes`. One snapshot establishes a baseline, not
  a quiet week. With limited history, say how many checks you have and that changes cannot yet
  be established. Keep today's listings separate from recorded changes.
  With fewer than two successful checks, stop after explaining the baseline and the next check;
  a weekly change question doesn't need a current price ranking or a marketing move.

## Shape

1. One opening line: the week in one sentence.
2. Up to 3 items that pass the checklist in SOUL. Each: what changed (store, product, numbers, when)
   → what it means for the owner's products → one move.
3. One line on anything from the owner's screenshots, if it adds something.
4. End with one offer to draft the most useful move ("Want me to write the Instagram post?").

If nothing passes the checklist, say no changes were recorded in the observed period. Call the
market quiet only when repeated checks support it. Today's listings, if the owner requests them,
are separate evidence and must retain their missing-currency and product-match limitations.

If a store failed checks all week, mention it once in plain words.
