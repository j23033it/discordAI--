# GitHub Actions 運用ガイド

このドキュメントは、本リポジトリの GitHub Actions の使い方をまとめた専用ガイドです。

## 対象ワークフロー
- `AI Updates Polling`
- `AI Updates Preview Notification`
- `AI Updates Maintenance`

## 事前準備
GitHub Repository Secrets に以下を設定します。
- `DISCORD_WEBHOOK_OPENAI`
- `DISCORD_WEBHOOK_GEMINI`
- `DISCORD_WEBHOOK_CLAUDE`
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

## 2. AI Updates Preview Notification
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

## 3. AI Updates Maintenance
- 役割: 既読DBを全削除して通知状態をリセットする
- 実行タイミング: 手動実行のみ
- ワークフロー定義: `.github/workflows/maintenance.yml`

手動実行手順:
1. `Actions` → `AI Updates Maintenance`
2. `Run workflow` を実行
3. `Run maintenance` ステップ成功を確認

## トラブルシュート
1. 実行は成功だが通知ゼロ: 新着なしの可能性。`AI Updates Preview Notification` で表示確認を先に行う
2. 要約が英語になる: `SUMMARY_PROVIDER` と対応する API キーの設定を確認
3. 401/403/429 エラー: APIキー誤り、権限不足、無料枠/クォータ超過を確認
4. 通知状態を初期化したい: `AI Updates Maintenance` を実行し、`Run maintenance` ステップログを確認
