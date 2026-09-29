#!/usr/bin/env bash
# Create Iris's two scheduled jobs in her Hermes profile. Run once on the host.
#   OWNER_CHAT_ID   the owner's Telegram user ID (required; alerts go only there)
#   IRIS_PROFILE    Hermes profile name (default: iris)
#   DAILY_SCHEDULE  default "0 8 * * *"   (for the demo, e.g. "every 10m")
#   WEEKLY_SCHEDULE default "0 10 * * 0"  (Sunday 10:00, profile time zone)
set -euo pipefail
: "${OWNER_CHAT_ID:?Set OWNER_CHAT_ID to the owner's Telegram user ID}"
PROFILE="${IRIS_PROFILE:-iris}"
DAILY="${DAILY_SCHEDULE:-0 8 * * *}"
WEEKLY="${WEEKLY_SCHEDULE:-0 10 * * 0}"

hermes -p "$PROFILE" cron create "$DAILY" \
  "Something urgent changed at the stores you watch for the owner. Using the facts above and the market-watch skill, write one short alert. Check the owner's own products with my_store so the alert says what it means for them, and offer one move you can draft." \
  --name iris-daily-check --script iris_daily_check.py --skill market-watch \
  --deliver "telegram:${OWNER_CHAT_ID}"

hermes -p "$PROFILE" cron create "$WEEKLY" \
  "Write 'This week in your market' for the owner, using the data above and the weekly-brief skill. Check the owner's own products with my_store. Do not repeat what you already reported last week." \
  --name iris-weekly-brief --script iris_weekly_data.py --skill weekly-brief --continuity \
  --deliver "telegram:${OWNER_CHAT_ID}"

hermes -p "$PROFILE" cron list
