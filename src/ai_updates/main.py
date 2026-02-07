from __future__ import annotations

import os
import traceback

from .collectors import collect_source
from .config import Config
from .dispatchers.discord import send_immediate
from .normalize import normalize
from .sources import SOURCES
from .store import Store
from .summarizer import summarize


def _service_webhook(cfg: Config, service: str) -> str | None:
    if service == "openai":
        return cfg.webhook_openai
    if service == "gemini":
        return cfg.webhook_gemini
    if service == "claude":
        return cfg.webhook_claude
    return None


def run_once() -> None:
    cfg = Config.from_env()
    store = Store(cfg.db_path)

    try:
        for source in SOURCES:
            try:
                raws = collect_source(source, cfg.user_agent)
            except Exception as exc:
                print(f"[warn] source collection failed: {source.id}: {exc}")
                continue
            for raw in raws:
                try:
                    item = normalize(raw)
                    if store.is_seen(item.fingerprint):
                        continue
                    store.add_update(item)
                    summary = summarize(
                        item=item,
                        provider=cfg.summary_provider,
                        openai_api_key=cfg.openai_api_key,
                        openai_model=cfg.openai_model,
                        gemini_api_key=cfg.gemini_api_key,
                        gemini_model=cfg.gemini_model,
                    )
                    store.add_summary(item.fingerprint, summary)

                    webhook = _service_webhook(cfg, item.service)
                    if webhook:
                        send_immediate(webhook, item, summary)
                        store.mark_immediate_sent(item.fingerprint)
                except Exception as exc:
                    print(f"[warn] item pipeline failed: {source.id}: {exc}")
                    print(traceback.format_exc(limit=1))
                    continue
    finally:
        store.close()


def run_once_cli() -> None:
    run_once()


def run_maintenance(action: str) -> None:
    cfg = Config.from_env()
    store = Store(cfg.db_path)
    try:
        if action == "reset_all":
            store.reset_all()
            print("[info] reset all update history")
            return
        raise ValueError(f"unknown maintenance action: {action}")
    finally:
        store.close()


def run_maintenance_cli() -> None:
    action = os.getenv("MAINTENANCE_ACTION", "reset_all").strip().lower()
    run_maintenance(action)
