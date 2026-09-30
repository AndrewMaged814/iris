# Iris feature prior art

Research date: **30 September 2026**. Purpose: choose a memorable next Iris workflow without expanding into a general commerce platform. This file records primary-source product documentation and vendor claims; it does not establish effectiveness, customer demand or uniqueness.

## What already exists

| Product | Documented capability / vendor claim | Implication for Iris |
| --- | --- | --- |
| Shopify Sidekick | Shopify documents store-aware assistance, content creation, voice/screen sharing, remembered context and supported third-party apps. [Sidekick](https://help.shopify.com/en/manual/ai-powered-tools/sidekick), [app guidance](https://help.shopify.com/en/manual/ai-powered-tools/sidekick/help-and-guidance) | A conversational store assistant, voice or memory is already familiar territory. Hermes also supplies these primitives. |
| Sidekick Pulse | Early access for selected merchants: proactive store-data recommendations, up to five suggested actions, a conversational to-do list and feedback-driven personalization. Changes require approval. Recent sales and Network Intelligence are prerequisites. [Pulse](https://help.shopify.com/en/manual/ai-powered-tools/sidekick/pulse) | “She proactively suggests your next move” alone is insufficient differentiation. Iris can focus on external-market evidence in a different owner workflow. |
| Prisync | Documents competitor prices, stock monitoring, alerts, dashboards and rule-based repricing. Its marketing page also names promotions and reviews; this is a vendor claim, not verification of interpreting every multi-buy offer. [Help](https://helpcenter.prisync.com/hc/en-us/articles/213844105-What-is-Prisync), [competitive intelligence](https://prisync.com/competitive-intelligence-software/) | Price/stock alerts and promotion monitoring are established. Do not claim Iris invented either; product matching, offer conditions and merchant-specific reasoning must be demonstrated. |
| Klaviyo Composer | Current vendor update page advertises auditing flows, segments and forms to find revenue opportunities, then producing campaign assets for review. [Current updates](https://www.klaviyo.com/whats-new) | AI campaign creation is crowded, including opportunity discovery. Iris should connect a specific external signal to a constrained owner decision, rather than promise a whole marketing department. |
| Similarweb | Cross-Retail IQ documents product/category/price collection plus modeled behavior, partner data and direct measurements. Separately, Web Intelligence can withhold traffic estimates for small sites lacking reliable data. [Cross-Retail IQ](https://support.similarweb.com/hc/en-us/articles/34560857710749-Cross-Retail-IQ), [small-site limitation](https://support.similarweb.com/hc/en-us/articles/207698639-What-does-Not-enough-data-mean) | Direct observation of a small local storefront is useful even without reliable traffic estimates. This does not establish a deficiency in Similarweb's retail product or permission to infer competitor sales. |

Shopify's September 2026 research guide explicitly describes pairing Sidekick for internal store data with ChatGPT for outside-market investigation. Combining internal and external information is therefore established prior art; reducing the owner's handoffs is an experience opportunity. [Shopify market research](https://www.shopify.com/enterprise/blog/ecommerce-market-research)

**Language caution:** Klaviyo's older Marketing Agent help page lists English, French and German, while current product pages advertise Composer. Do not turn that older list into a claim that current Klaviyo cannot generate Arabic. Egyptian Arabic quality remains a hypothesis to test with owners. [Older help page](https://help.klaviyo.com/hc/en-us/articles/40992879084059)

## Promising hypotheses to test

1. **One market signal, one useful response.** Iris detects a competitor offer, shows its dated evidence and basket conditions, compares the relevant own product, respects supplied costs, and produces one usable Egyptian Arabic response. The memorable moment is changing the owner's decision with an overlooked fact. The possible differentiation is the complete Telegram experience, not any individual feature.
2. **The screenshot becomes a business decision.** The owner forwards an offer image or product URL; Iris uses Hermes vision/search, validates what is visible, asks only for a missing material cost or condition, and returns an equivalent-basket comparison. Screenshot OCR alone adds little; linking the offer to this store's choices is the test.
3. **She checks the move afterward.** The owner chooses an action; Iris remembers it, re-reads a publicly observable listing change and asks about the result at the agreed time. Owner-reported numbers remain labeled. A before/after change is not causal proof that Iris increased sales. This continuity could matter more than producing more drafts.

These workflows are not proven market gaps. Test them with one Egyptian merchant before deciding that another platform, integration or data source is needed.

## Finishable first slice

Definition of done: **one market opportunity produces a source-backed, margin-aware Telegram recommendation, one owner-approved response offer created and verified in Shopify, an Arabic announcement draft and one remembered review.**

Use existing tools, Hermes vision/memory/scheduling and one category. Keep a saved expected-versus-actual case covering a multi-buy offer whose effective unit price reverses the single-item comparison. Require explicit eligibility, currency, pack size, freshness and known costs; abstain on missing facts. Check whether the owner uses the proposed response and whether it saves work.

Out of scope: base-price changes, automatic publishing, contacting customers or competitors, sales forecasts, estimated competitor revenue, customer-level data, broad review scraping, new dashboards, general store editing, multi-buy/bundle creation and a general CRM. Order analytics can be evaluated later if the pilot proves a need and the owner authorizes the additional read access.

## Shopify data and first write

Verified 30 September 2026 against Shopify's current GraphQL **2026-07** reference. These are possibilities, not enabled features or confirmation of the installed token's scopes.

**Current code:** `iris_store.py` reads product descriptions but truncates returned text to 600 characters, one featured image, the first 20 variants and first 10 metafields. It does not query costs, inventory levels or orders. Setup documents `read_products`; inspect granted scopes before extending access.

**Installed connection checked:** a read-only Admin API probe on 30 September returned
only `read_products`. All six variants returned by the active-product sample had no
stored `unitCost` and `tracked: false`. The cost query succeeded with existing access;
no scope or store setting was changed. This is evidence for the six checked variants,
not an audit of draft products or every possible inventory record. Add known cost-per-item
values and enable quantity tracking where appropriate before using these data for decisions.
[Shopify bulk editor](https://help.shopify.com/en/manual/products/inventory/adjusting-inventory/bulk-editing-inventory),
[inventory setup](https://help.shopify.com/en/manual/products/inventory/setup/set-up-inventory-tracking).

| Next data | Requirement and value |
| --- | --- |
| Full product detail | Remove truncation for selected-product detail; retrieve exact `descriptionHtml` before any edit. Better comparison and preservation of existing content. |
| Unit cost | `InventoryItem` accepts `read_products` **or** `read_inventory`; `unitCost` additionally needs “View product costs” when granular permissions apply. Costs can be missing and do not include all contribution costs. [InventoryItem](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryItem) |
| Stock by location | `InventoryLevel` requires `read_inventory`; quantities distinguish available, on-hand and committed stock. [InventoryLevel](https://shopify.dev/docs/api/admin-graphql/latest/objects/InventoryLevel) |
| Sales / outcomes, later | `read_orders` defaults to 60 days; older orders require approved `read_all_orders`. Orders are protected customer data; requirements vary by app type. `shopifyqlQuery` separately requires `read_reports` **and level 2 customer-data access**, even for aggregate queries. [Scopes](https://shopify.dev/docs/api/usage/access-scopes), [protected data](https://shopify.dev/docs/apps/launch/protected-customer-data), [ShopifyQL](https://shopify.dev/docs/api/admin-graphql/latest/queries/shopifyqlQuery) |

**Accepted positioning:** market discovery → business decision → approved response → Shopify action.
The owner rejected generic product-page editing as the first action because it does not complete
Iris's market-scout promise. A listing correction remains relevant only when tied to a specific
market finding; technical ease alone is insufficient reason to make it the flagship feature.

**Recommended first write:** create one owner-approved product-specific discount code in response
to a verified market opportunity, with an explicit value, start/end time and usage limit. Confirm
cost inputs, stock and interaction with existing offers before recommendation. Bind approval to
the precise terms, prevent duplicate execution, check errors and read back the saved terms. Allow
deactivation. An active offer affects checkout economics; it must not be described as an unpublished
draft. The owner may also choose no action. Scheduled discovery and competitor content cannot
authorize execution. This is planned, not implemented; the installed token is still read-only.
Shopify requires `write_discounts` for [discountCodeBasicCreate](https://shopify.dev/docs/api/admin-graphql/latest/mutations/discountCodeBasicCreate).

## Ranked brainstorm and recommendation

These are design judgments, not new implemented capabilities or demonstrated demand.

| Direction | Memorable demonstration | Increment beyond today's Iris | Recommendation |
| --- | --- | --- | --- |
| Competitor offer to your response | Forward an offer; Iris catches its conditions, checks your costs, rules out an unviable response and drafts a feasible alternative | A repeatable combined workflow, reliable basket/offer normalization, owner-confirmed cost constraints and deterministic scenario arithmetic | First: clear business value with a narrow build |
| On-demand campaign material | Say "prepare it"; receive the Arabic caption, customer reply and a branded visual using your product photo | Text drafts already exist; visual creation needs configured native Hermes image generation and verification that labels/products remain accurate | Second: visibly impressive, but only after the recommendation is correct |
| Product-page before and after | Iris finds a specific missing fact; owner fixes it; Iris re-reads and demonstrates the correction | Factual review and re-read already exist; a rendered storefront audit would need additional browser access and a separate security review | A useful near-term demo, modest feature increment |
| Relevant stock opportunity | A watched standalone product runs out; Iris finds your genuinely comparable available alternative and prepares a response | Better matching and freshness checks; the underlying alerts already exist | Valuable supporting case, not the central novelty claim |
| Investigate a sales drop | Connect an observed sales decline with funnel data, product changes and competitor events, then propose a test | Requires aggregate order/funnel evidence unavailable to the current catalog-only profile | Later: stronger diagnosis potential but substantially larger scope |

The chosen headline is **"Forward a competitor's offer. Iris works out your response."**
The differentiating hypothesis is judgment with this owner's constraints and reduced handoffs.
An attractive campaign or translated caption alone is not a defensible advantage.

### A compact demo to validate

1. Owner forwards one offer screenshot or product URL and asks how to respond.
2. Iris identifies the relevant own product, reads its source and distinguishes comparable product,
   quantity, currency, advertised offer conditions, known delivery cost and observation date.
3. Iris uses owner-confirmed product cost, packaging, fees and minimum acceptable contribution.
   Missing inputs stay unknown; she asks one material question rather than inventing them.
4. Compare at most two feasible responses: maintaining the price/positioning or a specified price,
   bundle or gift with known costs. Report contribution and break-even thresholds, not predicted sales.
   A different basket can be an alternative strategy but never an equivalent-price victory.
5. Recommend one response or explain why no response meets the constraints. On request, provide
   a copyable Egyptian Arabic caption and a customer reply; do not publish them.
6. When the owner approves precise supported offer terms, create the bounded Shopify discount
   code and verify it. Retain the chosen move in native memory and review it in the existing weekly
   conversation. Distinguish verified offer creation from owner-reported business outcomes.

Acceptance cases should include a straightforward discount, conditional multi-buy, mismatched
size/skin type, missing costs, conflicting advertised prices, a stale screenshot and no financially
feasible response. A single impressive happy path is insufficient. Collect one owner's usefulness
rating and manual versus assisted completion time before expanding.

The existing four tools and native vision, memory and scheduled delivery provide the foundation.
Page-only offer conditions are not currently preserved as structured changes by daily catalog
snapshots. The first slice can be owner-triggered; proactive offer detection is a later measured
extension. Scheduled agents currently cannot write owner memory, so cost context must be deliberately
made available before claiming proactive margin-aware decisions. Do not treat a prompt rewrite as
proof that either data gap has been solved.

### Freshness finding from this research

The official Infinity sunscreen page retrieved through web research displayed both LE 360 and a
LE 216 / 40% promotion, while the earlier Iris evaluation recorded a 2+2 offer. The research tool's
crawled representation is not a verified checkout or proof of the exact change time. Re-read and
resolve the current offer before using either in a live recommendation; do not stack the two offers.
[Official product page](https://infinityclinicpharma.com/ar/products/naturals-sun-screen-gel-spf-50-oily-skin).

Shopify documents eligibility and discount-combination limitations, further supporting explicit
conditions rather than assuming every advertised saving stacks. [Discount combinations](https://help.shopify.com/en/manual/discounts/discount-combinations).
Hermes documents native vision, memory, scheduling and image generation, but Iris's present Telegram
configuration enables vision and memory, not image generation. Native capability still needs host
configuration and end-to-end validation. [Hermes tools](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools/).
