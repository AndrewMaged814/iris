# Handoff: Iris for any store

Updated 2 October 2026. Continuing branch: `codex/iris-any-store`, based on fetched
`origin/iris-any-store`. Read AGENTS.md first. Delete this file only when the remaining proof
below is complete. Main's local changes were preserved in the original checkout.

## Completed

- Earlier branch: SearXNG scout/cache-first reads; extruct/price-parser; variant options;
  any-platform product links; sitemap samples; robots checks; Arabic URL encoding;
  Hermes browser read guard; optional changedetection.io integration.
- Doctor: reader imports, browser User-Agent argument, paired optional monitor settings and
  authenticated live monitor reachability. Fixed stale SearXNG test fixture.
- Setup docs: manual plugin dependency install, tested browser install commands, UA/sandbox
  flags, monitor setup and fallback. The pinned Hermes rejects `hermes pm install chromium`;
  Playwright's cache is needed for its Chromium availability probe.
- Category reference file, neutral comparison rules/unit prices, setup's owner-confirmed
  ~300-character Market profile in native memory, category pointers in all four skills,
  examples across categories and neutral tool focus examples. Beauty rules retained in reference.
- Missing types remain `other`: guessed title/option grouping could compare unrelated prices.
- Four hypothetical category-expansion evaluation cases plus three native Mira Nile regressions
  ran in a private profile with Telegram removed/offers disabled. Review in docs/EVALUATION.md.
- Live changedetection.io found a fake-test assumption: watch JSON omits native `restock`.
  Fixed adapter to parse its authenticated cached HTML (`history/latest?html=1`). Confirmed
  EGP360/in-stock from Infinity and full request UA through httpbin; temporary watches removed.
- Native Hermes browser navigate/snapshot UA checked; PluginManager hook actually loads and
  blocks click/private navigation, permits snapshots. Native inventory still exposes actions;
  hook blocks execution. SearXNG service answered JSON search with HTTP200.
- Six-store bounded coverage probe, including TV-IT sitemap sample, recorded with URLs and
  limitations in docs/research/IRIS_COVERAGE_MEASUREMENT.md.
- 116 offline tests; repository validator. See docs/STATUS.md for final host verification.

## Remaining proof (keep explicit)

1. Reconstruct and confirm the original 30-store URL cohort, then rerun coverage with a retained
   URL/result manifest. Original measurement threw it away; six reconstructed URLs are not a
   full before/after. Preserve blocked access and distinguish catalog from sample.
2. Live non-beauty owner/catalog onboarding: confirm Market profile in native memory and verify
   readback/recall in a new chat and scheduled context. Current expansion cases use supplied
   hypothetical catalogs, not a live electronics/fashion/food/home merchant.
3. Owner Telegram browser flow and a real competitor-discovery conversation; current checks are
   isolated native sessions and direct native browser/hook probes, not Telegram transport.
4. Response-quality gaps: native known-match answer still says "your demo" and exceeds the usual
   length; caption cites a returned CDN image. Preserve honest evaluation rather than marking
   these complete. Existing Mira Nile comparison/offer facts remain correct in reviewed runs.
5. Production rollout is separate. Candidate files have not replaced the live profile/config,
   owner memory, saved sessions or cron jobs. Runtime dependencies were installed on the host.
   Private candidate/evidence copies remain there for review; offers were disabled and no owner
   message or store write was sent.

Draft PR targets main. Never push to main.
