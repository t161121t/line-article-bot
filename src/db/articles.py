"""記事テーブルの CRUD 操作"""
from __future__ import annotations

from typing import Any
from .client import get_client


def upsert_articles(articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    記事を upsert する（URL が重複していれば何もしない）。

    Args:
        articles: title, url, source, published_at を含む dict のリスト

    Returns:
        upsert 結果のリスト
    """
    if not articles:
        return []

    db = get_client()
    result = (
        db.table("articles")
        .upsert(articles, on_conflict="url", ignore_duplicates=True)
        .execute()
    )
    return result.data or []


def fetch_unprocessed(limit: int = 50) -> list[dict[str, Any]]:
    """summary が NULL（AI 未処理）の記事を取得する"""
    db = get_client()
    result = (
        db.table("articles")
        .select("*")
        .is_("summary", "null")
        .order("created_at", desc=False)
        .limit(limit)
        .execute()
    )
    return result.data or []


def update_article(article_id: str, data: dict[str, Any]) -> None:
    """記事フィールドを更新する（要約・タグ・スコアなど）"""
    db = get_client()
    db.table("articles").update(data).eq("id", article_id).execute()


def fetch_top_unsent(limit: int = 3) -> list[dict[str, Any]]:
    """スコア上位の未送信記事を取得する"""
    db = get_client()
    result = (
        db.table("articles")
        .select("*")
        .is_("sent_at", "null")
        .not_.is_("summary", "null")       # AI 処理済みのみ
        .order("score", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data or []


def mark_as_sent(article_ids: list[str]) -> None:
    """送信済みフラグ（sent_at）を付ける"""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    db = get_client()
    db.table("articles").update({"sent_at": now}).in_("id", article_ids).execute()
