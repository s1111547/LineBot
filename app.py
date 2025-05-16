from flask import Flask, request, abort, jsonify
from datetime import datetime
import json
import os
import requests
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, StickerMessage, ImageMessage,
    LocationMessage, VideoMessage, TextSendMessage, StickerSendMessage,
    ImageSendMessage, VideoSendMessage, LocationSendMessage, FlexSendMessage
)

app = Flask(__name__)

# ✅ 金鑰設定
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
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        res = requests.post(url, headers=headers, json=data)
        if res.status_code == 200:
            return res.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"❌ Gemini API 錯誤：{res.status_code}\n{res.text}"
    except Exception as e:
        return f"❌ 錯誤：{str(e)}"

def call_stock(stock_id):
    try:
        url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{stock_id}.tw&json=1&delay=0"
        res = requests.get(url)
        data = res.json()
        if not data["msgArray"]:
            url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=otc_{stock_id}.tw&json=1&delay=0"
            res = requests.get(url)
            data = res.json()
        if not data["msgArray"]:
            return "⚠️ 查無此股票代碼，請確認是否正確（如：2330）"

        info = data["msgArray"][0]
        name = info["n"]
        open_price = info["o"]
        now_price = info["z"]
        yesterday_price = info["y"]

        if now_price == "--" or yesterday_price == "--":
            return f"📈 {name} ({stock_id})\n- 開盤：{open_price} 元\n- 現價：{now_price} 元\n- ⚠️ 無法計算漲跌幅"

        change_percent = ((float(now_price) - float(yesterday_price)) / float(yesterday_price)) * 100
        change_symbol = "+" if change_percent >= 0 else ""
        return f"📈 {name} ({stock_id})\n- 開盤：{open_price} 元\n- 現價：{now_price} 元\n- 漲跌幅：{change_symbol}{change_percent:.2f}%"
    except:
        return "⚠️ 無法取得股票資訊，請稍後再試"

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
        user_msg = msg.text.strip().lower()

        if user_msg.startswith("查詢"):
            stock_id = user_msg.replace("查詢", "").strip()
            bot_reply = call_stock(stock_id)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(bot_reply))
            save_history(user_id, user_msg, bot_reply)

        elif user_msg in ["貼圖", "sticker"]:
            line_bot_api.reply_message(event.reply_token, StickerSendMessage(package_id="1", sticker_id="2"))

       elif user_msg in ["圖片", "image"]:
    line_bot_api.reply_message(event.reply_token, ImageSendMessage(
        original_content_url="https://i.imgur.com/uWg9ld2.jpg",  # ✅ 有效圖片
        preview_image_url="https://i.imgur.com/uWg9ld2.jpg"
    ))


        elif user_msg in ["影片", "video"]:
            line_bot_api.reply_message(event.reply_token, VideoSendMessage(
                original_content_url="https://download.samplelib.com/mp4/sample-5s.mp4",
                preview_image_url="https://i.imgur.com/G7PVYLF.jpg"
            ))

        elif user_msg in ["位置", "location"]:
            line_bot_api.reply_message(event.reply_token, LocationSendMessage(
                title="台大資工系館",
                address="台北市大安區羅斯福路四段1號",
                latitude=25.0173405,
                longitude=121.5397519
            ))

        elif user_msg in ["flex"]:
            flex_content = {
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": "https://i.imgur.com/G7PVYLF.jpg",
                    "size": "full",
                    "aspectRatio": "20:13",
                    "aspectMode": "cover"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": "這是 Flex Message", "weight": "bold", "size": "xl"},
                        {"type": "text", "text": "支援圖片與樣式排版！", "size": "md", "color": "#666666"}
                    ]
                }
            }
            line_bot_api.reply_message(event.reply_token, FlexSendMessage("Flex 範例", flex_content))

        else:
            bot_reply = call_gemini(user_msg)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(bot_reply))
            save_history(user_id, user_msg, bot_reply)

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
