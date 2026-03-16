"""ユーザー設定テーブルの操作"""
from __future__ import annotations

from .client import get_client


def get_interests() -> list[str]:
    """現在の興味キーワードリストを取得する"""
    db = get_client()
    result = db.table("user_settings").select("interests").eq("id", 1).single().execute()
    return result.data.get("interests", []) if result.data else []


def update_interests(interests: list[str]) -> None:
    """興味キーワードリストを上書き更新する"""
    from datetime import datetime, timezone
    db = get_client()
    db.table("user_settings").upsert({
        "id": 1,
        "interests": interests,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).execute()
