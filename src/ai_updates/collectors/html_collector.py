from __future__ import annotations

import re
from datetime import datetime, timezone

from bs4 import BeautifulSoup

from ..models import RawItem
from ..sources import Source
from .http_utils import fetch_text


def _slugify(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9\s-]", "", text).strip().lower()
    s = re.sub(r"[\s_-]+", "-", s)
    return s[:60] or "update"


def _parse_date_from_text(text: str) -> datetime | None:
    patterns = [
        r"(20\\d{2})[-/](\\d{1,2})[-/](\\d{1,2})",
        r"(January|February|March|April|May|June|July|August|September|October|November|December)\\s+(\\d{1,2}),\\s*(20\\d{2})",
    ]
    m = re.search(patterns[0], text, flags=re.IGNORECASE)
    if m:
        y, mo, d = m.groups()
        try:
            return datetime(int(y), int(mo), int(d), tzinfo=timezone.utc)
        except ValueError:
            return None
    m = re.search(patterns[1], text, flags=re.IGNORECASE)
    if m:
        mon, d, y = m.groups()
        try:
            return datetime.strptime(f"{mon} {d} {y}", "%B %d %Y").replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


def _extract_sections(soup: BeautifulSoup) -> list[tuple[str, str, datetime | None]]:
    main = soup.find("main") or soup.find("article") or soup.body
    if not main:
        return []

    sections: list[tuple[str, str, datetime | None]] = []
    headers = main.find_all(["h2", "h3"])
    if not headers:
        text = " ".join(p.get_text(" ", strip=True) for p in main.find_all(["p", "li"])[:80])
        return [("Latest Update", text, None)] if text else []

    for h in headers[:20]:
        heading = h.get_text(" ", strip=True)
        parts: list[str] = []
        for sib in h.next_siblings:
            if getattr(sib, "name", None) in ["h2", "h3"]:
                break
            if getattr(sib, "name", None) in ["p", "li", "ul", "ol", "div"]:
                txt = sib.get_text(" ", strip=True)
                if txt:
                    parts.append(txt)
            if len(" ".join(parts)) > 2500:
                break
        body = " ".join(parts).strip()
        if not body:
            continue
        sections.append((heading, body, _parse_date_from_text(heading)))
    return sections


def collect(source: Source, user_agent: str) -> list[RawItem]:
    html = fetch_text(source.url, user_agent)
    soup = BeautifulSoup(html, "html.parser")

    page_title = soup.title.get_text(strip=True) if soup.title else source.label
    sections = _extract_sections(soup)
    if not sections:
        return []

    items: list[RawItem] = []
    for idx, (heading, body, published_at) in enumerate(sections):
        fragment = _slugify(heading)
        url = f"{source.url}#{fragment}-{idx}"
        items.append(
            RawItem(
                source_id=source.id,
                service=source.service,
                title=f"{heading} | {page_title}",
                url=url,
                published_at=published_at or datetime.now(timezone.utc),
                body=body,
            )
        )
    return items
