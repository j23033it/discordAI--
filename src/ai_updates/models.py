from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

"""アプリ全体で使うデータ型（モデル）を定義するモジュール。"""

# 扱うサービス名を型で制限し、タイポを減らす。
Service = Literal["openai", "gemini", "claude"]
# 通知の重要度レベル。
Importance = Literal["high", "medium", "low"]


@dataclass(slots=True)
class RawItem:
    # 収集直後の生データ。
    source_id: str
    service: Service
    title: str
    url: str
    published_at: datetime
    body: str


@dataclass(slots=True)
class UpdateItem:
    # 正規化後の内部データ。重複判定用の fingerprint を持つ。
    source_id: str
    service: Service
    title: str
    url: str
    published_at: datetime
    body: str
    fingerprint: str


@dataclass(slots=True)
class Summary:
    # LLM 要約の出力フォーマット。
    headline: str
    bullets: list[str]
    importance: Importance
    topic: str


def utc_now() -> datetime:
    # 現在時刻は UTC で統一して扱う。
    return datetime.now(timezone.utc)
