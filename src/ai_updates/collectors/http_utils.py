from __future__ import annotations

from datetime import datetime, timezone

import httpx


def fetch_text(url: str, user_agent: str) -> str:
    with httpx.Client(timeout=30, follow_redirects=True) as client:
        res = client.get(url, headers={"User-Agent": user_agent})
        res.raise_for_status()
        return res.text


def parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)
