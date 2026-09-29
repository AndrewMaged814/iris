---
name: market-watch
description: Use when the owner sends a link or screenshot about another store, asks what competitors are doing, or a daily watch alert needs to be written.
version: 1.0.0
---

# Market watch

## A link from the owner

1. `read_store` the link. Use `focus` if the owner asked about a product type.
2. Look at the market picture by product type (`by_type`), promotions (`on_sale`), stock problems
   (`out_of_stock`) and the newest products.
3. Call `my_store` (`summary`, or `search` for one product type) to see what the owner sells in the
   same types.
4. Answer with what matters, using the checklist in SOUL. Offer to watch the store if it isn't watched yet.

## A screenshot from the owner

Read it yourself. Note the store, the products, prices, offer and wording you can actually see.
Say what you can't read. Save anything useful for the weekly message with `watchlist` `note`
(`name` = the store or page, `text` = what you saw, in one or two lines).

## A daily alert (scheduled run)

The facts from the daily check are in your prompt. For each urgent item:
- `sale_started`: what is on sale, the old and new price, and since when you saw it.
- `out_of_stock`: which item ran out at which store.
- `new_product`: what they launched and at what price.
- Stores listed as `unreachable`: say which store you couldn't open for 3 days; it may have moved.

Then check the owner's own products in that type with `my_store`, say what it could mean for them,
and offer one move (see `references/signals.md`). One message, at most 3 items.

## References

- `references/signals.md` — what each kind of change usually means, and matching moves.
- `references/methods.md` — reading a price picture by product type; telling trends from noise.
