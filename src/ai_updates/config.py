from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Config:
    db_path: Path
    user_agent: str
    summary_provider: str
    openai_api_key: str | None
    openai_model: str
    gemini_api_key: str | None
    gemini_model: str
    webhook_openai: str | None
    webhook_gemini: str | None
    webhook_claude: str | None
    webhook_digest: str | None


    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            db_path=Path(os.getenv("DB_PATH", "data/updates.db")),
            user_agent=os.getenv("USER_AGENT", "discord-ai-updates/0.1 (+local)"),
            summary_provider=os.getenv("SUMMARY_PROVIDER", "openai").lower(),
            openai_api_key=os.getenv("OPENAI_API_KEY") or None,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            gemini_api_key=os.getenv("GEMINI_API_KEY") or None,
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite"),
            webhook_openai=os.getenv("DISCORD_WEBHOOK_OPENAI") or None,
            webhook_gemini=os.getenv("DISCORD_WEBHOOK_GEMINI") or None,
            webhook_claude=os.getenv("DISCORD_WEBHOOK_CLAUDE") or None,
            webhook_digest=os.getenv("DISCORD_WEBHOOK_DIGEST") or None,
        )
