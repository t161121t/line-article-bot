# 📋 プロダクト概要

**プロダクト名：** 技術記事キュレーション LINE Bot

**一言説明：** 自分の技術的興味に合った記事を、毎朝LINEで届けてくれる個人用キュレーションBot

## 面接でのストーリー（30秒版）

> 毎日技術記事をチェックしたいけど情報が多すぎて追えなかったので、自分専用のLINE Botを作りました。Zenn・Qiita・HackerNewsから記事を収集してClaude APIで要約・スコアリングし、毎朝上位3件だけLINEに届きます。GitHub Actionsで完全自動化しているのでサーバー費用もゼロです。

---

# ✅ 要件定義

## 背景・課題

- Zenn / Qiita / HackerNewsを毎日チェックするのが面倒
- 情報が多すぎて、自分に関係ある記事を見逃してしまう
- RSSリーダーは能動的に開かないと見れない → LINEなら確実に目に入る

## ターゲットユーザー

自分自身（個人用・単一ユーザー）

## やること / やらないこと

| やること ✅ | やらないこと ❌ |
| --- | --- |
| Zenn / Qiita / HN から記事収集 | 複数ユーザー対応 |
| Claude API で要約・タグ分類 | 管理画面・設定UI |
| 興味スコアで上位3件を選定 | ユーザー認証 |
| 毎朝LINEに自動送信 | 有料プラン・課金機能 |
| Supabaseで重複記事を排除 |  |
| GitHub Actionsで完全自動化 |  |
| LINEから興味設定を変更 |  |

## 非機能要件

- サーバー費用ゼロ（GitHub Actions活用）
- 自分の興味設定はLINEのメッセージで管理
- 重複記事は送らない

---

# 🛠️ 技術スタック

| レイヤー | 技術 | 理由 |
| --- | --- | --- |
| 言語 | Python | スクレイピング・AI処理との相性が良い |
| DB | Supabase | 認証・DB・APIが一体 |
| AI | Claude API | 日本語記事の要約精度が高い |
| 通知 | LINE Messaging API | Botで個人に送信 |
| 定期実行 | GitHub Actions | 無料・cronで毎日実行 |
| Webhookサーバー | FastAPI + Render | LINEからの設定変更を受け取る |

---

# 🏗️ システム設計

## アーキテクチャ

```text
[情報収集] → [AI処理] → [DB保存] → [LINE配信]
  毎日定時        要約・分類      Supabase      毎朝7時
```

## データフロー

```text
GitHub Actions (毎朝7時)
      ↓
Python スクリプト起動
      ↓
記事収集
  - Zenn RSS     → feedparser
  - Qiita API    → 公式API
  - HackerNews   → 公式API
      ↓
重複チェック (Supabase)
      ↓
Claude API で処理
  - 3行要約
  - タグ分類
  - 興味スコア算出
      ↓
Supabase に保存
      ↓
スコア上位3件を選定
      ↓
LINE Messaging API で送信
```

## DBテーブル設計

```sql
-- 記事テーブル
articles (
  id, title, url, source,
  summary,       -- AI 3行要約
  tags[],        -- AI分類タグ
  score,         -- 興味スコア
  sent_at,       -- LINE送信済みフラグ
  published_at
)

-- ユーザー設定テーブル
user_settings (
  id,
  interests[],   -- ["React", "TypeScript", "Go", "AI"]
  updated_at
)
```

---

# ⚙️ 機能一覧

## 1. 記事収集機能

- Zenn RSS フィードから最新記事を取得
- Qiita API から人気記事を取得
- HackerNews API からトップ記事を取得
- 取得済み記事はSupabaseでURLを使って重複排除

## 2. AI処理機能

- Claude API で記事を3行で要約
- タグを自動分類（言語 / フレームワーク / 分野）
- 興味キーワードと照合してスコアリング

## 3. LINE通知機能

- 毎朝7時にスコア上位3件を送信
- 送信フォーマット：タイトル・要約・URL・タグ
- 送信済み記事は再送しない

## 4. LINE Bot 対話機能（興味設定変更）

| コマンド | 動作 |
| --- | --- |
| `設定 React Go AI` | 興味タグを上書き更新 |
| `設定確認` | 現在の設定を表示 |

