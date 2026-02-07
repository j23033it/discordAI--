from __future__ import annotations

import httpx

from ..models import Summary, UpdateItem

"""Discord への通知送信を担当するモジュール。"""


def post_message(webhook_url: str, content: str) -> None:
    # Discord Incoming Webhook へテキストをPOSTする。
    with httpx.Client(timeout=20) as client:
        res = client.post(webhook_url, json={"content": content})
        res.raise_for_status()


def _format_item(item: UpdateItem, summary: Summary) -> str:
    # 見出し + 箇条書き + 原文リンクのシンプルな通知フォーマット。
    bullets = "\n".join(f"- {b}" for b in summary.bullets)
    return (
        f"**{summary.headline}**\n"
        f"{bullets}\n"
        f"原文: {item.url}"
    )


def send_immediate(webhook_url: str, item: UpdateItem, summary: Summary) -> None:
    # 送信用の本文を作って即時通知する。
    post_message(webhook_url, _format_item(item, summary))
