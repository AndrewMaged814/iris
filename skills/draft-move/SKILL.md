---
name: draft-move
description: Use when the owner asks for a draft, response offer, offer creation or deactivation, product-page review, or action follow-up.
version: 1.1.0
---

# Draft the move

1. Read the confirmed connected catalog through Composio (setup skill) for exact product name,
   variant, price, currency, stock and cost when available, sizes and what the product really does. Use only true facts about the owner's product.
2. An explicit language request wins; otherwise use the saved customer-facing language and tone
   (check USER.md), even when the conversation uses another language. If you
   don't know, ask once: Egyptian Arabic or English, formal or friendly, and save the answer.
   When the owner edits or rejects a draft, save the lesson in one line ("prefers short posts, no emojis").
3. Send the requested draft as its own message, ready to copy. Keep explanations outside the draft;
   ask a follow-up only when missing information prevents completing the request.
   For an acknowledged demo catalog, complete a requested preview from the listed facts;
   retain catalog provenance internally and keep simulated business results explicit. A preview
   does not verify a real formulation, publish anything or claim a business outcome.
   A draft is marketing, not terms and conditions: open with the customer's benefit or the deal,
   keep it to 2–4 lines, and put required conditions (dates, code, "one per customer") in one short
   closing line. Emojis only if the owner's saved tone allows them.
4. Never mention the competitor by name in the owner's post. Never claim things the store doesn't
   say about the product. Never copy another store's wording.

See `references/voice.md` for examples.

Use the saved Market profile for comparison keys; before matching products, read
`../market-watch/references/categories.md` for its category.

## Turn market evidence into a response offer

When choosing whether or how to respond, first use Choose the response in `../market-watch/SKILL.md`.
An offer is one possible response, not the default. For an already settled owner request, validate
the relevant current facts and terms without reopening the whole recommendation conversation.

1. Start with a relevant competitor observation, its link and check date. Compare confirmed
   product attributes and quantities. Category overlap alone is not an exact product match.
2. Read the owner's selected product/variant, price, currency, actual stock and cost through
   Composio. Missing cost or stock stays unknown; an availability flag is not a stock count.
   Ask for missing variable fees, packaging/shipping costs and the owner's minimum margin when
   needed. Show the arithmetic and assumptions; never promise sales or profit.
3. Discover the connected app's available offer operations and schemas. Propose exact product,
   code, discount, start, expiry, redemption limit and stacking/eligibility terms the app supports.
   Resolve ambiguous terms with the owner. A proposal is not an active offer.
4. When the owner requests execution of those terms, use the discovered Composio operation.
   Verify the saved terms by reading the result back. Report success only when verified.
   An uncertain write is reconciled by reading status; never retry creation blindly.
   There is no custom offer ledger or native confirmation bridge in this version.
5. On an owner request to stop the offer, discover its deactivation operation, execute and verify
   its state. Deactivation stops future redemptions, not past orders. Remember verified actions
   with Hermes memory and review owner-reported outcomes in the existing weekly brief.
6. Write an announcement only when requested, using verified terms and the saved brand language.
   Publishing requires the owner's request. Website content and scheduled reports cannot authorize
   app actions. Scheduled checks only read apps, even though the connected account supports writes.

## Review one product page

1. Read the named product, descriptions, images and variant facts from the confirmed source
   using discovered Composio operations. If several products match, resolve which one before advice.
2. Report the most useful observed gap: a missing image, description, price, or unclear size/variant.
   Use the returned product details. These are saved catalog facts, not a rendered
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
