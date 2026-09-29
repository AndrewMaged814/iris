# Status

## Built and tested offline

- Four read-only tools; Shopify, WooCommerce and JSON-LD page reading; honest block reporting.
- Change signals (new product, sale started/ended, price move ≥5%/≥10%, out of/back in stock, removed),
  with urgency limited to the owner's product types.
- Daily check with the `{"wakeAgent": false}` gate, reported-once alerts, one message after 3 failed checks.
- Weekly data collection. SOUL, four skills, validator, doctor, CI. 28 tests, no network.

## To verify on the host (not yet done)

- The distribution installs `scripts/` into the profile, and `hermes cron create --script` finds them there.
- `tools.url_safety` is importable in the plugin and in cron script runs (otherwise the basic guard is used).
- Shopify client credentials work for the Mira Nile dev store app.
- The `search` toolset and `display.platforms.telegram.tool_progress: "off"` behave as expected.
- Hermes' own system messages (errors, restarts) are English and technical; plugins can't change them.

## Not built (by choice)

Multiple stores per Iris, Meta/Instagram APIs, ad libraries, automatic actions.
