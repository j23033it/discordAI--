from __future__ import annotations

import os

from .config import Config
from .dispatchers.discord import send_digest, send_immediate
from .models import Service, Summary, UpdateItem, utc_now


def _service_webhook(cfg: Config, service: str) -> str | None:
    if service == "openai":
        return cfg.webhook_openai
    if service == "gemini":
        return cfg.webhook_gemini
    if service == "claude":
        return cfg.webhook_claude
    return None


def _preview_item(service: Service) -> tuple[UpdateItem, Summary]:
    now = utc_now()
    links = {
        "openai": "https://platform.openai.com/docs/overview",
        "gemini": "https://ai.google.dev/gemini-api/docs",
        "claude": "https://docs.anthropic.com/",
    }
    item = UpdateItem(
        source_id=f"preview_{service}",
        service=service,
        title=f"[プレビュー] {service} の通知表示テスト",
        url=links[service],
        published_at=now,
        body="Discord表示の確認用サンプルです。",
        fingerprint=f"preview-{service}-{now.isoformat()}",
    )
    summary = Summary(
        headline=f"[UI確認] {service} 更新の見出しサンプル",
        bullets=[
            "要点1: 1行で概要が把握できるか確認",
            "要点2: 箇条書き3点の読みやすさを確認",
            "要点3: 最後の原文リンク導線を確認",
        ],
        importance="medium",
        topic="preview",
    )
    return item, summary


def run_preview(target: str) -> None:
    cfg = Config.from_env()
    selected = target.lower().strip()
    allowed = {"all", "openai", "gemini", "claude", "digest"}
    if selected not in allowed:
        print(f"[warn] invalid PREVIEW_TARGET: {target}")
        return

    services: list[Service] = ["openai", "gemini", "claude"]
    if selected in services:
        services = [selected]
    elif selected == "digest":
        services = []

    for service in services:
        webhook = _service_webhook(cfg, service)
        if not webhook:
            print(f"[warn] webhook not set for service: {service}")
            continue
        item, summary = _preview_item(service)
        send_immediate(webhook, item, summary)

    if selected in {"all", "digest"}:
        if not cfg.webhook_digest:
            print("[warn] webhook not set for digest")
            return
        lines = [
            "**AI Updates Daily Digest (プレビュー)**",
            "",
            "## preview",
            "- [openai] UI確認用サンプル通知（リンク遷移チェック）",
            "- [gemini] UI確認用サンプル通知（読みやすさチェック）",
            "- [claude] UI確認用サンプル通知（文面チェック）",
        ]
        send_digest(cfg.webhook_digest, lines)


def run_preview_cli() -> None:
    run_preview(os.getenv("PREVIEW_TARGET", "all"))
