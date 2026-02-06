from __future__ import annotations

from datetime import datetime, timezone

import httpx

from ..models import RawItem
from ..sources import Source
from .http_utils import parse_datetime


def collect(source: Source, user_agent: str) -> list[RawItem]:
    with httpx.Client(timeout=30, follow_redirects=True) as client:
        res = client.get(source.url, headers={"User-Agent": user_agent, "Accept": "application/vnd.github+json"})
        res.raise_for_status()
        releases = res.json()

    items: list[RawItem] = []
    for rel in releases[:10]:
        published = parse_datetime(rel.get("published_at"))
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
        items.append(
            RawItem(
                source_id=source.id,
                service=source.service,
                title=rel.get("name") or rel.get("tag_name") or "Release",
                url=rel.get("html_url") or source.url,
                published_at=published,
                body=rel.get("body") or "",
            )
        )
    return items
