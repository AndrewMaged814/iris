# Iris for any store: design

Status: design only, nothing implemented. Date: 2 October 2026.
Goal: any Shopify store owner, whatever they sell, gets a correct scout. The demo stays on Mira Nile.

## The problem in one line

Iris's code is category-neutral; its judgment is skincare. The plugin reads products, prices, sale
prices, stock and new items and groups them by `product_type` for any catalog. But the rules that
decide *whether two products are the same* are written for skincare, so an electronics or fashion
owner gets the wrong comparisons.

## Where the skincare assumptions live (inventory)

| Kind | Where | Example |
| --- | --- | --- |
| Comparison rules | `skills/market-watch/SKILL.md` (product comparisons), `skills/draft-move/SKILL.md` step 2 | "check pack size, form, skin type", "compare price per ml", "size, skin type or formulation" |
| Worked examples | `SOUL.md`, `market-watch`, `setup`, `finding-competitors.md`, `voice.md`, `signals.md`, `weekly-brief` | "EGP 40 a bottle", "9 of 14 sunscreens", "vitamin c serum Egypt online store", "dermatologist tested" |
| Tool descriptions (seen every turn) | `plugins/iris/__init__.py` `read_store.focus`, `watchlist.focus` | `e.g. ['serum', 'sunscreen']` |
| Evaluation | `tools/evaluate_iris.py` | every store case is Mira Nile skincare |
| Market, not category | `SOUL.md`, `setup`, `market-watch`, `iris_offers.py` | Egyptian Arabic, EGP, Jumia/Noon/Amazon.eg, Cairo time |

Not skincare-specific (keep it): the reading pipeline, snapshots and change signals, the alert
types, the weekly brief structure, the offer workflow (percentage, quantity, margin), scope rules,
honest fetching, memory rules.

## What Hermes gives us (research summary)

From the Hermes Agent source (commit `10c6188d`) and its docs:
- **No install-time templating.** A distribution manifest has `name`, `version`, `env_requires`,
  `distribution_owned` and metadata only. SOUL.md has no substitution; SKILL.md substitutes only
  `${HERMES_SKILL_DIR}`/`${HERMES_SESSION_ID}`. So "one profile per category" would mean forks.
- **No category switch on skills.** Conditional activation covers OS, toolsets and fallbacks, not
  business type.
- **Progressive disclosure is the extension point.** `skill_view(name, path)` loads one
  `references/` file on demand. The docs: references are "a small set of files named by topic".
- **Memory is for *what*, skills for *how*.** The docs' own advice (`guides/tips.md`). Memory is
  small (MEMORY.md 2,200 chars, USER.md 1,375), frozen at session start, and loaded by cron runs too.
- **Onboarding precedent.** Hermes's own onboarding saves agreed answers as one USER.md entry and
  verifies the readback (`tui_gateway/onboarding_personalization.py`).
- **Updates replace shipped skill directories whole.** Anything the agent writes inside
  `skills/market-watch/` is deleted on the next update. `memories/` and Iris's `iris/iris.db` survive.
- **SOUL guidance.** Keep it "stable, broadly applicable"; a weak SOUL is "full of project details".
- **Skill config (`metadata.hermes.config`) is not reliable here.** Values are injected for
  preloaded and cron-attached skills, not for the model's own `skill_view` calls.
- No official example distribution handles domain differences; the documented recipe is "fork".

Conclusion: Hermes's model for generality is **a general method + on-demand topic references +
a short learned fact in memory**. That is the design below.

## Design

Iris knows *how* to scout; each store teaches her *what matters*. Three layers:

### 1. A general method (SOUL + skills, shipped)

Rewrite the comparison rules once, in category-neutral terms:
- Two products are comparable when they match on the attributes that define equivalence in this
  category (the market profile's comparison keys, below). Name the one unknown that could flip the
  verdict.
- Compare price per unit of measure (ml, g, kg, piece, metre, pack) when both sides confirm it,
  otherwise price per item with the size difference stated.
- Keep bundles, multi-buys and conditional offers separate from a single item's price (already general).

Examples stay, but as illustrations from more than one category, so the model doesn't learn
"Iris = skincare". SOUL keeps at most one short example per rule.

### 2. Category references (shipped, loaded on demand)

One new file: `skills/market-watch/references/categories.md`, so comparisons follow the rules of
the owner's category. One short section per common category (beauty and personal care, fashion and
shoes, electronics and accessories, food and drink, home and furniture, plus "other"):
- what makes two products the same (beauty: size, form, skin type; electronics: exact model,
  storage, condition, warranty; fashion: item type, material, size range; food: weight, pack count)
