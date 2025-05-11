# LINE BOT + Gemini + 股票查詢功能

本專案是一個使用 LINE Messaging API 串接 Google Gemini AI 的聊天機器人，支援：

- AI 對話生成（使用 Gemini 1.5 Pro）
- 股票查詢（輸入：查詢2330）
- 儲存歷史訊息、GET/DELETE API
- 支援圖片、貼圖、影片、位置訊息
- Render 雲端部署

## 🔗 測試網址
Render Webhook：https://linebot-2jq4.onrender.com/callback  
GitHub Repo：https://github.com/s1111547/LineBot

## ✅ 使用方式
- LINE 加入 BOT 好友後傳送文字訊息
- 傳「查詢2330」即可查詢台積電股價
- 可用 Postman 測試 GET/DELETE `/history`

## 📁 專案結構
app.py # 主程式
requirements.txt # 套件清單
Procfile # Render 啟動設定
.render.yaml # Render 自動部署設定
history.json # 對話紀錄（會自動建立）
