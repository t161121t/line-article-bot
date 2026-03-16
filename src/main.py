"""
メインバッチスクリプト
GitHub Actions から毎朝7時に呼び出される

実行フロー:
  1. Zenn / Qiita / HN から記事収集
  2. Supabase に upsert（重複排除）
  3. Claude API で未処理記事を要約・スコアリング
  4. スコア上位3件を LINE に送信
"""
from __future__ import annotations

import sys
import traceback

from dotenv import load_dotenv

load_dotenv()

from collectors import fetch_zenn, fetch_qiita, fetch_hackernews
from db import (
    upsert_articles,
    fetch_unprocessed,
    update_article,
    fetch_top_unsent,
    mark_as_sent,
    get_interests,
)
from ai import process_article
from line import send_articles


def collect_articles() -> int:
    """全ソースから記事を収集して Supabase に保存する"""
    print("📥 記事を収集しています...")

    all_articles = []
    try:
        zenn = fetch_zenn(20)
        print(f"  Zenn: {len(zenn)} 件")
        all_articles.extend(zenn)
    except Exception as e:
        print(f"  ⚠️ Zenn 収集エラー: {e}")

    try:
        qiita = fetch_qiita(20)
        print(f"  Qiita: {len(qiita)} 件")
        all_articles.extend(qiita)
    except Exception as e:
        print(f"  ⚠️ Qiita 収集エラー: {e}")

    try:
        hn = fetch_hackernews(20)
        print(f"  HackerNews: {len(hn)} 件")
        all_articles.extend(hn)
    except Exception as e:
        print(f"  ⚠️ HackerNews 収集エラー: {e}")

    saved = upsert_articles(all_articles)
    print(f"✅ {len(saved)} 件を DB に保存しました（重複除く）")
    return len(saved)


def process_with_ai() -> int:
    """未処理記事を Claude API で要約・タグ分類・スコアリングする"""
    print("\n🤖 AI 処理を開始します...")

    interests = get_interests()
    print(f"  興味キーワード: {', '.join(interests)}")

    unprocessed = fetch_unprocessed(limit=30)
    print(f"  未処理記事: {len(unprocessed)} 件")

    processed = 0
    for article in unprocessed:
        try:
            result = process_article(
                title=article["title"],
                url=article["url"],
                interests=interests,
            )
            update_article(article["id"], {
                "summary": result["summary"],
                "tags": result["tags"],
                "score": result["score"],
            })
            print(f"  ✓ [{result['score']:.2f}] {article['title'][:50]}")
            processed += 1
        except Exception as e:
            print(f"  ✗ エラー ({article['title'][:30]}): {e}")

    print(f"✅ {processed} 件の AI 処理が完了しました")
    return processed


def notify_line() -> None:
    """スコア上位3件を LINE に送信する"""
    print("\n📱 LINE に送信します...")

    top_articles = fetch_top_unsent(limit=3)
    if not top_articles:
        print("  送信する記事がありません")
        return

    send_articles(top_articles)
    mark_as_sent([a["id"] for a in top_articles])
    print(f"✅ {len(top_articles)} 件を送信・送信済みマーク完了")


def main() -> None:
    print("=" * 50)
    print("🚀 技術記事キュレーション Bot 起動")
    print("=" * 50)

    try:
        collect_articles()
        process_with_ai()
        notify_line()
        print("\n🎉 全処理が完了しました！")
    except Exception:
        print("\n❌ 予期しないエラーが発生しました:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
