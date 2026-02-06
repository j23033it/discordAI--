from __future__ import annotations

import hashlib
import re

from .models import RawItem, UpdateItem


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _fingerprint(source_id: str, title: str, url: str, body: str) -> str:
    base = f"{source_id}|{title.lower()}|{url}|{body[:500].lower()}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def normalize(raw: RawItem) -> UpdateItem:
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
