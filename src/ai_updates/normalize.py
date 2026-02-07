from __future__ import annotations

import hashlib
import re

from .models import RawItem, UpdateItem

"""収集した生データを、比較しやすい形式へ整えるモジュール。"""


def _clean_text(text: str) -> str:
    # 改行や連続スペースを1つに圧縮して差分ノイズを減らす。
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _fingerprint(source_id: str, title: str, url: str, body: str) -> str:
    # 重複判定に使うハッシュを作る。本文は先頭のみ使って過剰な差分を抑える。
    base = f"{source_id}|{title.lower()}|{url}|{body[:500].lower()}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def normalize(raw: RawItem) -> UpdateItem:
    # 表記ゆれを軽く正規化し、fingerprint を付与した UpdateItem を返す。
    title = _clean_text(raw.title)
    body = _clean_text(raw.body)
    return UpdateItem(
        source_id=raw.source_id,
        service=raw.service,
        title=title,
        url=raw.url,
        published_at=raw.published_at,
        body=body,
        fingerprint=_fingerprint(raw.source_id, title, raw.url, body),
    )
