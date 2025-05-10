from flask import Flask, request, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests
import json
import os

app = Flask(__name__)


LINE_CHANNEL_ACCESS_TOKEN = "DzoB3aZmgQl0OrqcAVdSUjNxBDqUJm/T5+/IWMndcXKVMIxmZmLrGmKobMMgFhTx21A1umlYpZYJU+35P3e4lxK/shefeSMX1h9wavHQLRn0N9PdZ/787lVZTvusfDIxXGeZvkgFE37tbf5XiQFhVgdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "9375813267d5e4606d479c6bed94f0b1"
GEMINI_API_KEY = "AIzaSyDeQ4Kgs4mU3u3ljONPdk0wd_SYoZk2m4w"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

HISTORY_FILE = "history.json"

# 初始化歷史紀錄
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)

def load_history():
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def call_gemini(user_input):
    url = "https://generativelanguage.googleapis.com/v1beta2/models/text-bison-001:generateText"
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    data = {
        "prompt": {"text": user_input},
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, params=params, json=data)
        if response.status_code == 200:
            return response.json()["candidates"][0]["output"]
        else:
            return "Gemini API 發生錯誤。"
    except:
        return "呼叫 Gemini 失敗。"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except Exception as e:
        return str(e)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text
    user_id = event.source.user_id

    # 呼叫 Gemini API 回應
    ai_response = call_gemini(user_msg)

    # 回覆訊息
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=ai_response)
    )

    # 儲存對話紀錄
    history = load_history()
    history.append({"user": user_msg, "bot": ai_response})
    save_history(history)

@app.route("/history", methods=["GET"])
def get_history():
    return jsonify(load_history())

@app.route("/history", methods=["DELETE"])
def delete_history():
    save_history([])
    return jsonify({"status": "deleted"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
