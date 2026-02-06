from __future__ import annotations

import json
from typing import Any

import httpx

from .models import Summary, UpdateItem


def heuristic_importance(item: UpdateItem) -> str:
    t = (item.title + " " + item.body).lower()
    high_terms = ["breaking", "deprec", "price", "billing", "security", "removed"]
    medium_terms = ["new", "release", "model", "cli", "api"]
    if any(k in t for k in high_terms):
        return "high"
    if any(k in t for k in medium_terms):
        return "medium"
    return "low"


def _fallback_summary(item: UpdateItem) -> Summary:
    text = item.body[:700] if item.body else item.title
    bullets = [
        f"更新元: {item.source_id}",
        f"要点: {text[:120]}...",
        f"公開: {item.published_at.date().isoformat()}",
    ]
    return Summary(
        headline=item.title,
        bullets=bullets,
        importance=heuristic_importance(item),
        topic="release-note",
    )


def summarize_with_openai(api_key: str, model: str, item: UpdateItem) -> Summary:
    prompt = {
        "role": "user",
        "content": (
            "次の更新情報を日本語で要約してください。"
            "厳密にJSONで返してください。"
            "スキーマ: {headline: string, bullets: [string,string,string], importance: high|medium|low, topic: string}.\n"
            f"title: {item.title}\n"
            f"url: {item.url}\n"
            f"published_at: {item.published_at.isoformat()}\n"
            f"body: {item.body[:4000]}"
        ),
    }
    body: dict[str, Any] = {
        "model": model,
        "input": [prompt],
        "text": {"format": {"type": "json_object"}},
    }
    with httpx.Client(timeout=30) as client:
        res = client.post(
            "https://api.openai.com/v1/responses",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=body,
        )
        res.raise_for_status()
        data = res.json()
    text = data.get("output", [{}])[0].get("content", [{}])[0].get("text", "{}")
    parsed = json.loads(text)
    return Summary(
        headline=parsed["headline"],
        bullets=list(parsed["bullets"])[:3],
        importance=parsed.get("importance", heuristic_importance(item)),
        topic=parsed.get("topic", "release-note"),
    )


def summarize(item: UpdateItem, api_key: str | None, model: str) -> Summary:
    if not api_key:
        return _fallback_summary(item)
    try:
        return summarize_with_openai(api_key, model, item)
    except Exception:
        return _fallback_summary(item)
