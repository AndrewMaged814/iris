# Setting up Iris (operator)

The host already runs Hermes (pinned commit `c1488ac`). Background notes from the first prototype:
`docs/research/OPERATOR_SETUP.md` and `docs/research/SHOPIFY_DEV_APP.md`.

1. **Create the profile** `iris` and install this repo as its distribution (SOUL, config, skills, plugins,
   scripts). Choose the model: `hermes -p iris setup`. Set a fallback provider too.
2. **Fill the profile's `.env`** from `.env.EXAMPLE`: bot token, the owner's Telegram ID (only this ID may
   talk to Iris), the store's `myshopify.com` address and the Shopify app credentials (`read_products` only).
3. **Check it:** `python3 tools/iris_doctor.py --profile-home ~/.hermes/profiles/iris --live`, using
   Hermes' Python so the safe web client is found.
4. **Check the gateway mode.** This host's default gateway serves every profile and notices profile changes
   automatically. Do not install a separate Iris gateway. After connecting Telegram, check
   `hermes -p iris gateway status`; restart the shared gateway only if the plugin has not loaded.
5. **First chat:** the owner taps Start. Iris reads the store, suggests competitors, the owner approves.
6. **Create the scheduled jobs** once: `OWNER_CHAT_ID=<id> scripts/setup_jobs.sh`
   For the demo, use a short schedule: `DAILY_SCHEDULE="every 10m" OWNER_CHAT_ID=<id> scripts/setup_jobs.sh`.
7. `hermes -p iris cron list` should show `iris-daily-check` and `iris-weekly-brief`.

When replacing a deleted profile on this Hermes revision, create its empty home first:
`hermes profile create iris --no-skills --no-alias`, then install with `--force` before configuring
credentials or the model. Direct distribution installation does not clear the deleted-profile marker.
Never force-install the blank template over a configured profile.

The doctor needs Hermes' Python, including its `python-dotenv` dependency, to read quoted `.env` values
correctly. Store credentials and data paths use Hermes' native profile scope in the shared gateway.

The final host's Telegram connection is verified and its daily and weekly jobs are already active.
Check them with `hermes -p iris cron list --all`. Do not run `setup_jobs.sh` again, which would create
duplicates. If a job is paused for maintenance, resume it with `hermes -p iris cron resume <job-id>`.

Iris's data lives in `<profile>/iris/iris.db`. Delete that file to start the watchlist over.
