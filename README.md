# Iris

**Iris is a market scout for one small business, on Telegram.** Tell her which stores to watch.
She checks them every day and tells you what changed, what it means for your own products, and
one thing you can do this week. She drafts it for you when you say yes.

- Watches competitor stores: Shopify stores, WooCommerce stores, and product pages (Jumia, Noon and
  others that publish product data).
- Reads screenshots of Instagram and Facebook posts you send her.
- Compares by product type with your own Shopify catalog, never product against product.
- Messages you only when something urgent happens: a promotion starts, a watched item runs out, or a
  new product appears. Every Sunday: "This week in your market".
- Read-only. Speaks Egyptian Arabic or English.

Built on [Hermes](https://github.com/NousResearch/hermes-agent). One Iris per store.

## How it works

| Part | What it does |
| --- | --- |
| Hermes | Telegram, the agent loop, vision, web search, scheduled jobs, delivery |
| `SOUL.md` + `skills/` | Who Iris is, the market-message checklist, how to set up, watch, report and draft |
| `plugins/iris/` | Four read-only tools: `my_store`, `read_store`, `watchlist`, `market_changes` |
| `scripts/` | The daily check (wakes Iris only when something urgent changed) and the weekly data |

## Install

See [`docs/SETUP.md`](docs/SETUP.md). Tests: `python3 -m unittest discover -s tests` (no network needed).

## Status

See [`docs/STATUS.md`](docs/STATUS.md). The earlier brand-protection prototype lives in the old
`iris-agent` repo (tag `v0-brand-protection`).
