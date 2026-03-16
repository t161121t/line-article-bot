"""Zenn RSS フィードから最新記事を取得する"""
from __future__ import annotations

import feedparser
import requests
from datetime import datetime, timezone
from typing import Any


ZENN_RSS_URL = "https://zenn.dev/feed"


def fetch_articles(limit: int = 20) -> list[dict[str, Any]]:
    """
    Zenn RSS フィードから記事を取得する。

    Returns:
        list of dict with keys: title, url, source, published_at
    """
    feed = feedparser.parse(ZENN_RSS_URL)
    articles: list[dict[str, Any]] = []

    for entry in feed.entries[:limit]:
        published_at = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()

        articles.append({
            "title": entry.get("title", ""),
            "url": entry.get("link", ""),
            "source": "zenn",
            "published_at": published_at,
        })

    return articles


if __name__ == "__main__":
    import json
    results = fetch_articles(5)
    print(json.dumps(results, ensure_ascii=False, indent=2))
