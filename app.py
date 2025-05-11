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

# ✅ 金鑰設定（直接寫入）
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

def call_weather(location_name):
    try:
        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
        params = {
            "Authorization": "CWA-97E0911B-BE84-4E57-9338-EA5797B5C0AB",
            "locationName": location_name,
            "format": "JSON"
        }
        res = requests.get(url, params=params)
        data = res.json()["records"]["location"][0]["weatherElement"]
        wx = data[0]["time"][0]["parameter"]["parameterName"]
        pop = data[1]["time"][0]["parameter"]["parameterName"] + "%"
        minT = data[2]["time"][0]["parameter"]["parameterName"]
        maxT = data[4]["time"][0]["parameter"]["parameterName"]
        return f"🌤️ {location_name}天氣預報：\n- 狀況：{wx}\n- 降雨機率：{pop}\n- 溫度：{minT} ~ {maxT}°C\n資料來源：中央氣象局"
    except:
        return "⚠️ 無法取得天氣資訊，請確認城市名稱是否正確（如：台北市）"

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
    msg = event.message

    if isinstance(msg, TextMessage):
        user_msg = msg.text
        if "天氣" in user_msg:
            loc = user_msg.replace("天氣", "").strip()
            loc = loc if loc else "台北市"
            bot_reply = call_weather(loc)
        else:
            bot_reply = call_gemini(user_msg)

        line_bot_api.reply_message(event.reply_token, TextSendMessage(bot_reply))
        save_history(user_id, user_msg, bot_reply)

    elif isinstance(msg, StickerMessage):
        line_bot_api.reply_message(event.reply_token, TextSendMessage("收到貼圖 👍"))

    elif isinstance(msg, ImageMessage):
        line_bot_api.reply_message(event.reply_token, TextSendMessage("收到圖片 📷"))

    elif isinstance(msg, VideoMessage):
        line_bot_api.reply_message(event.reply_token, TextSendMessage("收到影片 🎥"))

    elif isinstance(msg, LocationMessage):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(f"收到位置：{msg.address}"))

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
