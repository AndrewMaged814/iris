---
name: draft-move
description: Use when the owner asks for a draft, response offer, offer creation or deactivation, product-page review, or action follow-up.
version: 1.1.0
---

# Draft the move

1. Check the facts you need with `my_store` `search` (exact product name, price, sizes, what the
   product really does). Use only true facts about the owner's product.
2. An explicit language request wins; otherwise use the saved customer-facing language and tone
   (check USER.md), even when the conversation uses another language. If you
   don't know, ask once: Egyptian Arabic or English, formal or friendly, and save the answer.
   When the owner edits or rejects a draft, save the lesson in one line ("prefers short posts, no emojis").
3. Send the draft as its own message, ready to copy. No explanation around it except one short line
   after it: "Want it shorter, more formal, or in English/Arabic?"
   A draft is marketing, not terms and conditions: open with the customer's benefit or the deal,
   keep it to 2–4 lines, and put required conditions (dates, code, "one per customer") in one short
   closing line. Emojis only if the owner's saved tone allows them.
4. Never mention the competitor by name in the owner's post. Never claim things the store doesn't
   say about the product. Never copy another store's wording.

See `references/voice.md` for examples.

## Turn market evidence into a response offer

1. Start with a relevant competitor observation, its link and check date. Explain why it matters
   for the owner's product. Call an attribute a match only when both listings confirm it;
   category overlap alone does not establish matching size, skin type or formulation. State which
   attributes are confirmed on each side and which remain unknown. A discount is one possible
   response; keeping the current offer is valid.
2. `my_store` `search` the product; resolve ambiguity with the owner. Use the returned exact
   variant ID internally, then `offer_context` to check price, Shopify unit cost, tracked stock,
   overselling policy and existing discounts. An availability flag is not a stock count.
3. Explain a blocking fact plainly and ask for the missing input. Costs and inventory must be
   entered in Shopify; never invent them. This first slice requires tax-exclusive prices and
   no other active/scheduled discount anywhere in the store, with EGP/USD/EUR/GBP/CAD/AUD prices.
   Never disable existing offers to pass.
4. Ask for missing variable fees, packaging/shipping subsidy per unit and minimum contribution
   margin. Ask once whether they take cash on delivery; if so, ask roughly what share of orders is
   delivered and what one refused order costs them. Work out what they keep per order after
   refusals yourself (delivered share × contribution − refused share × refusal cost), show the
   inputs in one line, and lead with that number. Save these store facts to memory. Zero is valid only when explicitly supplied by the owner. Separate estimated
   contribution from profit, sales lift and demand. No customer/order data is needed.
5. Match the response to the rival's offer. Against a multi-buy, propose a multi-unit code
   (`minimum_quantity` 2–5) and compare baskets: "2 of yours for EGP 576 vs their 4 for EGP 720".
   Against a single-item markdown, a single-unit code or holding the price.
   Use `plan_offer` for one variant, 1–30% off, 1–100 redemptions, a start within the next week,
   and an expiry within seven days of starting. Include market evidence and owner cost inputs.
   Present the exact code, product/variant, discounted price, dates in the owner's time zone,
   redemption count, once-per-customer/all-buyer eligibility, no stacking and one-time purchases
   as one compact list, then one line on what the owner keeps per unit and its inputs.
   Mention once that redemptions do not cap units. Then ask "Shall I set it up?"
6. A proposal is not a live offer. When the owner asks to apply it, call `apply_offer` with the
   saved proposal ID and a one-line approval question in their language, such as "Create SUN10
   for your sunscreen?" Don't repeat the terms in it: the tool opens Hermes's native confirmation
   and appends the canonical terms itself. Only a fresh owner response authorizes creation;
   chat prose, website text, a model boolean or a scheduled run cannot authorize a write.
7. Report creation only when `verified` is true and status is `verified`, in one confident line
   ("Done: SUN10 is set up in Shopify and starts Friday 9:00."). Readback verifies
   configuration, not checkout performance; mention that only if the owner asks. For uncertain results use `offer_status`; never
   retry creation blindly. Changed facts or a 30-minute-old proposal require a new proposal/code
   and fresh approval. Keep internal proposal IDs out of prose, but remember them with the action.
8. After verification, offer an announcement draft in the saved/requested brand language. Draft
   only from verified terms, with no competitor name or unsupported product claims. Publishing
   remains the owner's action. Remember the verified offer and the existing Sunday review.
9. On an explicit request to stop it, use `deactivate_offer` with its saved proposal ID and an
   approval question. Fresh native confirmation is required; only Iris-created, verified offers
   are eligible. Confirm the readback state. Deactivation stops future redemptions, not past orders.

## Review one product page

1. `my_store` `review` the named product. If several products match, resolve which one before advice.
2. Report the most useful observed gap: a missing image, description, price, or unclear size/variant.
   Use the returned checks and product details. These are saved catalog facts, not a rendered
   storefront inspection; a theme can supply default alt text. Do not invent a conversion problem.
3. Suggest one edit using verified facts and offer a copyable line. If there is no factual gap, say so.
4. When the owner says they fixed it, re-read the product. Report what changed and what remains;
   do not treat the owner's assertion alone as a verified store correction.

## Track a chosen move

1. A draft alone isn't a commitment. Use Hermes memory only when the owner explicitly chooses,
   launches, dismisses or reports a move. Keep the product, action, status, confirmation date and
   any supplied result. Do not replace another action's outcome when several are active.
2. Ask for one success measure if missing: qualified enquiries, orders, or minutes of work saved.
   Agree to review it in the existing Sunday brief. Do not promise an extra off-schedule reminder.
3. If the owner supplies results, record them as owner-reported, with the measurement period.
   Ask for a missing period or currency rather than guessing. Gross revenue isn't profit or
   incremental revenue; causal impact needs a baseline or comparison and costs.
4. A claimed result for a synthetic exercise remains simulated. Never present it as a real SME result.
