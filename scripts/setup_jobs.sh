#!/usr/bin/env bash
# Create Iris's two scheduled jobs in her Hermes profile. Run once on the host.
#   OWNER_CHAT_ID   the owner's Telegram user ID (required; alerts go only there)
#   IRIS_PROFILE    Hermes profile name (default: iris)
#   DAILY_SCHEDULE  default "0 8 * * *"   (for the demo, e.g. "every 10m")
#   WEEKLY_SCHEDULE default "0 10 * * 0"  (Sunday 10:00, profile time zone)
set -euo pipefail
: "${OWNER_CHAT_ID:?Set OWNER_CHAT_ID to the owner's Telegram user ID}"
PROFILE="${IRIS_PROFILE:-iris}"
HERMES_SOURCE="${HERMES_SOURCE:-${HOME}/.hermes/hermes-agent}"
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
    if job.get("name") in ("iris-daily-check", "iris-weekly-brief") and job.get("deliver") == "telegram:" + sys.argv[3]:
        updated = update_job(job["id"], {"attach_to_session": True})
        assert updated and updated.get("attach_to_session") is True
        ids.append(job["id"])
assert len(ids) == 2, "Expected exactly the two Iris jobs for this owner; inspect the schedule setup."
print(json.dumps({"chat_continuity_enabled_for": ids}))
PY

hermes -p "$PROFILE" cron list
