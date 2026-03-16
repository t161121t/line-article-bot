"""
FastAPI Webhook サーバー
LINE Bot からの設定変更コマンドを受け取る

デプロイ: Render の Web Service に配置し、
LINE Developers の Webhook URL に https://<your-app>.onrender.com/webhook を設定する
"""
from __future__ import annotations

import hashlib
import hmac
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from db.settings import get_interests, update_interests

load_dotenv()

app = FastAPI(title="LINE Article Bot Webhook")
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])


def _get_api() -> MessagingApi:
    config = Configuration(access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
    return MessagingApi(ApiClient(config))


def _reply(reply_token: str, text: str) -> None:
    api = _get_api()
    api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=[TextMessage(type="text", text=text)],
        )
    )


@app.get("/")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/webhook")
async def webhook(
    request: Request,
    x_line_signature: str = Header(None),
) -> JSONResponse:
    body = await request.body()
    try:
        handler.handle(body.decode(), x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    return JSONResponse(content={"status": "ok"})


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent) -> None:
    text: str = event.message.text.strip()
    reply_token = event.reply_token

    # コマンド: 設定 React TypeScript Go
    if text.startswith("設定 ") or text.startswith("設定　"):
        raw = text[2:].strip()
        interests = [kw.strip() for kw in raw.replace("　", " ").split() if kw.strip()]
        if not interests:
            _reply(reply_token, "❌ キーワードを指定してください。例: 設定 React TypeScript Go")
            return
        update_interests(interests)
        joined = ", ".join(interests)
        _reply(reply_token, f"✅ 設定を更新しました！\n興味キーワード: {joined}")

    # コマンド: 設定確認
    elif text in ("設定確認", "設定を確認", "設定みせて"):
        interests = get_interests()
        if interests:
            joined = ", ".join(interests)
            _reply(reply_token, f"📋 現在の設定\n興味キーワード: {joined}")
        else:
            _reply(reply_token, "⚠️ 設定が見つかりませんでした。")

    # その他
    else:
        _reply(
            reply_token,
            "ℹ️ コマンド一覧\n"
            "・設定 <キーワード...>  → 興味タグを更新\n"
            "・設定確認  → 現在の設定を表示",
        )
