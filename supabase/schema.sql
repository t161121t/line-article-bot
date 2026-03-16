-- =============================================
-- 技術記事キュレーション LINE Bot - DB スキーマ
-- Supabase SQL Editor に貼り付けて実行してください
-- =============================================

-- 記事テーブル
CREATE TABLE IF NOT EXISTS articles (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title       TEXT NOT NULL,
    url         TEXT NOT NULL UNIQUE,   -- 重複排除キー
    source      TEXT NOT NULL,          -- 'zenn' | 'qiita' | 'hackernews'
    summary     TEXT,                   -- Claude API による3行要約
    tags        TEXT[] DEFAULT '{}',    -- AI 分類タグ
    score       FLOAT DEFAULT 0,        -- 興味スコア（0〜1）
    sent_at     TIMESTAMPTZ,            -- LINE 送信済み日時（NULL = 未送信）
    published_at TIMESTAMPTZ,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- URL に一意インデックス（upsert 用）
CREATE UNIQUE INDEX IF NOT EXISTS articles_url_idx ON articles(url);

-- スコア降順で未送信記事を取りやすくするインデックス
CREATE INDEX IF NOT EXISTS articles_score_sent_idx ON articles(score DESC, sent_at NULLS FIRST);

-- ユーザー設定テーブル（単一ユーザー想定 → id=1 固定で使う）
CREATE TABLE IF NOT EXISTS user_settings (
    id          INT PRIMARY KEY DEFAULT 1,
    interests   TEXT[] DEFAULT ARRAY['React', 'TypeScript', 'Python', 'Go', 'AI'],
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- デフォルト設定を挿入（なければ）
INSERT INTO user_settings (id, interests)
VALUES (1, ARRAY['React', 'TypeScript', 'Python', 'Go', 'AI', 'LLM'])
ON CONFLICT (id) DO NOTHING;

-- RLS は個人用なので無効化（必要に応じて有効化）
ALTER TABLE articles DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings DISABLE ROW LEVEL SECURITY;
