#!/usr/bin/env bash
# Create Iris's three scheduled jobs in her Hermes profile. Run once on the host.
#   OWNER_CHAT_ID   the owner's Telegram user ID (required; alerts go only there)
#   IRIS_PROFILE    Hermes profile name (default: iris)
#   DAILY_SCHEDULE  default "0 8 * * *"   (for the demo, e.g. "every 10m")
#   WEEKLY_SCHEDULE default "0 10 * * 0"  (Sunday 10:00, profile time zone)
#   OFFER_SCHEDULE  default "30 8 * * *"  (rival product-page offer check)
set -euo pipefail
: "${OWNER_CHAT_ID:?Set OWNER_CHAT_ID to the Telegram user ID of the owner}"
PROFILE="${IRIS_PROFILE:-iris}"
HERMES_SOURCE="${HERMES_SOURCE:-${HOME}/.hermes/hermes-agent}"
DAILY="${DAILY_SCHEDULE:-0 8 * * *}"
WEEKLY="${WEEKLY_SCHEDULE:-0 10 * * 0}"
OFFERS="${OFFER_SCHEDULE:-30 8 * * *}"

hermes -p "$PROFILE" cron create "$DAILY" \
  "The product-watch check returned changes or monitoring failures. Use the market-watch skill to decide what deserves the owner's attention. Read relevant facts from the confirmed connected catalog through Composio, compare a response with holding course, and lead with one justified priority. A detected change is not automatically a reason to act. Explain monitoring failures separately. Read connected apps only; do not change app data." \
  --name iris-daily-check --script iris_daily_check.py --skill market-watch \
  --deliver "telegram:${OWNER_CHAT_ID}"

# No pre-run script: Iris reads the watched rival product pages herself, and replies [SILENT]
# (Hermes delivers nothing) unless a page advertises an offer her previous report didn't mention.
hermes -p "$PROFILE" cron create "$OFFERS" \
  "Run the morning offer check from the market-watch skill: read the watched rival product pages, and alert the owner only about an advertised offer your previous report didn't mention. Otherwise reply exactly [SILENT]." \
  --name iris-offer-check --skill market-watch --continuity \
  --deliver "telegram:${OWNER_CHAT_ID}"

hermes -p "$PROFILE" cron create "$WEEKLY" \
  "Write 'This week in your market' for the owner, using the data above and the weekly-brief skill. Check the owner's own products from the owner-confirmed connected catalog through Composio. Do not repeat what you already reported last week. Read connected apps only; do not change app data." \
  --name iris-weekly-brief --script iris_weekly_data.py --skill weekly-brief --continuity \
  --deliver "telegram:${OWNER_CHAT_ID}"

# Explicit Telegram targets require native per-job opt-in; the global mirror flag
# alone only covers origin/home targets. The CLI doesn't expose this setting yet.
"${HERMES_PYTHON:-${HERMES_SOURCE}/venv/bin/python}" - "$HERMES_SOURCE" "$PROFILE" "$OWNER_CHAT_ID" <<'PY'
import json, os, sys
sys.path.insert(0, sys.argv[1])
from hermes_cli.profiles import get_profile_dir
os.environ["HERMES_HOME"] = str(get_profile_dir(sys.argv[2]))
from cron.jobs import load_jobs, update_job
ids = []
for job in load_jobs():
    if job.get("name") in ("iris-daily-check", "iris-offer-check", "iris-weekly-brief") and job.get("deliver") == "telegram:" + sys.argv[3]:
        updated = update_job(job["id"], {"attach_to_session": True})
        assert updated and updated.get("attach_to_session") is True
        ids.append(job["id"])
assert len(ids) == 3, "Expected exactly the three Iris jobs for this owner; inspect the schedule setup."
print(json.dumps({"chat_continuity_enabled_for": ids}))
PY

hermes -p "$PROFILE" cron list
