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
- The same native research case passed with cron toolsets. An exact Infinity product case used
  native extraction/search/browser only; its returned price/promotion differs from the earlier
  reader baseline, so that case remains partial pending current first-party offer reconciliation.
- Synthetic electronics onboarding confirmed the Market profile, native readback, fresh-session
  recall and cron-toolset recall. The owner has no merchant store yet. Fixture stays isolated.
- Canonical own-product storefront URLs returned by Shopify; null unpublished URLs stay null.
- 96 offline regressions pass locally; deleted tests cover intentionally removed catalog features.
  Delivery retry/receipt handling, store-write approval and reader safety remain tested.
- Earlier CI failure was missing python-dotenv; fixed and those pushed checks passed.

## Deployed 2 October 2026

The owner requested rollout. Runtime source `c0f4cb5` is installed; the shared gateway was
gracefully restarted and Iris Telegram reconnected. Live doctor reports Ready: own-store
catalog and exact product readable, IrisBot User-Agent set. Four broad watches were retired
under the product-only decision while keeping their history; the exact Infinity watch remains.
All 696 messages, owner memory, auth/model configuration and three job definitions were
preserved. Hermes's native session API cleared the one frozen prompt, retaining the transcript.
Backups are private on the host. Earlier local main edits/drafts are preserved in Git stash
`before Iris native rollout 2026-10-02`; primary and host checkouts use the pushed branch.

## Remaining proof

1. Additional exact product watches require the owner's selection. Existing broad history
   remains but its old full-store coverage is retired. First observations establish a baseline.
2. Retired external-monitor watches remain on the service until the operator cleans them up;
   deleting integration code does not delete live watches or stop services.
3. Native owner Telegram research/browser flow and actual scheduled execution/delivery need
   verification. Isolated native chat and cron-toolset research are not Telegram transport.
4. Live merchant onboarding remains pending until a store exists. Synthetic context recall
   does not prove Shopify access or actual scheduled delivery.
5. Known-match answers sometimes repeat acknowledged demo provenance and run long. The caption
   acknowledged-preview case passed source handling; quality is reviewed, not an automatic score.

Earlier coverage research documents are historical evidence for the retired crawler, not current
product capability or acceptance gates. The exact original URL cohort was discarded; operator
host retains a reconstructed 30-name repeat. Do not claim an exact before/after coverage gain.
