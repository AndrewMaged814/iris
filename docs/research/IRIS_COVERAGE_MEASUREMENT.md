# Can Iris read stores outside skincare? Coverage measurement

Date: 2 October 2026. Step 1 of the proof plan in [IRIS_GENERAL_STORE_DESIGN.md](IRIS_GENERAL_STORE_DESIGN.md).

## Method

- 30 real Egyptian online stores (6 each: beauty, fashion, electronics, food, home), found by web
  search and chosen to mix platforms, plus 5 Jumia/Noon category pages.
- Each was read once with Iris's own `read_store` (`plugins/iris/iris_feeds.py`), with its honest
  `IrisBot/1.0` user agent and no browser, from a plain Python run (Hermes's safe client not loaded).
  Paging was capped at 3 pages per store to stay polite; Iris itself allows 20.
- For every readable store, one product link was read too, as the morning offer check does.
- Stores that returned nothing were then checked for platform, product links on the homepage,
  one product page, and `robots.txt`/sitemap.

## Results

| Category | Full catalog | One product at a time | Not readable | Other |
| --- | --- | --- | --- | --- |
| Beauty | 3 (Joviality, Source Beauty, IMPALA) | – | Dr Beauty (Wuilt), Ramfa (Shopify feed returns 500) | Gloss Cairo unreachable |
| Fashion | 4 (Novencci, Phantom (Woo), Y House, Bulga) | – | – | Crypt (store closed, 402); Elia read with **wrong currency (IDR)** |
| Electronics | 1 (Trust) | 3 (Hardware Market, LDNIO, 2B category page) | CairoVolt, TV-IT (JS-only) | – |
| Food | 4 (18 Grams, Seelaz, Greenuts, Alyaa Dates) | 1 (Oven Heaven) | Keto Maram (Wuilt) | – |
| Home | 2 (Decohome, Maramzy) | 3 (Coccaro, no price; Efreshli; Ricrac) | Mobz (Wuilt) | – |
| **Total (30)** | **14** | **7** | **6** | 3 |

Marketplaces: 3 of 4 Jumia category pages gave 10 products each (EGP price and stock, about 12 s);
Jumia home/office timed out; Noon timed out.

What the readable catalogs contain (14 stores):
- Prices, EGP and stock: 100% of products in every catalog.
- Variant options (Size, Color, Weight…) in the raw feed: 13 of 14. Iris drops them today.
- `product_type` mostly empty in 5 of 14 (Y House, 18 Grams, Greenuts, Decohome, Alyaa Dates), so
  Iris's price picture puts most of their products under "other".
- Sale prices visible: 10 of 14 stores had products on sale.
- Time: 1.4–8 s per store. A store that fails costs 2–9 s before returning "no products".

## What this means

1. **Beauty isn't special; Shopify is.** 13 Shopify feeds read fully across all five categories;
   2 more Shopify stores (Ramfa, Ricrac) had their feed failing.
   Coverage follows the platform mix: electronics sellers in this sample mostly run WooCommerce
   with the Store API off, Magento or custom sites, so only 1 of 6 read as a catalog.
2. **Most failures are cheap to fix honestly.** All 13 no-product stores publish a sitemap (LDNIO's
   is broken); at least 10 clearly list product URLs. Product pages on WooCommerce, Magento and
   custom sites carry standard product data (JSON-LD) that Iris already parses. A sitemap fallback
   would turn about 7 stores into readable catalogs or samples: no browser, no new tool.
3. **JavaScript-only stores need a page renderer or screenshots.** Wuilt (3 stores, a common
   Egyptian builder) and two custom React sites returned no product data without a browser.
   Hermes `web_extract` with a JS-rendering backend is the Hermes-first route; until then,
   screenshots.
4. **Grouping by `product_type` doesn't work for many stores.** Iris needs to group by what's
   always there: title words, collections and variant options.
5. **Marketplaces give a sample, not a catalog.** Jumia category pages are enough for a price
   check on one product type; Noon didn't respond.

## Bugs found

- **Product-page reads only work for Shopify links.** `read_store` treats only `/products/<handle>`
  as a single product. A WooCommerce or Magento product link is read as a whole store and returns
  no page text, so the morning offer check can't see multi-buys or gifts outside Shopify.
- **Wrong currency accepted.** Elia Shoewear's page data says IDR; Iris would report IDR prices for
  an Egyptian store. The skill asks Iris to confirm currency, but the reader passes it through.
- **Arabic product links crash the fallback reader.** Without Hermes's client, a URL with Arabic
  characters raises `UnicodeEncodeError` instead of returning an access state. Hermes's own client
  handles it; the cron scripts or tests without it don't.
- **`robots.txt` isn't checked.** Every store in this sample allows general crawlers (Wuilt blocks
  named SEO bots only), but honest fetching should read and respect it.

## Recommended changes (for the implementation step)

In order of stores gained per line of code; none adds a tool or script:
1. Recognize product links on any platform (`/product/`, `.html`, `/p/`, JSON-LD `Product` on the page).
2. Sitemap fallback in `read_store`: when the feeds fail, read the sitemap's product URLs and a
   small, polite sample of product pages; say it's a sample. Check `robots.txt` first.
3. Keep variant option names; group products by title words, collections and options when
   `product_type` is empty.
4. Reject a currency that doesn't match the store's market unless the page confirms it.
5. Percent-encode non-ASCII links before fetching.
6. JS-only stores: route to Hermes `web_extract` (JS-rendering backend) or ask for screenshots.

Store list and raw results were produced from a temporary script and are not kept in the repo;
rerun by reading the same stores with `read_store`.

## Bounded after-probe — 2 October 2026

The original temporary URL/results manifest was discarded. An exact 30-store before/after
comparison needs those addresses reconstructed and confirmed; this probe is a subset, not a
replacement measurement or a claim of seven stores gained. Ran on the Hermes host with Iris
UA, `MAX_PAGES=3`, sitemap sample capped at three product pages and one-second page delays.
Feeds, robots and sitemap requests are additional requests; the cap is on feed paging/sample pages.

| Store URL | Before (original named store) | After | Scope/count |
| --- | --- | --- | --- |
| https://ramfabeauty.com/ | Feed 500/no catalog | blocked | no products |
| https://www.jovialitynaturals.com/ | Full catalog under Joviality name | blocked | identity/domain may differ from discarded original URL |
| https://novenccieg.com/ | Full catalog | Shopify readable, EGP | 216 products within paging cap |
| https://cairovolt.com/ | No products | no_products | browser/extraction still needed |
| https://www.ldnioegypt.com/ | One product readable | homepage no_products | exact-product reads are separate from this homepage probe |
| https://tv-it.com/ | JS-only/no products | sitemap readable, EGP | 2 products from 3 sampled pages out of 2,782 listed URLs |

Access depends on domain, network and current store behavior. Blocks were reported without
retrying through disguises or challenges. Samples do not prove catalog-wide price/stock coverage.
Missing `product_type` stays `other`; option names such as Size/Color cannot safely infer a
product category. Comparison skills use confirmed profile keys and individual catalog details.