## 5. 自動化

- GitHub Actions で毎朝7時に自動実行（cron）
- 実行ログをGitHub Actionsで確認可能

---

# 🔄 ユーザーフロー

## フロー① 毎朝の記事受信

```text
毎朝7時（自動）
      ↓
GitHub Actions が起動
      ↓
Zenn / Qiita / HN から記事収集
      ↓
Supabase で重複チェック
      ↓
Claude API で要約・タグ分類・スコアリング
      ↓
スコア上位3件を選定
      ↓
LINEに通知 📱
```

## フロー② 興味設定の変更

```text
ユーザーがLINEで「設定 React Go AI」と送信
      ↓
LINE サーバーが Webhook で FastAPI に転送
      ↓
FastAPI がコマンドを解析
      ↓
Supabase の user_settings を更新
      ↓
LINEに「✅ 設定を更新しました」と返信
      ↓
翌朝から新しい設定で記事が届く 🌅
```

---

# 💰 コスト試算

| サービス | 無料枠 | 今回の使用量 | 判定 |
| --- | --- | --- | --- |
| GitHub Actions | 2,000分/月 | 約150分 | ✅ 余裕 |
| Supabase | DB 500MB | 数MB程度 | ✅ 余裕 |
| LINE Messaging API | 月500件まで無料 | 約90件 | ✅ 余裕 |
| Claude API | 従量課金（初回無料クレジットあり） | 約$0.01〜0.02/月 | ✅ ほぼ無料 |
| Render | 750時間/月 | 約720時間 | ⚠️ スリープ対策必要 |

**月額目安：ほぼ $0〜$0.05（数円〜数十円）**

---

# 📅 1週間実装スケジュール

## Day 1｜環境構築・記事収集

- [ ] GitHubリポジトリ作成
- [ ] Python環境構築（venv・ライブラリインストール）
- [ ] Supabase プロジェクト作成・`articles`テーブル作成
- [ ] Zenn RSS / Qiita API / HN API から記事取得スクリプト作成

## Day 2｜Supabase連携・重複排除

- [ ] 取得した記事をSupabaseに保存
- [ ] URLをキーにしたupsert（重複排除）実装
- [ ] 動作確認・デバッグ

## Day 3｜Claude API連携

- [ ] Anthropic APIキー取得・設定
- [ ] Claude APIで3行要約・タグ分類の実装
- [ ] 興味キーワードとのスコアリングロジック実装
- [ ] 上位3件の選定ロジック実装

## Day 4｜LINE Bot基礎

- [ ] LINE Developers でチャンネル作成
- [ ] LINE Messaging API でpush送信の実装
- [ ] メッセージフォーマットの整形
- [ ] 手動で送信テスト

## Day 5｜LINE Bot対話機能

- [ ] FastAPI でWebhookサーバー作成
- [ ] `設定 ...` コマンドの解析実装
- [ ] Supabaseの`user_settings`テーブル更新
- [ ] `設定確認` コマンドの実装

## Day 6｜デプロイ・自動化

- [ ] RenderにFastAPIサーバーをデプロイ
- [ ] UptimeRobotでスリープ対策
- [ ] GitHub Actionsでcron設定（毎朝7時）
- [ ] `.env` の設定をGitHub Secretsに移行
- [ ] エンドツーエンドで動作確認

## Day 7｜仕上げ・ドキュメント

- [ ] バグ修正・エラーハンドリング追加
- [ ] READMEを丁寧に書く（構成図・セットアップ手順）
- [ ] 実際に1日動かして動作確認
- [ ] デモ用スクリーンショット撮影

---

# 🎯 難易度目安

| Day | 内容 | 難易度 |
| --- | --- | --- |
| 1 | 環境構築・記事収集 | ⭐⭐ |
| 2 | DB連携 | ⭐⭐ |
| 3 | Claude API | ⭐⭐⭐ |
| 4 | LINE送信 | ⭐⭐ |
| 5 | Webhook対話 | ⭐⭐⭐ |
| 6 | デプロイ・自動化 | ⭐⭐⭐ |
| 7 | 仕上げ | ⭐ |
