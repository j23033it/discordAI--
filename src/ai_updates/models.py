from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

Service = Literal["openai", "gemini", "claude"]
Importance = Literal["high", "medium", "low"]


@dataclass(slots=True)
class RawItem:
    source_id: str
    service: Service
    title: str
    url: str
    published_at: datetime
    body: str


@dataclass(slots=True)
class UpdateItem:
    source_id: str
    service: Service
    title: str
    url: str
    published_at: datetime
    body: str
    fingerprint: str


@dataclass(slots=True)
class Summary:
    headline: str
    bullets: list[str]
    importance: Importance
    topic: str


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
