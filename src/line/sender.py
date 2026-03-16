"""LINE Messaging API で記事を push 送信する"""
from __future__ import annotations

import os
from typing import Any

from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    PushMessageRequest,
    TextMessage,
)
from dotenv import load_dotenv

load_dotenv()


def _get_api() -> MessagingApi:
    config = Configuration(access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
    return MessagingApi(ApiClient(config))


def format_article_message(articles: list[dict[str, Any]]) -> str:
    """上位3件の記事をテキストメッセージにフォーマットする"""
    lines = ["📰 本日のおすすめ技術記事 Top3\n"]

    for i, article in enumerate(articles, 1):
        tags = " ".join(f"#{t}" for t in (article.get("tags") or [])[:3])
        lines.append(
            f"【{i}】{article['title']}\n"
            f"{article.get('summary', '（要約なし）')}\n"
            f"{tags}\n"
            f"🔗 {article['url']}\n"
        )

    return "\n".join(lines).strip()


def send_articles(articles: list[dict[str, Any]]) -> None:
    """
    スコア上位3件の記事を LINE に push 送信する。

    Args:
        articles: fetch_top_unsent() の結果
    """
    if not articles:
        print("[LINE] 送信する記事がありません")
        return

    user_id = os.environ["LINE_USER_ID"]
    text = format_article_message(articles)

    api = _get_api()
    api.push_message(
        PushMessageRequest(
            to=user_id,
            messages=[TextMessage(type="text", text=text)],
        )
    )
    print(f"[LINE] {len(articles)} 件の記事を送信しました")


if __name__ == "__main__":
    # 動作確認（ダミーデータ）
    dummy = [
        {
            "title": "テスト記事",
            "url": "https://example.com",
            "summary": "これはテストの要約です。\nAI が生成しました。\n3行目です。",
            "tags": ["TypeScript", "React"],
        }
    ]
    print(format_article_message(dummy))
