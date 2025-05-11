from flask import Flask, request, abort, jsonify
from datetime import datetime
import json
import os
import requests
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, StickerMessage, ImageMessage,
    LocationMessage, VideoMessage, TextSendMessage
)

app = Flask(__name__)


LINE_CHANNEL_ACCESS_TOKEN = "DzoB3aZmgQl0OrqcAVdSUjNxBDqUJm/T5+/IWMndcXKVMIxmZmLrGmKobMMgFhTx21A1umlYpZYJU+35P3e4lxK/shefeSMX1h9wavHQLRn0N9PdZ/787lVZTvusfDIxXGeZvkgFE37tbf5XiQFhVgdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "9375813267d5e4606d479c6bed94f0b1"
GEMINI_API_KEY = "AIzaSyD40Whl7xpRFjtyqpqBFge3z3WDVcF85O0"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

HISTORY_PATH = "history.json"

if not os.path.exists(HISTORY_PATH):
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

def call_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        res = requests.post(url, headers=headers, json=data)
        if res.status_code == 200:
            return res.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"❌ Gemini API 錯誤：{res.status_code}\n{res.text}"
    except Exception as e:
        return f"❌ 錯誤：{str(e)}"

def save_history(user_id, user_msg, bot_reply):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record = {
        "user_id": user_id,
        "user_msg": user_msg,
        "bot_reply": bot_reply,
        "timestamp": now
    }
    with open(HISTORY_PATH, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data.append(record)
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent)
def handle_message(event):
    user_id = event.source.user_id
    msg_type = event.message

    if isinstance(msg_type, TextMessage):
        user_msg = msg_type.text
        bot_reply = call_gemini(user_msg)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(bot_reply))
        save_history(user_id, user_msg, bot_reply)

    elif isinstance(msg_type, StickerMessage):
        line_bot_api.reply_message(event.reply_token, TextSendMessage("收到貼圖 👍"))

    elif isinstance(msg_type, ImageMessage):
        line_bot_api.reply_message(event.reply_token, TextSendMessage("收到圖片 📷"))

    elif isinstance(msg_type, VideoMessage):
        line_bot_api.reply_message(event.reply_token, TextSendMessage("收到影片 🎥"))

    elif isinstance(msg_type, LocationMessage):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(f"收到位置：{msg_type.address}"))

@app.route("/history", methods=["GET", "DELETE"])
def manage_history():
    if request.method == "GET":
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)

    elif request.method == "DELETE":
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return jsonify({"message": "歷史紀錄已清空"}), 200

if __name__ == "__main__":
    app.run()
