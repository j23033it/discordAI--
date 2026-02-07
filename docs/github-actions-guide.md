# GitHub Actions 運用ガイド

このドキュメントは、本リポジトリの GitHub Actions の使い方をまとめた専用ガイドです。

## 対象ワークフロー
- `AI Updates Polling`
- `AI Updates Daily Digest`
- `AI Updates Preview Notification`
- `AI Updates Maintenance`

## 事前準備
GitHub Repository Secrets に以下を設定します。
- `DISCORD_WEBHOOK_OPENAI`
- `DISCORD_WEBHOOK_GEMINI`
- `DISCORD_WEBHOOK_CLAUDE`
- `DISCORD_WEBHOOK_DIGEST` (任意)
- `GEMINI_API_KEY` (`SUMMARY_PROVIDER=gemini` の場合)
- `OPENAI_API_KEY` (`SUMMARY_PROVIDER=openai` の場合)

## 1. AI Updates Polling
- 役割: 公式ソースを巡回し、新着のみ即時通知する
- 実行タイミング: 30分ごとの定期実行 + 手動実行
- ワークフロー定義: `.github/workflows/polling.yml`

手動実行手順:
1. `Actions` → `AI Updates Polling`
2. `Run workflow` を実行
3. `Run polling` ステップ成功を確認

通知が来ない主な理由:
- 新着がない（既読DBで重複除外）
- Webhook未設定
- APIキー・クォータエラー

## 2. AI Updates Daily Digest
- 役割: 未送信分を日次ダイジェストとしてまとめて通知
- 実行タイミング: 毎日 09:00 JST + 手動実行
- ワークフロー定義: `.github/workflows/digest.yml`

手動実行手順:
1. `Actions` → `AI Updates Daily Digest`
2. `Run workflow` を実行
3. `Run digest` ステップ成功を確認

補足:
- `DISCORD_WEBHOOK_DIGEST` がある場合は1チャンネルへ集約
- 未設定の場合はサービス別Webhookへ送信

## 3. AI Updates Preview Notification
- 役割: 新着がなくてもUI確認用サンプル通知を送信
- 実行タイミング: 手動実行のみ
- ワークフロー定義: `.github/workflows/preview.yml`

手動実行手順:
1. `Actions` → `AI Updates Preview Notification`
2. `Run workflow` で `target` を選択
3. Discordで見た目・文面・リンク導線を確認

`target` の意味:
- `all`: 全サービス通知
- `openai` / `gemini` / `claude`: サービス別通知のみ

## 4. AI Updates Maintenance
- 役割: 既読DBのノイズ履歴を手動で整理する
- 実行タイミング: 手動実行のみ
- ワークフロー定義: `.github/workflows/maintenance.yml`

手動実行手順:
1. `Actions` → `AI Updates Maintenance`
2. `Run workflow` で `action` を選択
3. `Run maintenance` ステップ成功を確認

`action` の意味:
- `drop_unsent_digest`: 未送信ダイジェスト候補だけ削除（過去ノイズ整理に推奨）
- `reset_all`: 既読DBを全削除（全履歴リセット）

## トラブルシュート
1. 実行は成功だが通知ゼロ: 新着なしの可能性。`AI Updates Preview Notification` で表示確認を先に行う
2. 要約が英語になる: `SUMMARY_PROVIDER` と対応する API キーの設定を確認
3. 401/403/429 エラー: APIキー誤り、権限不足、無料枠/クォータ超過を確認
4. 過去の未和訳通知がノイズ: `AI Updates Maintenance` の `drop_unsent_digest` 実行後、`AI Updates Polling` を再実行
