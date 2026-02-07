from __future__ import annotations

from collections import defaultdict
import os
import traceback

from .collectors import collect_source
from .config import Config
from .dispatchers.discord import send_digest, send_immediate
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


def run_digest() -> None:
    cfg = Config.from_env()
    store = Store(cfg.db_path)

    try:
        rows = store.unsent_digest_items(limit=150)
        if not rows:
            return

        grouped: dict[str, list[str]] = defaultdict(list)
        for r in rows:
            line = f"- [{r['service']}] {r['headline']} ({r['importance']})\n  {r['url']}"
            grouped[r["service"]].append(line)

        if cfg.webhook_digest:
            lines = ["**AI Updates Daily Digest**"]
            for service, entries in grouped.items():
                lines.append(f"\n## {service}")
                lines.extend(entries[:20])
            try:
                send_digest(cfg.webhook_digest, lines)
            except Exception as exc:
                print(f"[warn] digest send failed: {exc}")
                return
        else:
            for service, entries in grouped.items():
                webhook = _service_webhook(cfg, service)
                if not webhook:
                    continue
                lines = [f"**Daily Digest: {service}**"] + entries[:20]
                try:
                    send_digest(webhook, lines)
                except Exception as exc:
                    print(f"[warn] digest send failed for {service}: {exc}")
                    continue

        for r in rows:
            store.mark_digest_sent(r["fingerprint"])
    finally:
        store.close()


def run_once_cli() -> None:
    run_once()


def run_digest_cli() -> None:
    run_digest()


def run_maintenance(action: str) -> None:
    cfg = Config.from_env()
    store = Store(cfg.db_path)
    try:
        if action == "drop_unsent_digest":
            deleted = store.delete_unsent_digest_items()
            print(f"[info] deleted unsent digest items: {deleted}")
            return
        if action == "reset_all":
            store.reset_all()
            print("[info] reset all update history")
            return
        raise ValueError(f"unknown maintenance action: {action}")
    finally:
        store.close()


def run_maintenance_cli() -> None:
    action = os.getenv("MAINTENANCE_ACTION", "drop_unsent_digest").strip().lower()
    run_maintenance(action)
