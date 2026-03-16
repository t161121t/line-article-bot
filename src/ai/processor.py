"""Claude API で記事の要約・タグ分類・スコアリングを行う"""
from __future__ import annotations

import json
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


SYSTEM_PROMPT = """\
あなたは技術記事のキュレーターです。
与えられた記事タイトルと URL をもとに、以下の JSON を返してください。
余計な説明は不要です。JSON のみを返してください。

{
  "summary": "記事の内容を3行（日本語）で要約",
  "tags": ["タグ1", "タグ2", ...],  // 言語・FW・分野など最大5件
  "score": 0.0   // 0〜1 の浮動小数点。interests に合致するほど高く
}
"""


def process_article(
    title: str,
    url: str,
    interests: list[str],
) -> dict:
    """
    Claude API で記事を処理し、要約・タグ・スコアを返す。

    Args:
        title: 記事タイトル
        url: 記事 URL
        interests: ユーザーの興味キーワードリスト

    Returns:
        dict with summary, tags, score
    """
    user_message = f"""\
記事タイトル: {title}
URL: {url}
ユーザーの興味キーワード: {', '.join(interests)}

上記の情報をもとに JSON を返してください。
"""
    client = get_client()
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",   # 高速・低コスト
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    text = message.content[0].text.strip()

    # コードブロックが付いている場合は除去
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        # パース失敗時はデフォルト値
        result = {"summary": text[:200], "tags": [], "score": 0.0}

    # 型の保証
    result.setdefault("summary", "")
    result.setdefault("tags", [])
    result.setdefault("score", 0.0)
    result["score"] = float(result["score"])

    return result


if __name__ == "__main__":
    # 動作確認
    r = process_article(
        title="TypeScript 5.5 の新機能まとめ",
        url="https://example.com",
        interests=["TypeScript", "React", "AI"],
    )
    print(r)
