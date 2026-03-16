# 📰 技術記事キュレーション LINE Bot

自分の技術的興味に合った記事を、毎朝 LINE で届けてくれる個人用キュレーション Bot。

```
Zenn / Qiita / HackerNews
        ↓ 収集
   Supabase (重複排除)
        ↓
  Claude API (要約・スコアリング)
        ↓
   LINE に毎朝 Top3 を配信
```

## 機能

- Zenn RSS / Qiita API / HackerNews API から毎日記事を収集
- Claude API（Haiku）で3行要約・タグ分類・興味スコア算出
- 毎朝7時に LINE へ上位3件を自動送信
- LINE から興味設定をリアルタイム変更
- GitHub Actions で完全自動化（サーバー費用ゼロ）

## ディレクトリ構成

```
line-article-bot/
├── src/
│   ├── main.py              # バッチ本体（GitHub Actions から実行）
│   ├── webhook.py           # FastAPI Webhook サーバー（Render にデプロイ）
│   ├── collectors/
│   │   ├── zenn.py          # Zenn RSS 収集
│   │   ├── qiita.py         # Qiita API 収集
│   │   └── hackernews.py    # HackerNews API 収集
│   ├── db/
│   │   ├── client.py        # Supabase クライアント
│   │   ├── articles.py      # 記事テーブル CRUD
│   │   └── settings.py      # ユーザー設定テーブル
│   ├── ai/
│   │   └── processor.py     # Claude API 処理
│   └── line/
│       └── sender.py        # LINE push 送信
├── supabase/
│   └── schema.sql           # テーブル定義（Supabase SQL Editor で実行）
├── .github/
│   └── workflows/
│       └── daily_batch.yml  # GitHub Actions cron
├── .env.example             # 環境変数テンプレート
├── .gitignore
└── requirements.txt
```

## セットアップ

### 1. 環境変数

`.env.example` をコピーして `.env` を作成し、各値を設定する。

```bash
cp .env.example .env
```

| 変数名 | 取得場所 |
|--------|---------|
| `SUPABASE_URL` | Supabase → Project Settings → API |
| `SUPABASE_SERVICE_KEY` | Supabase → Project Settings → API → service_role |
| `ANTHROPIC_API_KEY` | https://console.anthropic.com |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Developers → Messaging API |
| `LINE_CHANNEL_SECRET` | LINE Developers → Basic settings |
| `LINE_USER_ID` | LINE Developers → Messaging API → Your user ID |
| `QIITA_API_TOKEN` | https://qiita.com/settings/tokens（任意） |

### 2. Supabase テーブル作成

Supabase の SQL Editor で `supabase/schema.sql` を実行する。

### 3. Python 依存ライブラリのインストール

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. バッチの手動実行テスト

```bash
cd src
python main.py
```

### 5. Webhook サーバーを Render にデプロイ

1. Render で **Web Service** を作成
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `uvicorn src.webhook:app --host 0.0.0.0 --port $PORT`
4. 環境変数を Render の Environment に設定
5. デプロイ後の URL を LINE Developers の Webhook URL に設定

### 6. GitHub Actions Secrets の設定

リポジトリの Settings → Secrets and variables → Actions に `.env` の各値を登録する。

## LINE Bot コマンド

| コマンド | 動作 |
|--------|------|
| `設定 React TypeScript Go` | 興味キーワードを上書き更新 |
| `設定確認` | 現在の設定を表示 |

## コスト目安

| サービス | 月額 |
|--------|------|
| GitHub Actions | 無料（150分/月程度） |
| Supabase | 無料 |
| LINE Messaging API | 無料（~500通/月） |
| Claude API | ~$0.01〜0.05 |
| Render | 無料（スリープあり） |

**合計: ほぼ $0〜$0.05 / 月**

---

## 実際のセットアップ手順（ハマりポイントまとめ）

### Python バージョンについて

Python 3.14 では `pydantic-core` がビルドできないため、**Python 3.11** で仮想環境を作成する必要がある。

```bash
brew install python@3.11
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Supabase 接続

- **SUPABASE_URL**: `https://<project-ref>.supabase.co`（PostgreSQL接続文字列のホスト名から取得）
- **SUPABASE_SERVICE_KEY**: `sb_secret_...` 形式の新しいキー（Supabase Dashboard → Settings → API → service_role）
- テーブルは `supabase/schema.sql` の内容を Supabase Dashboard → SQL Editor で実行して作成

### Anthropic API

- console.anthropic.com でAPIキーを発行
- クレジットを追加しただけでは使えない場合がある → **Settings → Limits → Spending limits** を設定する必要あり
- クレジットと同じワークスペースで発行したAPIキーを使うこと

### LINE 設定

| 変数 | 取得場所 | 備考 |
|------|----------|------|
| `LINE_CHANNEL_ACCESS_TOKEN` | Messaging API タブ → Channel access token | 「Issue」ボタンで発行 |
| `LINE_CHANNEL_SECRET` | Basic settings タブ → Channel secret | |
| `LINE_USER_ID` | Messaging API タブ → Your user ID | `U` で始まる32文字。数字のみのIDは誤り |

### Qiita APIトークン

- qiita.com → 設定 → アプリケーション → 個人用アクセストークン → 発行
- スコープは `read_qiita` のみでOK
- 説明欄は空白でも問題なし
- 設定しなくてもZenn・HackerNewsのみで動作する

### 動作確認済み環境

```
Python: 3.11
supabase: 2.28.2（2.4.0では sb_secret_ 形式のキーが無効エラーになる）
anthropic: 0.83.0
linebot: v3系
```
