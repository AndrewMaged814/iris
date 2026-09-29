---
name: weekly-brief
description: Use when writing "This week in your market", on the Sunday schedule or when the owner asks how the week went in their market.
version: 1.0.0
---

# This week in your market

## Inputs

- Scheduled run: the week's data is in your prompt. Your previous weekly message is also there;
  don't repeat what you already said unless it changed.
- Owner asks in chat: call `market_changes` with `week`.
- Always call `my_store` `summary` to connect findings to the owner's own products.

## Shape

1. One opening line: the week in one sentence.
2. Up to 3 items that pass the checklist in SOUL. Each: what changed (store, product, numbers, when)
   → what it means for the owner's products → one move.
3. One line on anything from the owner's screenshots, if it adds something.
4. End with one offer to draft the most useful move ("Want me to write the Instagram post?").

If nothing passes the checklist, send one line: the market was quiet, and where the owner sits on
price in their main product type.

If a store failed checks all week, mention it once in plain words.
