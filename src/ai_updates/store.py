from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from .models import Summary, UpdateItem, utc_now


class Store:
    def __init__(self, db_path: Path) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS seen_updates (
                fingerprint TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                service TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                published_at TEXT NOT NULL,
                body TEXT NOT NULL,
                first_seen_at TEXT NOT NULL,
                summarized_at TEXT,
                sent_immediate_at TEXT,
                sent_digest_at TEXT
            );

            CREATE TABLE IF NOT EXISTS summaries (
                fingerprint TEXT PRIMARY KEY,
                headline TEXT NOT NULL,
                bullets_json TEXT NOT NULL,
                importance TEXT NOT NULL,
                topic TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(fingerprint) REFERENCES seen_updates(fingerprint)
            );
            """
        )
        self.conn.commit()

    def is_seen(self, fingerprint: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM seen_updates WHERE fingerprint = ? LIMIT 1", (fingerprint,)
        ).fetchone()
        return row is not None

    def add_update(self, item: UpdateItem) -> None:
        self.conn.execute(
            """
            INSERT OR IGNORE INTO seen_updates (
                fingerprint, source_id, service, title, url, published_at, body, first_seen_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.fingerprint,
                item.source_id,
                item.service,
                item.title,
                item.url,
                item.published_at.isoformat(),
                item.body,
                utc_now().isoformat(),
            ),
        )
        self.conn.commit()

    def add_summary(self, fingerprint: str, summary: Summary) -> None:
        bullets = "\n".join(summary.bullets)
        self.conn.execute(
            """
            INSERT OR REPLACE INTO summaries (
                fingerprint, headline, bullets_json, importance, topic, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                fingerprint,
                summary.headline,
                bullets,
                summary.importance,
                summary.topic,
                utc_now().isoformat(),
            ),
        )
        self.conn.execute(
            "UPDATE seen_updates SET summarized_at = ? WHERE fingerprint = ?",
            (utc_now().isoformat(), fingerprint),
        )
        self.conn.commit()

    def mark_immediate_sent(self, fingerprint: str) -> None:
        self.conn.execute(
            "UPDATE seen_updates SET sent_immediate_at = ? WHERE fingerprint = ?",
            (utc_now().isoformat(), fingerprint),
        )
        self.conn.commit()

    def mark_digest_sent(self, fingerprint: str) -> None:
        self.conn.execute(
            "UPDATE seen_updates SET sent_digest_at = ? WHERE fingerprint = ?",
            (utc_now().isoformat(), fingerprint),
        )
        self.conn.commit()

    def unsent_digest_items(self, limit: int = 100):
        return self.conn.execute(
            """
            SELECT u.*, s.headline, s.bullets_json, s.importance, s.topic
            FROM seen_updates u
            JOIN summaries s ON s.fingerprint = u.fingerprint
            WHERE u.sent_digest_at IS NULL
            ORDER BY u.published_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    def delete_unsent_digest_items(self) -> int:
        rows = self.conn.execute(
            "SELECT fingerprint FROM seen_updates WHERE sent_digest_at IS NULL"
        ).fetchall()
        fingerprints = [r["fingerprint"] for r in rows]
        if not fingerprints:
            return 0

        placeholders = ",".join(["?"] * len(fingerprints))
        self.conn.execute(
            f"DELETE FROM summaries WHERE fingerprint IN ({placeholders})", fingerprints
        )
        self.conn.execute(
            f"DELETE FROM seen_updates WHERE fingerprint IN ({placeholders})", fingerprints
        )
        self.conn.commit()
        return len(fingerprints)

    def reset_all(self) -> None:
        self.conn.execute("DELETE FROM summaries")
        self.conn.execute("DELETE FROM seen_updates")
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
