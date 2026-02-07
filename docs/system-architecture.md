# システムアーキテクチャ

## 1. 目的と全体像
このシステムは、OpenAI / Gemini / Claude Code の公式更新情報を定期収集し、重複を除外したうえで日本語要約して Discord に通知するバッチ型アプリケーションです。

主な処理責務は以下です。
- 収集: 公式サイトHTML・GitHub Releases API から更新情報を取得
- 正規化: 文字ノイズを整形し、重複判定用 fingerprint を生成
- 既読管理: SQLite で「通知済み相当」の更新履歴を保持
- 要約: OpenAI/Gemini で JSON 要約（失敗時はフォールバック）
- 配信: サービス別 Discord Webhook へ即時通知

## 2. 実行モード
- 通常実行: `ai_updates.main.run_once`
  - 収集から通知までの本処理
- プレビュー実行: `ai_updates.preview.run_preview`
  - 新着がなくても通知UI確認用のサンプル通知を送信
- メンテナンス実行: `ai_updates.main.run_maintenance`
  - 現在は既読・要約履歴の全削除（`reset_all`）

## 3. 処理フロー（通常実行）
`src/ai_updates/main.py` の `run_once` がエントリーポイントです。

1. 環境変数から設定を読み込む（`Config.from_env`）
2. SQLite ストアを初期化（`Store`）
3. `SOURCES` を順に巡回
4. ソースごとに `collect_source` で `RawItem` 一覧を取得
5. 各 `RawItem` を `normalize` で `UpdateItem` に変換
6. `Store.is_seen` で fingerprint 重複判定
7. 新規のみ `Store.add_update` で保存
8. `summarize` で `Summary` を生成（API失敗時はフォールバック）
9. `Store.add_summary` で要約保存
10. サービス別 webhook があれば `send_immediate` で通知
11. 送信成功後に `Store.mark_immediate_sent`
12. 終了時に `Store.close`

エラーハンドリング方針:
- ソース単位の失敗: そのソースをスキップし、他ソース継続
- アイテム単位の失敗: そのアイテムをスキップし、同ソース内の次へ継続
- DBクローズ: `finally` で必ず実行

## 4. src 配下ファイルの役割

### 4.1 `src/ai_updates/`
- `src/ai_updates/main.py`
  - 通常実行パイプライン、メンテナンス処理、CLI 用関数を提供
- `src/ai_updates/preview.py`
  - プレビュー通知のサンプル `UpdateItem` / `Summary` を作成し、Webhook 送信
- `src/ai_updates/config.py`
  - 環境変数を `Config` にマッピング（DB パス、要約プロバイダ、API キー、Webhook）
- `src/ai_updates/sources.py`
  - 監視対象ソース（ID、サービス、種類、URL）を静的定義
- `src/ai_updates/models.py`
  - `RawItem` / `UpdateItem` / `Summary` と型定義（`Service`, `Importance`）
- `src/ai_updates/normalize.py`
  - タイトル・本文の整形と fingerprint 生成
- `src/ai_updates/store.py`
  - SQLite 永続化層（既読判定、更新保存、要約保存、送信済み更新、履歴リセット）
- `src/ai_updates/summarizer.py`
  - OpenAI/Gemini 呼び分け、プロンプト生成、JSON 応答の安全パース、フォールバック要約
- `src/ai_updates/__init__.py`
  - パッケージ公開シンボル管理（現状は公開シンボルなし）

### 4.2 `src/ai_updates/collectors/`
- `src/ai_updates/collectors/__init__.py`
  - `Source.kind` に応じた collector ルーティング
- `src/ai_updates/collectors/html_collector.py`
  - HTML を取得して `h2/h3` セクション単位で本文抽出し `RawItem` 化
  - 見出し文字列から URL フラグメント生成、見出し日付の簡易抽出
- `src/ai_updates/collectors/github_releases_collector.py`
  - GitHub Releases API を取得し、最新リリース群を `RawItem` 化
- `src/ai_updates/collectors/http_utils.py`
  - HTTP テキスト取得と ISO8601 日付パースの共通ユーティリティ

### 4.3 `src/ai_updates/dispatchers/`
- `src/ai_updates/dispatchers/discord.py`
  - Discord Webhook 投稿処理
  - `Summary` を箇条書き形式に整形して通知本文を作成

## 5. データモデル
- `RawItem`
  - 収集直後の生データ（`source_id`, `service`, `title`, `url`, `published_at`, `body`）
- `UpdateItem`
  - 正規化後データ。`RawItem` に `fingerprint` を追加
- `Summary`
  - 通知表示用要約（`headline`, `bullets`, `importance`, `topic`）

`fingerprint` は `source_id + title + url + body先頭` を SHA-256 化して生成し、重複除外の主キーとして利用します。

## 6. 永続化（SQLite）
`src/ai_updates/store.py` で次の2テーブルを管理します。

- `seen_updates`
  - 更新本体と処理状態を保持
  - 主なカラム: `fingerprint`(PK), `first_seen_at`, `summarized_at`, `sent_immediate_at`
- `summaries`
  - 要約結果を保持
  - 主なカラム: `fingerprint`(PK/FK), `headline`, `bullets_json`(実装上は改行結合文字列), `importance`, `topic`

## 7. 外部依存と境界
- 収集境界
  - HTML: 対象サイト構造に依存（`BeautifulSoup` で抽出）
  - GitHub Releases: GitHub REST API 応答に依存
- 要約境界
  - OpenAI Responses API / Gemini GenerateContent API
  - APIキー未設定・失敗時はローカルフォールバック要約に自動退避
- 配信境界
  - Discord Incoming Webhook

## 8. 変更時の着眼点（保守・拡張）
- 新しい収集先を追加する場合
  1. `Source.kind` を決める（既存 `html` / `github_releases` か新種別か）
  2. `src/ai_updates/sources.py` に `Source` を追加
  3. 新種別なら collector 実装を追加し、`collectors/__init__.py` の分岐を拡張
- 新しい通知先を追加する場合
  1. dispatcher モジュールを追加
  2. `main.py` / `preview.py` から呼び出しを追加
- 要約品質調整をする場合
  - `summarizer.py` のプロンプト、`_summary_from_parsed` の補正ロジックを調整
- 重複判定を調整する場合
  - `normalize.py` の `_fingerprint` 材料を変更（過検知/取りこぼしのトレードオフに注意）
