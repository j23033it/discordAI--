from __future__ import annotations

import json
from urllib.parse import quote
from typing import Any

import httpx

from .models import Summary, UpdateItem

"""要約処理を担当するモジュール。OpenAI/Gemini とフォールバックを切り替える。"""


_FALLBACK_BULLET_TEMPLATE = "要点: (要約取得失敗)"


def heuristic_importance(item: UpdateItem) -> str:
    # タイトルと本文のキーワードから重要度を簡易判定する。
    t = (item.title + " " + item.body).lower()
    high_terms = ["breaking", "deprec", "price", "billing", "security", "removed"]
    medium_terms = ["new", "release", "model", "cli", "api"]
    if any(k in t for k in high_terms):
        return "high"
    if any(k in t for k in medium_terms):
        return "medium"
    return "low"


def _fallback_summary(item: UpdateItem) -> Summary:
    # API未設定・失敗時でも通知できるよう、最小要約を生成する。
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


def _build_prompt(item: UpdateItem) -> str:
    # LLMに渡すプロンプト。JSON固定で返すように明示する。
    return (
        "次の更新情報を日本語で要約してください。"
        "厳密にJSONで返してください。"
        "スキーマ: {headline: string, bullets: [string,string,string], importance: high|medium|low, topic: string}.\n"
        f"title: {item.title}\n"
        f"url: {item.url}\n"
        f"published_at: {item.published_at.isoformat()}\n"
        f"body: {item.body[:4000]}"
    )


def _summary_from_parsed(parsed: dict[str, Any], item: UpdateItem) -> Summary:
    # レスポンスが欠けていても壊れないよう安全に値を補正する。
    importance = parsed.get("importance", heuristic_importance(item))
    if importance not in {"high", "medium", "low"}:
        importance = heuristic_importance(item)

    bullets = list(parsed.get("bullets", []))[:3]
    if not bullets:
        # 箇条書きが空なら、最低3行を埋めて通知体裁を保つ。
        bullets = [
            f"更新元: {item.source_id}",
            _FALLBACK_BULLET_TEMPLATE,
            f"公開: {item.published_at.date().isoformat()}",
        ]
    return Summary(
        headline=parsed.get("headline", item.title),
        bullets=bullets,
        importance=importance,
        topic=parsed.get("topic", "release-note"),
    )


def summarize_with_openai(api_key: str, model: str, item: UpdateItem) -> Summary:
    # OpenAI Responses API を使って JSON 要約を生成する。
    prompt = {
        "role": "user",
        "content": _build_prompt(item),
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
    # 想定パスから JSON 文字列を取り出し、Summary へ変換する。
    text = data.get("output", [{}])[0].get("content", [{}])[0].get("text", "{}")
    return _summary_from_parsed(json.loads(text), item)


def summarize_with_gemini(api_key: str, model: str, item: UpdateItem) -> Summary:
    # Gemini API でも同じスキーマで JSON 要約を取得する。
    body: dict[str, Any] = {
        "contents": [{"parts": [{"text": _build_prompt(item)}]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }
    encoded_model = quote(model, safe="")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{encoded_model}:generateContent?key={api_key}"
    with httpx.Client(timeout=30) as client:
        res = client.post(url, json=body)
        res.raise_for_status()
        data = res.json()
    text = (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text", "{}")
    )
    return _summary_from_parsed(json.loads(text), item)


def summarize(
    item: UpdateItem,
    provider: str,
    openai_api_key: str | None,
    openai_model: str,
    gemini_api_key: str | None,
    gemini_model: str,
) -> Summary:
    # 設定に応じて要約プロバイダを選択する。
    selected = provider.lower()

    if selected == "gemini":
        if not gemini_api_key:
            # APIキー未設定なら必ずフォールバックにする。
            return _fallback_summary(item)
        try:
            return summarize_with_gemini(gemini_api_key, gemini_model, item)
        except Exception:
            # 外部API失敗時もパイプラインを止めない。
            return _fallback_summary(item)

    if not openai_api_key:
        return _fallback_summary(item)
    try:
        return summarize_with_openai(openai_api_key, openai_model, item)
    except Exception:
        return _fallback_summary(item)
