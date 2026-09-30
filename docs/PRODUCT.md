# Iris's promise

**Know what changed. Understand why it matters. Turn it into your next move.**

Iris is an AI growth scout for a Shopify store owner. She brings competitor intelligence,
product comparisons and useful drafts into the place the owner already talks: Telegram.
English and Egyptian Arabic are supported.

The next version completes that promise with an owner-approved response offer in Shopify.
Every action starts with relevant market evidence and a decision for the owner's products.
Standalone product-page editing is not the feature direction; a listing correction can support
a specific market response when the evidence calls for it.

## The owner journey

1. **Know the store.** Read the catalog and agree which competitors matter.
2. **Watch the market.** Check daily; establish a baseline and record relevant changes.
3. **Make a decision.** Connect the evidence to the owner's products and one feasible move.
4. **Make it usable.** Draft the caption or product line, or review a listing, when asked.
5. **Close the loop.** Remember the owner's chosen action; review the reported result in the weekly brief.

The installed version is read-only: the owner applies the action. Hermes supplies memory,
scheduling, vision and delivery. Approved Shopify offer creation is the planned extension;
it has not been implemented or granted access.

## What comes next

The next milestone is **one relevant market opportunity leading to one approved response offer
created and verified in Shopify, followed by an Arabic announcement draft and a remembered review.**

Start with one product-specific discount code, with an explicit value, start/end time and usage
limit. Check product costs, stock and existing offers before proposing it; missing facts need
owner input. Keeping the current offer is a valid decision. Review the exact terms in Telegram
before execution, then re-read Shopify to verify creation. Provide a way to deactivate the code.
Storefront content cannot authorize a write; scheduled discovery runs cannot execute offers.

Shopify's [code-discount API](https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeBasicCreate)
requires `write_discounts`. The installed connection has only `read_products`; additional access
and implementation are prerequisites. Read richer product/cost context first, then add the
bounded action using the existing Hermes and Iris architecture.

| What to learn | Evidence |
| --- | --- |
| Did Iris surface something useful? | Fresh competitor evidence, a relevant owner product and an accepted move |
| Did she save work? | Manual versus Iris-assisted time for the same task, with date and method |
| Was the action created and used? | Verified Shopify offer terms, owner confirmation and available outcome evidence |
| What happened afterward? | Owner-reported period and outcome; costs and a comparison before profit or uplift claims |
| Did the whole flow work? | Actual Telegram exchange, delivery and remembered follow-up |

Do not collect customer-level data for this pilot. Demo catalogs and simulated reports demonstrate
workflow behavior; they do not establish real sales impact. [Current proof](STATUS.md).

## Improve from the cases

Prioritize gaps that appear in owner conversations and [business evaluations](EVALUATION.md):
page-only promotion coverage, product and bundle matching, and dependable weekly action follow-up.
Keep four business tools and three business scripts; build on Hermes's existing capabilities.

Sales analytics, general store editing, base-price changes, automatic campaign publishing,
multi-buy/bundle creation and a broader CRM are outside this first slice.
Add new access only when the pilot needs it and the owner authorizes it.

[See Iris in action →](DEMO.md) · [Feature research](research/IRIS_FEATURE_PRIOR_ART.md) · [Business impact](research/BUSINESS_IMPACT.md)
