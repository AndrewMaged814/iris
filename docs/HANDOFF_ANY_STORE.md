# Handoff: Iris for any store (branch `iris-any-store`)

For the next agent continuing this work. Read `AGENTS.md` first; its rules still apply.
Delete this file when the remaining work below is done.

## Why this branch exists

Iris was written around a skincare store. The goal: any Shopify owner, any category, with
off-the-shelf tools instead of hand-built readers. Mira Nile stays the demo.
Background, in order:
1. `docs/research/IRIS_GENERAL_STORE_DESIGN.md`: the design (general method + category
   references + a market profile in memory).
2. `docs/research/IRIS_COVERAGE_MEASUREMENT.md`: 30 real Egyptian stores. Coverage followed the
   store platform, not the category; 14/30 fully readable before this branch.

## Done on this branch (all offline-tested: `python3 -m unittest discover -s tests`, 111 pass)

- **Scout (commit "Scout for unwatched competitors…")**: "who is my real competitor" searches beyond
  the watchlist; SearXNG pinned as the free search backend (`web.search_backend: searxng`,
  `SEARXNG_URL`); cache-first reads via `market_changes`; doctor checks `SEARXNG_URL`.
- **Page reader swapped to extruct + price-parser** (`plugins/iris/iris_feeds.py`): JSON-LD,
  microdata and OpenGraph; price strings like "EGP 1,250.00"; a page whose currencies contradict
  each other leaves `currency` null with `currency_conflict`. Hand-written JSON-LD parser removed.
- **Variant options kept** from Shopify (`options`) and WooCommerce (`attributes`), passed to Iris.
- **Product links on any platform** (`_PRODUCT_LINK`): Shopify, WooCommerce (trailing `/` kept),
  Wuilt `/product/all/x`, Magento `x.html`, `/p/ /item/ /shop/ /dp/`. A link that turns out to be a
  category page returns `scope: "listing"`.
- **Sitemap sample**: a store homepage with no feed is read from an even, repeatable sample of 6
  product pages from its sitemap (`source: "sitemap"`, `scope: "sample"`, `sample: {...}`). The daily
  diff treats samples as partial: no new/removed-product alerts.
- **robots.txt respected** in the network layer (`http_get` → `robots_allows`, stdlib
  `urllib.robotparser`, cached per site). A disallowed optional feed counts as absent.
  New access states: `disallowed_by_robots`, `reader_unavailable`.
- **Arabic links percent-encoded** (`_uri`); the fallback reader no longer crashes on them.
- **Hermes browser enabled, read-only, chat-only** (`config.yaml`): `browser` in Telegram toolsets,
  `browser.cloud_provider: local`, `browser.backend: "off"`. The plugin's `pre_tool_call` hook
  `browser_guard` (`plugins/iris/__init__.py`) allows only navigate/snapshot/scroll/back/
  get_images/vision, blocks click/type/press/console/cdp/dialog/vault/exec, non-http(s), private
  addresses and robots-disallowed pages. Honest UA via `AGENT_BROWSER_ARGS` in `.env`.
- **changedetection.io integration** (`plugins/iris/iris_monitor.py`): adding a product page to the
  watchlist creates a `restock_diff` watch (daily, Iris UA, no proxy); removing deletes it; the daily
  check reads the watch (`_monitored` in `scripts/iris_daily_check.py`) and falls back to Iris's own
  read if the monitor is down. Watch id stored in `stores.monitor_id` (auto-migrated).
- Dependencies declared: `plugins/iris/plugin.yaml` `python_dependencies`, CI installs them.

## Not verified yet (needs a machine with Docker / a Hermes host)

1. **changedetection.io live**: run `docker run -d -p 127.0.0.1:5000:5000 ghcr.io/dgtlmoon/changedetection.io`,
   create an API key, set `CHANGEDETECTION_URL`/`CHANGEDETECTION_API_KEY`, then: watch one real
   product page via `iris_monitor.watch`, trigger a recheck (`GET /api/v1/watch/<uuid>?recheck=1`),
   confirm `iris_monitor.product` returns price/currency/stock. Confirm the watch's request really
   uses Iris's `User-Agent` header. Only tested against a fake so far.
2. **Hermes browser live**: on the Hermes host, confirm the Telegram session lists only the browser
   read tools after the guard, that `AGENT_BROWSER_ARGS` sets the UA (check a request log or
   httpbin.org/user-agent), and that `ctx.register_hook` exists on the installed Hermes revision.
3. **SearXNG live**: `web.search_backend` was checked against Hermes `main`, not the tested
   `c1488ac`. Run the doctor and one "who is my competitor" chat.
4. **`python_dependencies`** in `plugin.yaml`: confirm the installed Hermes admits them for a plugin
   shipped inside a profile distribution; otherwise install extruct/price-parser into Hermes's venv.

## Remaining work (task 5 of the plan)

1. **Doctor** (`tools/iris_doctor.py`): check `extruct`/`price_parser` importable, `AGENT_BROWSER_ARGS`
   contains `--user-agent=IrisBot`, and (optional) changedetection.io reachable with the key.
2. **Docs**: `docs/SETUP.md` sections for the browser (Chromium via `hermes pm install chromium`,
   UA, sandbox flags) and changedetection.io (Docker command, API key, what it replaces).
   Update `docs/STATUS.md`, `README.md` architecture notes if they say the browser is off.
3. **Skill routing** (`skills/market-watch/SKILL.md`): when `read_store` returns `no_products` or a
   page without product data, use `web_extract` on the product page and read the price from text
   (say it came from page text); if the page needs JavaScript, use the browser read tools; if
   `disallowed_by_robots`, say so and ask for a screenshot. Explain `scope: "sample"` to the owner
   as "a sample of N of their M products".
4. **Category-neutral skills** (design doc, "Implementation order" steps 2–4):
   - new `skills/market-watch/references/categories.md` (beauty, fashion, electronics, food, home,
     other: what makes two products the same, unit price, where competitors sell). Move the skincare
     rules (skin type, per ml) into its beauty section unchanged.
   - neutral comparison rules in `market-watch` and `draft-move` step 2; price per unit of measure.
   - `skills/setup/SKILL.md`: write a ~300-char "Market profile" to MEMORY.md (category, comparison
     keys from `my_store search` variant options, where competitors sell, market/currency),
     confirmed with the owner in one question; skills read it.
   - neutral examples in SOUL, skills and the two tool-description `focus` examples in `__init__.py`.
5. **Grouping**: `iris_changes.summarize` groups by `product_type`; 5/14 readable stores leave it empty.
   Consider grouping by option names or title words when the type is missing.
6. **Re-measure**: rerun the 30 stores in the coverage doc with the new reader (honest UA, ≤3
   pages, 1 s delay) and add an "after" column. Expected gain: about 7 stores via sitemap/product
   pages; Wuilt/React stores via the browser.
7. **Evaluation**: add 3–4 non-beauty cases to `tools/evaluate_iris.py`; rerun the Mira Nile cases to
   confirm no regression.
8. Open a draft PR to `main` when green. Never push to `main`.
