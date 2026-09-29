# Setting up Iris (operator)

The host already runs Hermes (pinned commit `c1488ac`). Background notes from the first prototype:
`docs/research/OPERATOR_SETUP.md` and `docs/research/SHOPIFY_DEV_APP.md`.

1. **Create the profile** `iris` and install this repo as its distribution (SOUL, config, skills, plugins,
   scripts). Choose the model: `hermes -p iris setup`. Set a fallback provider too.
2. **Fill the profile's `.env`** from `.env.EXAMPLE`: bot token, the owner's Telegram ID (only this ID may
   talk to Iris), the store's `myshopify.com` address and the Shopify app credentials (`read_products` only).
3. **Check it:** `python3 tools/iris_doctor.py --profile-home ~/.hermes/profiles/iris --live`, using
   Hermes' Python so the safe web client is found.
4. **Restart the gateway** so the plugin loads (the known plugin-cache issue): restart the systemd service.
5. **First chat:** the owner taps Start. Iris reads the store, suggests competitors, the owner approves.
6. **Create the scheduled jobs** once: `OWNER_CHAT_ID=<id> scripts/setup_jobs.sh`
   For the demo, use a short schedule: `DAILY_SCHEDULE="every 10m" OWNER_CHAT_ID=<id> scripts/setup_jobs.sh`.
7. `hermes -p iris cron list` should show `iris-daily-check` and `iris-weekly-brief`.

Iris's data lives in `<profile>/iris/iris.db`. Delete that file to start the watchlist over.
