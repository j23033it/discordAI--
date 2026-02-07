from __future__ import annotations

import httpx

from ..models import Summary, UpdateItem


def post_message(webhook_url: str, content: str) -> None:
    with httpx.Client(timeout=20) as client:
        res = client.post(webhook_url, json={"content": content})
        res.raise_for_status()


def _format_item(item: UpdateItem, summary: Summary) -> str:
    bullets = "\n".join(f"- {b}" for b in summary.bullets)
    return (
        f"**{summary.headline}**\n"
        f"{bullets}\n"
        f"原文: {item.url}"
    )


def send_immediate(webhook_url: str, item: UpdateItem, summary: Summary) -> None:
    post_message(webhook_url, _format_item(item, summary))


def send_digest(webhook_url: str, lines: list[str]) -> None:
    post_message(webhook_url, "\n".join(lines))