- the right unit price
- where competitors usually sell, and what Iris can or can't read there
- one worked comparison line

The skincare rules move here from `market-watch` unchanged, so Mira Nile behaves as today.
Categories that aren't listed use "other": derive the keys from the catalog (layer 3) and say
which keys were used.

### 3. A market profile per store (learned, in memory)

During setup Iris writes one MEMORY.md entry of about 300 characters, for example:

> Market profile: home fragrance (candles, diffusers). Compare by scent family, size (g/ml), burn
> time. Price per 100 g. Competitors: own Shopify sites + Instagram sellers. Market: Egypt, EGP.

- **Derived from the catalog, then confirmed by the owner in one question.** `my_store summary`
  gives the types and price range. `my_store search` already returns each product's variant
  `options` (Size, Color, Storage…): the owner's own catalog says which attributes distinguish
  products. The category reference adds what the catalog can't show.
- **MEMORY.md, not USER.md.** SOUL limits USER.md to what the owner says in their own words; the
  profile is Iris's working note. Owner corrections update it.
- **Cron runs see it.** Cron loads memory, so daily alerts and the Sunday brief use the same keys.
- **Survives updates.** Memory is user-owned; nothing is written inside shipped skill folders.
- Skills say "use the comparison keys in your market profile; for the category's details, read
  `references/categories.md`".

### Small code change (one, later)

Competitor reads keep only a variant *count*. Shopify `products.json` and the Woo Store API also
return option names and values (Size, Color, Storage). Keeping a short `options` field per product
in `iris_feeds.py` lets Iris match on the same keys for both stores. No new tool or script.
Tool-description examples become neutral (`e.g. ['sunscreen']` → `e.g. a product type such as
'sunscreen' or 'phone case'`).

## The market question (decision needed)

Category generality and country generality are separate. Iris is Egypt-first today: Egyptian
Arabic, EGP, Jumia/Noon/Amazon.eg, Cairo schedule. Recommendation: **make category general now; keep
Egypt as the default market but read it from the profile** (currency from the catalog, marketplaces
and language from the profile), so a second country later is a profile change, not a rewrite. The
offer currency list in `iris_offers.py` is already multi-currency.

## What we will not do

- Fork a profile per category or template SOUL at install (Hermes has no templating; forks drift).
- Let Iris write category rubrics into shipped skill folders (wiped on update, unreviewed).
- Rely on `metadata.hermes.config` for the category (not injected into `skill_view`).
- Put the rubric in memory (too small, wrong layer: memory is *what*, skills are *how*).
- Pretend coverage: a category whose competitors live on Instagram or blocked marketplaces gets
  an honest "send me screenshots", not a guessed comparison.

## Proof plan (before and after implementing)

1. **Coverage measurement (read-only, before any code).** For each of 5 categories, 5 real Egyptian
   competitor stores: record whether `read_store` returns products, prices, options and stock.
   Result: a table in `docs/research/` saying which categories Iris can cover today.
2. **Offline tests.** Add one non-beauty fixture catalog (e.g. electronics, Shopify JSON with
   Storage/Color options) and test that option names survive the feed reader. No network.
3. **Evaluation cases.** Keep every Mira Nile case. Add a few cross-category cases that check the
   behavior, not the wording: correct comparison keys, unit price, honest gap when the match is
   uncertain, no skin-type questions for a phone store.
4. **Demo unchanged.** Mira Nile's answers must be the same quality as today; its rules simply
   come from the beauty section of `categories.md`.

## Implementation order (for later)

1. Coverage measurement (decides how much each category can promise).
2. `categories.md` + neutral comparison rules in `market-watch`/`draft-move`, skincare rules moved
   into the beauty section.
3. Setup writes and confirms the market profile; skills read it.
4. Neutral examples in SOUL, skills and tool descriptions.
5. `options` in competitor reads + fixture test.
6. Cross-category evaluation cases, then a Mira Nile regression run.

Files touched: `SOUL.md`, four skills, one new reference, `iris_feeds.py`, `__init__.py`
descriptions, one test fixture, `evaluate_iris.py`. No new tools or scripts.
