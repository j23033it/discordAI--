from __future__ import annotations

from ..models import RawItem
from ..sources import Source
from . import github_releases_collector, html_collector

"""ソース種別に応じて適切なコレクターへ委譲する入口。"""


def collect_source(source: Source, user_agent: str) -> list[RawItem]:
    # kind フィールドで処理先を切り替える。
    if source.kind == "html":
        return html_collector.collect(source, user_agent)
    if source.kind == "github_releases":
        return github_releases_collector.collect(source, user_agent)
    return []
