from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import Summary, UpdateItem, utc_now

"""SQLite を使った永続化層。既読管理と要約保存を担当する。"""


class Store:
    def __init__(self, db_path: Path) -> None:
        # DBディレクトリが無ければ作成してから接続する。
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        # 起動時に必要テーブルを自動作成する。
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
                sent_immediate_at TEXT
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
        # 既読判定は fingerprint の存在確認のみで行う。
        row = self.conn.execute(
            "SELECT 1 FROM seen_updates WHERE fingerprint = ? LIMIT 1", (fingerprint,)
        ).fetchone()
        return row is not None

    def add_update(self, item: UpdateItem) -> None:
        # INSERT OR IGNORE で二重登録を防ぐ。
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
        # 箇条書きは改行区切りで1カラムに保存する。
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
            # 要約完了時刻を seen_updates 側にも記録する。
            "UPDATE seen_updates SET summarized_at = ? WHERE fingerprint = ?",
            (utc_now().isoformat(), fingerprint),
        )
        self.conn.commit()

    def mark_immediate_sent(self, fingerprint: str) -> None:
        # Discord 送信済みフラグの更新。
        self.conn.execute(
            "UPDATE seen_updates SET sent_immediate_at = ? WHERE fingerprint = ?",
            (utc_now().isoformat(), fingerprint),
        )
        self.conn.commit()

    def reset_all(self) -> None:
        # テストや再通知確認用に履歴を全削除する。
        self.conn.execute("DELETE FROM summaries")
        self.conn.execute("DELETE FROM seen_updates")
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
