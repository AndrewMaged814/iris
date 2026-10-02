"""Iris's small local database: watched stores, snapshots, signals and screenshot notes.

One Iris per store, so there is one owner and no per-owner separation.
No package-relative imports: the cron scripts import this module too.
"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

try:
    from agent.secret_scope import get_secret as _profile_value
except ImportError:  # standalone scripts/tests, or Hermes before profile scopes
    _profile_value = os.environ.get

KEEP_SNAPSHOTS = 30
MAX_STORES = 20

SCHEMA = """
CREATE TABLE IF NOT EXISTS stores (
  id INTEGER PRIMARY KEY, name TEXT NOT NULL, url TEXT NOT NULL UNIQUE,
  kind TEXT NOT NULL DEFAULT 'auto', focus TEXT NOT NULL DEFAULT '[]',
  added_at TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1, failures INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS snapshots (
  id INTEGER PRIMARY KEY, store_id INTEGER NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
  taken_at TEXT NOT NULL, access TEXT NOT NULL, source TEXT, products TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS signals (
  id INTEGER PRIMARY KEY, store_id INTEGER NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
  created_at TEXT NOT NULL, kind TEXT NOT NULL, urgent INTEGER NOT NULL, data TEXT NOT NULL,
  reported INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS notes (
  id INTEGER PRIMARY KEY, created_at TEXT NOT NULL, source TEXT NOT NULL, about TEXT, text TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS alert_runs (
  execution_id TEXT PRIMARY KEY, signal_ids TEXT NOT NULL);
"""


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def profile_timezone():
    """Use Hermes' profile configuration, with the distribution's Cairo default offline."""
    try:
        from hermes_cli.config import load_config
        name = load_config().get("timezone") or "Africa/Cairo"
    except ImportError:
        name = "Africa/Cairo"
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError):
        return timezone.utc


def default_path() -> Path:
    base = _profile_value("IRIS_DATA_DIR")
    if base:
        return Path(base) / "iris.db"
    try:
        from hermes_constants import get_hermes_home
        home = get_hermes_home()
    except ImportError:
        home = os.environ.get("HERMES_HOME") or str(Path.home() / ".hermes")
    return Path(home) / "iris" / "iris.db"


class Watchlist:
    def __init__(self, path: Path | None = None):
        self.path = Path(path) if path else default_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.executescript(SCHEMA)
        try:
            os.chmod(self.path, 0o600)
        except OSError:
            pass

    def close(self):
        self.db.close()

    # ---- stores
    def stores(self, active_only=True) -> list[dict]:
        sql = "SELECT * FROM stores" + (" WHERE active = 1" if active_only else "") + " ORDER BY id"
        return [dict(r, focus=json.loads(r["focus"])) for r in self.db.execute(sql)]

    def find(self, url_or_name: str) -> dict | None:
        row = self.db.execute("SELECT * FROM stores WHERE url = ? OR lower(name) = lower(?)",
                              (url_or_name.strip(), url_or_name.strip())).fetchone()
        return dict(row, focus=json.loads(row["focus"])) if row else None

    def add(self, name: str, url: str, kind: str = "auto", focus: list[str] | None = None) -> dict:
        existing = self.find(url)
        if existing:
            self.db.execute("UPDATE stores SET active = 1, name = ?, focus = ? WHERE id = ?",
                            (name, json.dumps(focus or existing["focus"]), existing["id"]))
            self.db.commit()
            return self.find(url)
        if len(self.stores()) >= MAX_STORES:
            raise ValueError(f"Iris watches at most {MAX_STORES} stores.")
        self.db.execute("INSERT INTO stores (name, url, kind, focus, added_at) VALUES (?, ?, ?, ?, ?)",
                        (name, url.strip(), kind, json.dumps(focus or []), now()))
        self.db.commit()
        return self.find(url)

    def remove(self, url_or_name: str) -> bool:
        store = self.find(url_or_name)
        if not store:
            return False
        self.db.execute("UPDATE stores SET active = 0 WHERE id = ?", (store["id"],))
        self.db.commit()
        return True


    def record_failure(self, store_id: int, failed: bool) -> int:
        self.db.execute("UPDATE stores SET failures = CASE WHEN ? THEN failures + 1 ELSE 0 END WHERE id = ?",
                        (1 if failed else 0, store_id))
        self.db.commit()
        return self.db.execute("SELECT failures FROM stores WHERE id = ?", (store_id,)).fetchone()[0]

    # ---- snapshots
    def last_good_snapshot(self, store_id: int) -> list[dict] | None:
        row = self.db.execute("SELECT products FROM snapshots WHERE store_id = ? AND access = 'ok' "
                              "ORDER BY id DESC LIMIT 1", (store_id,)).fetchone()
        return json.loads(row["products"]) if row else None

    def save_snapshot(self, store_id: int, result: dict) -> None:
        self.db.execute("INSERT INTO snapshots (store_id, taken_at, access, source, products) VALUES (?, ?, ?, ?, ?)",
                        (store_id, result.get("fetched_at") or now(), result["access"], result.get("source"),
                         json.dumps(result.get("products") or [])))
        self.db.execute("DELETE FROM snapshots WHERE store_id = ? AND id NOT IN "
                        "(SELECT id FROM snapshots WHERE store_id = ? ORDER BY id DESC LIMIT ?)",
                        (store_id, store_id, KEEP_SNAPSHOTS))
        self.db.commit()

    def market_context(self, days: int = 7) -> dict:
        """The same dated evidence for chat and scheduled briefs; never inferred currency."""
        from iris_changes import summarize
        zone = profile_timezone()
        since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        coverage, market = {}, {}
        for s in self.stores():
            row = self.db.execute("SELECT COUNT(*) AS checks, MIN(taken_at) AS first_checked, "
                                  "MAX(taken_at) AS last_checked FROM snapshots "
                                  "WHERE store_id = ? AND access = 'ok' AND taken_at >= ?",
                                  (s["id"], since)).fetchone()
            evidence = {"url": s["url"], **dict(row)}
            for key in ("first_checked", "last_checked"):
                evidence[key + "_local"] = (datetime.fromisoformat(row[key].replace("Z", "+00:00"))
                                             .astimezone(zone).isoformat()) if row[key] else None
            last = self.db.execute("SELECT taken_at, products FROM snapshots WHERE store_id = ? "
                                   "AND access = 'ok' ORDER BY id DESC LIMIT 1", (s["id"],)).fetchone()
            evidence["snapshot_checked_local"] = (datetime.fromisoformat(last["taken_at"].replace("Z", "+00:00"))
                                                   .astimezone(zone).isoformat()) if last else None
            coverage[s["name"]] = evidence
            if last:
                market[s["name"]] = summarize(json.loads(last["products"]))
        return {"observation_by_store": coverage, "market_by_store": market,
                "timezone": str(zone), "generated_at_local": datetime.now(zone).isoformat()}

    # ---- signals
    def save_signals(self, store_id: int, signals: list[dict]) -> None:
        stamp = now()
        self.db.executemany("INSERT INTO signals (store_id, created_at, kind, urgent, data) VALUES (?, ?, ?, ?, ?)",
                            [(store_id, stamp, s["kind"], 1 if s.get("urgent") else 0, json.dumps(s)) for s in signals])
        self.db.commit()

    def signals(self, days: int = 7, urgent_only=False, unreported_only=False) -> list[dict]:
        sql = ("SELECT signals.*, stores.name AS store FROM signals JOIN stores ON stores.id = signals.store_id "
               "WHERE stores.active = 1")
        params = []
        if days is not None:
            since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
            sql += " AND signals.created_at >= ?"
            params.append(since)
        if urgent_only:
            sql += " AND urgent = 1"
        if unreported_only:
            sql += " AND reported = 0"
        rows = self.db.execute(sql + " ORDER BY signals.id", params).fetchall()
        return [{"id": r["id"], "store": r["store"], "created_at": r["created_at"], **json.loads(r["data"])} for r in rows]

    def mark_reported(self, ids: list[int]) -> None:
        if ids:
            self.db.executemany("UPDATE signals SET reported = 1 WHERE id = ?", [(i,) for i in ids])
            self.db.commit()

    # ---- notes (things Iris saw in screenshots)
    def add_note(self, text: str, about: str | None = None, source: str = "screenshot") -> dict:
        cur = self.db.execute("INSERT INTO notes (created_at, source, about, text) VALUES (?, ?, ?, ?)",
                              (now(), source, (about or "")[:120], text[:1000]))
        self.db.commit()
        return {"id": cur.lastrowid, "about": about, "text": text[:1000]}

    def notes(self, days: int = 7) -> list[dict]:
        since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        return [dict(r) for r in self.db.execute("SELECT * FROM notes WHERE created_at >= ? ORDER BY id", (since,))]
