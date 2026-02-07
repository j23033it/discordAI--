# Discord AI Update Notifier (MVP)

OpenAI / Gemini / Claude Code の公式更新情報を収集し、重複除去・日本語要約して Discord に通知する最小実装です。

## Features
- 公式ソース6件を監視（OpenAI, Gemini, Claude Code）
- 既読管理 + 重複除去（SQLite）
- 日本語要約（LLM API利用、未設定時フォールバック）
- Discordサービス別Webhook通知
- GitHub Actionsで定期実行

## Setup
1. Python 3.11+ を用意
2. 依存をインストール
   ```bash
   pip install -e .
   ```
3. `.env.example` を参考に GitHub Secrets/環境変数を設定
4. まずローカルで動作確認
   ```bash
   ai-updates-once
   ai-updates-digest
   ```

## What You Need To Do
1. Discordでチャンネルを作成
   - `#openai-updates`
   - `#gemini-updates`
   - `#claude-updates`
   - (任意) `#ai-digest`
2. 各チャンネルのWebhook URLを発行
3. GitHub repository secrets を設定
   - `DISCORD_WEBHOOK_OPENAI`
   - `DISCORD_WEBHOOK_GEMINI`
   - `DISCORD_WEBHOOK_CLAUDE`
   - `DISCORD_WEBHOOK_DIGEST` (任意)
   - `GEMINI_API_KEY` (Geminiで要約する場合)
   - `OPENAI_API_KEY` (OpenAIで要約する場合)
4. Actionsを手動実行して初回確認
   - `AI Updates Polling`
   - `AI Updates Daily Digest`
   - `AI Updates Preview Notification` (UI確認用)

## Environment Variables
- `DB_PATH` (default: `data/updates.db`)
- `USER_AGENT` (defaultあり)
- `SUMMARY_PROVIDER` (`gemini` or `openai`, default: `openai`)
- `OPENAI_API_KEY` (任意, 要約の品質向上用)
- `OPENAI_MODEL` (default: `gpt-4.1-mini`)
- `GEMINI_API_KEY` (任意, `SUMMARY_PROVIDER=gemini` で利用)
- `GEMINI_MODEL` (default: `gemini-2.5-flash-lite`)
- `DISCORD_WEBHOOK_OPENAI`
- `DISCORD_WEBHOOK_GEMINI`
- `DISCORD_WEBHOOK_CLAUDE`
- `DISCORD_WEBHOOK_DIGEST` (任意)

無料枠優先で使う場合は `SUMMARY_PROVIDER=gemini` と `GEMINI_API_KEY` を設定してください。

## Schedules (recommended)
- Polling: 30分毎（高信号ソース）
- Digest: 毎日 09:00 JST

## GitHub Actions Documentation
- 専用ドキュメント: `docs/github-actions-guide.md`

## Notes
- GitHub Actions private repo では実行時間課金に注意
