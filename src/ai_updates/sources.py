from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .models import Service

"""監視対象ソースの定義。"""

SourceKind = Literal["html", "github_releases"]


@dataclass(frozen=True, slots=True)
class Source:
    # 収集先を表す設定オブジェクト。
    id: str
    service: Service
    label: str
    kind: SourceKind
    url: str


SOURCES: list[Source] = [
    # OpenAI
    Source(
        id="openai_chatgpt_release_notes",
        service="openai",
        label="OpenAI ChatGPT Release Notes",
        kind="html",
        url="https://help.openai.com/en/articles/6825453-chatgpt-release-notes",
    ),
    Source(
        id="openai_codex_changelog",
        service="openai",
        label="OpenAI Codex Changelog",
        kind="html",
        url="https://developers.openai.com/codex/changelog",
    ),
    # Gemini
    Source(
        id="gemini_app_drops",
        service="gemini",
        label="Gemini App Drops",
        kind="html",
        url="https://gemini.google/gemini-drops/",
    ),
    Source(
        id="gemini_cli_release_notes",
        service="gemini",
        label="Gemini CLI Release Notes",
        kind="html",
        url="https://geminicli.com/docs/changelogs/",
    ),
    # Claude
    Source(
        id="claude_code_release_notes",
        service="claude",
        label="Claude Code Release Notes",
        kind="html",
        url="https://docs.anthropic.com/en/release-notes/claude-code",
    ),
]
