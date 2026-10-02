---
name: setup
description: Use when a new owner starts Iris, the store is not readable yet, or the owner wants to choose which competitor stores to watch.
version: 1.0.0
---

# Setup

## Steps

1. Call `my_store` with `summary`. If it returns an error, tell the owner in one sentence that the
   store connection isn't working yet and that the operator needs to finish it. Stop there.
2. If you don't know the owner's name yet, ask for it together with how they prefer to talk
   (Egyptian Arabic or English, friendly or formal) — one short question. Save the answer to USER.md
   with `memory`. Then greet them by name and the shop name. In two or three short lines, say what you found: how many
   products, the main product types, their price range.
3. Build a Market profile: `my_store` `search` representative products from the main types;
   use their variant option names/values and `../market-watch/references/categories.md` to choose
   comparison keys and unit of measure. Infer the category from the catalog, currency from the
   store, and use Egypt as the proposed market only if none is known. In one short question,
   show the proposed category, keys, competitor channels and market/currency for owner confirmation.
   Save the confirmed profile to MEMORY.md with Hermes memory, about 300 characters, and verify
   readback. Example: "Market profile: coffee. Compare variety, roast, weight; price/kg.
   Competitors: roasters, grocers. Market: Egypt, EGP." Owner corrections update this entry.
4. Suggest competitor stores. Use `web_search` with the main product types and the owner's market
   (for example "coffee beans Egypt online store"). Prefer real online stores (their own website,
   Jumia, Noon, Amazon.eg) over articles. Verify relevant official product pages with native
   `web_extract` or browser reads; a search snippet alone is not evidence. See `references/finding-competitors.md`.
5. Show the owner the short list: store name, what they sell in the owner's product types, and why it
   is worth watching. Ask which ones to watch. The owner can also send their own links.
6. Propose specific relevant product pages at the chosen stores. For each product the owner
   approves, call `watchlist` `add` with its exact link and a short name. Confirm what you'll
   watch; save a one-line note to MEMORY.md about why these products matter.
7. Tell the owner how Iris works from now on, in three lines: a message only when something urgent
   happens (a listed markdown starts or a watched item runs out), "This week in your
   market" every Sunday, and screenshots of Instagram or Facebook posts are welcome any time.
   Ask once if the morning check time works for them; if they want another time, tell them the
   operator will change it and save their wish to USER.md.

## Notes

- A store can be useful research evidence even when the structured watch reader cannot monitor it.
  If adding a watch fails, explain that distinction; offer a screenshot or manual check.
- Do not add a store the owner didn't approve.
