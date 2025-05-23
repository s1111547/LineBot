這是Line的好友碼@608ungju
# LINE 股票查詢互動機器人

## 簡介

本專案是一個使用 LINE Messaging API 開發的聊天機器人，旨在提供使用者即時的台灣證券交易所（TWSE）股票資訊查詢服務，同時支援豐富的互動功能，能夠處理多種使用者輸入的訊息類型。

## 功能

* **股票查詢：** 使用者可以透過文字指令查詢 TWSE 上市股票的即時資訊，包括開盤價、現價、漲跌幅等。
* **多樣化的訊息處理：** 能夠解析和回應包括文字、圖片、貼圖、位置資訊和影片等多種類型的使用者訊息，提供更豐富的互動體驗。
* **互動式對話：** Bot 可以根據使用者的輸入，提供引導式的回覆，例如詢問更多資訊以提供更精確的服務（例如，晚餐推薦）。
* **歷史紀錄管理：** 具備儲存使用者查詢歷史紀錄的功能，並提供查看和清除歷史紀錄的接口，方便使用者管理自己的查詢行為。

## 技術棧

* LINE Messaging API
* Flask (Python)
* TWSE 股票 API
* Python
* Postman (用於 API 測試)

## 運作流程

1.  使用者在 LINE 中傳送訊息給 Bot。
2.  LINE 透過 Webhook 將訊息傳遞給 Flask 伺服器。
3.  Flask 伺服器接收請求，並判斷訊息類型（輸入image、sticker、location、video和文字等）。
4.  如果訊息為股票查詢指令，則呼叫 TWSE 股票 API 獲取資料，並產生文字回覆。
5.  Bot 將回覆訊息傳送給使用者。
6.  所有訊息和查詢紀錄都會儲存於歷史紀錄中，並提供 API 進行查看和清除 (使用 Postman 測試)。（參考 PDF 第一頁流程圖）

## 使用範例

### 1. 股票查詢

使用者輸入：「查詢 2330」

Bot 回覆：
台積電(2330)

開盤: 991.0000元
現價: 998.0000元
漲跌幅: +0.50%


### 2. 多種類型訊息回復 (參考 PDF 第三、四頁)

* **文字：** Bot 可以回應文字訊息，並提供相關資訊或引導。
* **貼圖：** Bot 可以接收和發送 LINE 貼圖。
* **圖片：** Bot 可以接收和處理圖片訊息。
* **位置：** Bot 可以接收使用者傳送的位置資訊。
* **影片：** Bot 可以接收使用者傳送的影片訊息。

## 介面展示

（這裡可以放入 LINE Bot 的截圖，例如 PDF 第二頁和第三、四頁的截圖）

## API 使用說明

### 1. 查看歷史紀錄

`GET /history`

使用 Postman 或其他 API 客戶端工具，向此端點發送 GET 請求，可以查看所有儲存的歷史紀錄。

### 2. 清除歷史紀錄

`DELETE /history`

向此端點發送 DELETE 請求，可以清除所有儲存的歷史紀錄。

## 專案作者

[陳重文/
https://github.com/s1111547/LineBot ]

## 備註

本專案僅供學習和參考，請勿用於商業用途。
