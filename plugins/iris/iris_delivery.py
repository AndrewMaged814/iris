"""Acknowledge Iris facts only from Hermes' native execution/delivery evidence.

This adapter sends nothing and never changes Hermes' ledgers. Unknown or active
sends stay held: replaying an uncertain send could duplicate an owner's alert.
"""
import json
import os
import sqlite3
from contextlib import closing
from pathlib import Path


def _rows(home, name, sql, params=()):
    path = Path(home) / "cron" / name
    if not path.exists():
        return []
    try:
        with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
            db.row_factory = sqlite3.Row
            return [dict(row) for row in db.execute(sql, params)]
    except sqlite3.Error:
        return []  # absent/changed native schema is not proof of delivery


def current_execution(home, script="iris_daily_check.py"):
    """Native cron launches scripts directly; match its parent worker and job.

    Hermes currently exports no execution ID to scripts. An ambiguous worker
    match is deliberately left uncorrelated rather than attributing another run.
    """
    try:
        jobs = json.loads((Path(home) / "cron/jobs.json").read_text())["jobs"]
    except (OSError, ValueError, KeyError, TypeError):
        return None
    matching = {job.get("id") for job in jobs if isinstance(job, dict)
                and job.get("script") == script and not job.get("no_agent")}
    rows = _rows(home, "executions.db",
                 "SELECT id,job_id FROM executions WHERE pid=? AND status='running'",
                 (os.getppid(),))
    matches = [row["id"] for row in rows if row["job_id"] in matching]
    return matches[0] if len(matches) == 1 else None


def reconcile(wl, home):
    """Return signal IDs held by unfinished/uncertain native sends.

    A failure notification being delivered does not acknowledge a failed model
    run. Deferred deliveries need the queue's final result, not just 'queued'.
    """
    held = set()
    for receipt in wl.db.execute("SELECT * FROM alert_runs").fetchall():
        ids = json.loads(receipt["signal_ids"])
        rows = _rows(home, "executions.db",
                     "SELECT status,delivery_outcome FROM executions WHERE id=?",
                     (receipt["execution_id"],))
        row = rows[0] if rows else {}
        status, delivery = row.get("status"), row.get("delivery_outcome")
        if status == "completed" and delivery == "queued":
            queued = _rows(home, "deliveries.db", "SELECT status FROM deliveries WHERE execution_id=?",
                           (receipt["execution_id"],))
            if not queued:
                queued = _rows(home, "deliveries.db",
                               "SELECT terminal_status AS status FROM delivery_tombstones WHERE execution_id=?",
                               (receipt["execution_id"],))
            delivery = queued[0]["status"] if queued else "queued"
        if status == "completed" and delivery == "delivered":
            wl.mark_reported(ids)
        elif status == "failed" or (status == "completed" and delivery in
                                     ("failed", "suppressed", "not_configured")):
            pass  # safe retry; no business answer was confirmed delivered
        else:
            held.update(ids)
            continue
        wl.db.execute("DELETE FROM alert_runs WHERE execution_id=?", (receipt["execution_id"],))
    wl.db.commit()
    return held


def record(wl, execution_id, ids):
    if execution_id and ids:
        wl.db.execute("INSERT OR REPLACE INTO alert_runs (execution_id,signal_ids) VALUES (?,?)",
                      (execution_id, json.dumps(ids)))
        wl.db.commit()
