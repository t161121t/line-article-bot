"""HackerNews API からトップ記事を取得する"""
from __future__ import annotations

import requests
from datetime import datetime, timezone
from typing import Any


HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"


def fetch_item(item_id: int) -> dict[str, Any] | None:
    """HN の個別アイテムを取得する"""
    try:
        resp = requests.get(HN_ITEM_URL.format(item_id), timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def fetch_articles(limit: int = 20) -> list[dict[str, Any]]:
    """
    HackerNews API からトップ記事を取得する。
    外部リンクを持つ "story" 型のみを返す。

    Returns:
        list of dict with keys: title, url, source, published_at
    """
    resp = requests.get(HN_TOP_STORIES_URL, timeout=10)
    resp.raise_for_status()
    top_ids: list[int] = resp.json()

    articles: list[dict[str, Any]] = []
    fetched = 0

    for item_id in top_ids:
        if fetched >= limit:
            break

        item = fetch_item(item_id)
        if not item:
            continue

        # "story" 型かつ外部 URL があるものだけ
        if item.get("type") != "story" or not item.get("url"):
            continue

        published_at = None
        if item.get("time"):
            published_at = datetime.fromtimestamp(item["time"], tz=timezone.utc).isoformat()

        articles.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "source": "hackernews",
            "published_at": published_at,
        })
        fetched += 1

    return articles


if __name__ == "__main__":
    import json
    results = fetch_articles(5)
    print(json.dumps(results, ensure_ascii=False, indent=2))
