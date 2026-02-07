from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

"""環境変数からアプリ設定を読み込むモジュール。"""


@dataclass(slots=True)
class Config:
    # SQLite ファイルの保存先。
    db_path: Path
    # HTTP リクエストで送る User-Agent。
    user_agent: str
    # 要約に使うプロバイダ名（openai / gemini）。
    summary_provider: str
    # OpenAI 要約の認証情報とモデル。
    openai_api_key: str | None
    openai_model: str
    # Gemini 要約の認証情報とモデル。
    gemini_api_key: str | None
    gemini_model: str
    # サービス別 Discord Webhook。
    webhook_openai: str | None
    webhook_gemini: str | None
    webhook_claude: str | None


    @classmethod
    def from_env(cls) -> "Config":
        # 環境変数に値がない場合でも動くように、デフォルト値を持たせる。
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
        )
