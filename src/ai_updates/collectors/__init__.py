from __future__ import annotations

from ..models import RawItem
from ..sources import Source
from . import github_releases_collector, html_collector


def collect_source(source: Source, user_agent: str) -> list[RawItem]:
    if source.kind == "html":
        return html_collector.collect(source, user_agent)
    if source.kind == "github_releases":
        return github_releases_collector.collect(source, user_agent)
    return []
