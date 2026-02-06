from __future__ import annotations

from collections import defaultdict

from .collectors import collect_source
from .config import Config
from .dispatchers.discord import send_digest, send_immediate
from .normalize import normalize
from .sources import SOURCES
from .store import Store
from .summarizer import summarize

_IMPORTANCE_ORDER = {"low": 1, "medium": 2, "high": 3}


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
    min_level = _IMPORTANCE_ORDER.get(cfg.immediate_min_importance, 3)

    try:
        for source in SOURCES:
            raws = collect_source(source, cfg.user_agent)
            for raw in raws:
                item = normalize(raw)
                if store.is_seen(item.fingerprint):
                    continue
                store.add_update(item)
                summary = summarize(item, cfg.openai_api_key, cfg.openai_model)
                store.add_summary(item.fingerprint, summary)

                if _IMPORTANCE_ORDER.get(summary.importance, 1) < min_level:
                    continue
                webhook = _service_webhook(cfg, item.service)
                if webhook:
                    send_immediate(webhook, item, summary)
                    store.mark_immediate_sent(item.fingerprint)
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
            send_digest(cfg.webhook_digest, lines)
        else:
            for service, entries in grouped.items():
                webhook = _service_webhook(cfg, service)
                if not webhook:
                    continue
                lines = [f"**Daily Digest: {service}**"] + entries[:20]
                send_digest(webhook, lines)

        for r in rows:
            store.mark_digest_sent(r["fingerprint"])
    finally:
        store.close()


def run_once_cli() -> None:
    run_once()


def run_digest_cli() -> None:
    run_digest()
