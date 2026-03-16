"""Qiita API から人気記事を取得する"""
from __future__ import annotations

import os
import requests
from typing import Any


QIITA_API_URL = "https://qiita.com/api/v2/items"


def fetch_articles(limit: int = 20) -> list[dict[str, Any]]:
    """
    Qiita API からトレンド記事を取得する。
    QIITA_API_TOKEN 環境変数があれば認証付きで取得（レート制限が緩い）。

    Returns:
        list of dict with keys: title, url, source, published_at
    """
    token = os.getenv("QIITA_API_TOKEN")
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    params = {
        "per_page": limit,
        "query": "stocks:>10",  # ストック数10以上の記事に絞る
    }

    response = requests.get(QIITA_API_URL, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    items = response.json()

    articles: list[dict[str, Any]] = []
    for item in items:
        articles.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "source": "qiita",
            "published_at": item.get("created_at"),
        })

    return articles


if __name__ == "__main__":
    import json
    from dotenv import load_dotenv
    load_dotenv()
    results = fetch_articles(5)
    print(json.dumps(results, ensure_ascii=False, indent=2))
