# Status

## Built and tested offline

- Four read-only tools; Shopify, WooCommerce and JSON-LD page reading; honest block reporting.
- Change signals (new product, sale started/ended, price move ≥5%/≥10%, out of/back in stock, removed),
  with urgency limited to the owner's product types.
- Daily check with the `{"wakeAgent": false}` gate, reported-once alerts, one message after 3 failed checks.
- Weekly data collection. SOUL, four skills, validator, doctor, CI. 39 tests, no network.
- Profile-scoped store credentials and data paths; quoted environment settings checked by the doctor.

## Verified on the host (2026-09-30)

- Installed the final distribution as `iris`; removed the two earlier Iris profiles and stopped their
  legacy services after making a private host backup.
- A native Hermes turn returned the expected response using Luna through Azure Foundry.
- The own-store reader returned Mira Nile's catalog (15 active products).
- Telegram resolves exactly the four Iris tools, web search, vision, memory and skill reads.
  Scheduled runs resolve only the four Iris tools and skill reads; no terminal or store-write tools.
- Hermes' safe web client is importable. Telegram is connected to IrisMarketWatcherBot; an owner message
  and Luna reply are recorded. Full chat tests remain pending.
- Daily (08:00 Cairo) and Sunday (10:00 Cairo) jobs are active. The watchlist is empty until onboarding.

## Remaining live checks

- `hermes cron create --script` finds the scripts in the profile's `scripts/` folder. (Confirmed in the Hermes
  source: the installer copies every folder listed in `distribution_owned`, and `scripts` isn't a reserved name.)
- `tools.url_safety` is importable in the plugin and in cron script runs (otherwise the basic guard is used).
- Web search results and `display.platforms.telegram.tool_progress: "off"` behave as expected in chat.
- Hermes' own system messages (errors, restarts) are English and technical; plugins can't change them.

- Memory: the owner's name and preferences are saved and come back in a new chat (`/new`).
  Hermes also runs a periodic background memory review; check it never saves text that came from a website.

## Not built (by choice)

Multiple stores per Iris, Meta/Instagram APIs, ad libraries, automatic actions.
