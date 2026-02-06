from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .models import Service

SourceKind = Literal["html", "github_releases"]


@dataclass(frozen=True, slots=True)
class Source:
    id: str
    service: Service
    label: str
    kind: SourceKind
    url: str


SOURCES: list[Source] = [
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
    Source(
        id="gemini_api_changelog",
        service="gemini",
        label="Gemini API Changelog",
        kind="html",
        url="https://ai.google.dev/gemini-api/docs/changelog",
    ),
    Source(
        id="gemini_cli_releases",
        service="gemini",
        label="Gemini CLI Releases",
        kind="github_releases",
        url="https://api.github.com/repos/google-gemini/gemini-cli/releases",
    ),
    Source(
        id="claude_code_release_notes",
        service="claude",
        label="Claude Code Release Notes",
        kind="html",
        url="https://docs.anthropic.com/en/release-notes/claude-code",
    ),
    Source(
        id="claude_code_github_releases",
        service="claude",
        label="Claude Code GitHub Releases",
        kind="github_releases",
        url="https://api.github.com/repos/anthropics/claude-code/releases",
    ),
]
