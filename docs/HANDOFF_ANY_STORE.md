# Handoff: Hermes-native Iris

Updated 2 October 2026. Branch `codex/iris-any-store`, fetched from `origin/iris-any-store`.
Read AGENTS.md. Main's local changes remain in the original checkout. Draft PR targets main.

## Current decision

Done means Hermes researches competitors; Iris adds the owner's business context and tracks
only owner-approved specific products. The owner explicitly chose product watches and asked
for substantial removal of custom research machinery.

Out of scope: full-catalog crawling, sitemap sampling, automatic new-product detection,
self-hosted search/monitor services, multi-owner support and broader store writes.

## Implemented

- Removed the forced SearXNG backend and environment setup; native Hermes selects providers,
  extracts pages and supplies search/extract cache and fallback. Existing profiles need the
  old override/environment removed; profiles do not automatically share provider credentials.
- Deleted Shopify/WooCommerce catalog paging, sitemap/navigation crawling and custom page-text
  extraction. `read_store` now only normalizes structured facts for one selected product watch.
  Homepages are rejected without crawling; ambiguous multi-product pages do not become watches.
- Deleted the optional changedetection.io integration, its environment/doctor setup and watch
  enrollment. Hermes scheduling remains; no extra search or monitoring service is required.
- Replaced detailed research-routing instructions with a short native research skill. Native
  web tools are also available to scheduled offer checks; scheduled memory/store-write limits remain.
- Kept own-store access and native owner-confirmed response codes, source links, confirmed Market
  profile, snapshots/diffs, alert delivery recovery, weekly continuity and browser read guard.
- Native isolated research used only skill_view, web_search and web_extract: found Greenuts'
  official 50 g matcha page, returned EGP350/EGP400 and its source. No custom reader, watch, memory
  or store writes. Default Hermes tools also found/extracted the page where forced SearXNG failed.
- Synthetic electronics onboarding confirmed the Market profile, native readback, fresh-session
  recall and cron-toolset recall. The owner has no merchant store yet. Fixture stays isolated.
- Canonical own-product storefront URLs returned by Shopify; null unpublished URLs stay null.
- 96 offline regressions pass locally; deleted tests cover intentionally removed catalog features.
  Delivery retry/receipt handling, store-write approval and reader safety remain tested.
- Earlier CI failure was missing python-dotenv; fixed and those pushed checks passed.

## Before deployment

1. Verify the final pushed CI and review this simplification. Candidate files have not replaced
   the live profile, owner memory, sessions or cron jobs. No owner Telegram message or store
   mutation was sent during validation.
2. Existing broad store watches must be replaced with exact product pages chosen by the owner.
   Do not silently remove their database/history or claim the old full-store coverage survives.
   Legacy reader kinds are accepted but do not restore crawling. Price/stock keys can change;
   first observations establish a fresh baseline, not new/removed product alerts.
3. Retired external-monitor watches remain on the service until the operator cleans them up;
   deleting integration code does not delete live watches or stop services.
4. Native owner Telegram research/browser flow and actual scheduled web-provider access need
   verification. The current native research proof is an isolated chat, not Telegram transport.
5. Live merchant onboarding remains pending until a store exists. Synthetic context recall
   does not prove Shopify access or actual scheduled delivery.
6. Known-match answers sometimes repeat acknowledged demo provenance and run long. The caption
   acknowledged-preview case passed source handling; quality is reviewed, not an automatic score.

Earlier coverage research documents are historical evidence for the retired crawler, not current
product capability or acceptance gates. The exact original URL cohort was discarded; operator
host retains a reconstructed 30-name repeat. Do not claim an exact before/after coverage gain.
