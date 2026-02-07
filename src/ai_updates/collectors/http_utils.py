from __future__ import annotations

from datetime import datetime, timezone

import httpx

"""収集処理で共通利用する HTTP / 日付ユーティリティ。"""


def fetch_text(url: str, user_agent: str) -> str:
    # HTMLページ本文を取得する。失敗時は呼び出し元で例外処理する。
    with httpx.Client(timeout=30, follow_redirects=True) as client:
        res = client.get(url, headers={"User-Agent": user_agent})
        res.raise_for_status()
        return res.text


def parse_datetime(value: str | None) -> datetime:
    # ISO8601文字列を datetime に変換。壊れた値なら現在UTCを返す。
    if not value:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)
