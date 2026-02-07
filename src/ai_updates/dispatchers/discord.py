from __future__ import annotations

from datetime import timezone, timedelta

import httpx

from ..models import Summary, UpdateItem

"""Discord への通知送信を担当するモジュール。"""


def post_message(webhook_url: str, content: str) -> None:
    # Discord Incoming Webhook へテキストをPOSTする。
    with httpx.Client(timeout=20) as client:
        res = client.post(webhook_url, json={"content": content})
        res.raise_for_status()


_JST = timezone(timedelta(hours=9))


def _format_published_at(item: UpdateItem) -> str:
    # 通知タイトルに表示する日時を JST で固定フォーマット化する。
    dt = item.published_at
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(_JST).strftime("%Y-%m-%d %H:%M JST")


def _format_item(item: UpdateItem, summary: Summary) -> str:
    # 全サービス共通の固定通知フォーマット。
    title = f"{summary.headline}（{_format_published_at(item)}）"
    picked_bullets = summary.bullets[:3] if summary.bullets else ["詳細は原文リンクを参照してください。"]
    bullets = "\n".join(f"• {b}" for b in picked_bullets)
    return (
        f"**{title}**\n"
        f"{bullets}\n"
        f"原文: {item.url}"
    )


def send_immediate(webhook_url: str, item: UpdateItem, summary: Summary) -> None:
    # 送信用の本文を作って即時通知する。
    post_message(webhook_url, _format_item(item, summary))
