from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from flask.logging import create_logger
from linebot.models import (
    MessageEvent,
    TextSendMessage,
    PostbackEvent,
    URIAction,
    TemplateSendMessage,
    ButtonsTemplate,
    MessageAction,
)
import pymysql
import re


def sql_connect(host, port, user, passwd, database):
    global db, cursor
    try:
        db = pymysql.connect(
            host=host, user=user, passwd=passwd, database=database, port=int(port)
        )
        print("連線成功")
        cursor = db.cursor()  # 創建一個與資料庫連線的游標(cursor)對象
        return True
    except pymysql.Error as e:
        print("連線失敗:", str(e))
        return False


def select(sql):
    cursor.execute(sql)  # 執行sql語句
    result = cursor.fetchall()  # 取得查詢結果
    result = list(result)
    for i in range(len(result)):
        result[i] = str(result[i])
        result[i] = re.sub(r"[(),\"']", "", result[i])  # 移除結果中的特殊字元
    return result


def insert(sql):
    cursor.execute(sql)  # 執行sql語句
    db.commit()  # 提交交易，確認寫入資料庫


app = Flask(__name__)  # 初始化 Flask 應用程式
LOG = create_logger(app)  # 設定日誌紀錄器
line_bot_api = LineBotApi(
    "H+2kmGOeBxAqGHImKJpKJPLAtgAUqNa9TTAgY4wesr9kJbs14FJwNDaUFYL90z9Yh/MlJpQXU3A0nPdoDaVvyqZkQeV4fjfAb9Ez5YfOaOGP64bECzjzxeOHMUK/lTvCS009Elcpi6caa5hCeTPfIwdB04t89/1O/w1cDnyilFU="
)  # 初始化 LINE Bot API，帶入對應的 Channel Access Token
handler = WebhookHandler(
    "11882e6d285791298ae7897a1445ac3c"
)  # 初始化 Webhook 處理器並設定 Channel Secret
sql_connect("localhost", 3306, "william", "Chang0928", "City")


# 設定 Webhook 接收的路徑和 HTTP 方法
@app.route("/", methods=["POST"])
def callback():
    signature = request.headers[
        "X-Line-Signature"
    ]  # 取得 Line Signature 用於驗證請求的合法性
    print("signature:", signature)
    body = request.get_data(as_text=True)  # 取得請求的內容
    LOG.info("Request body: " + body)  # 將請求內容記錄到 LOG 中
    try:
        handler.handle(body, signature)  # 使用 handler 處理接收到的事件
    except InvalidSignatureError:
        abort(400)  # 若 Line Signature 驗證失敗，則回傳 400 錯誤
    return "OK"  # 回傳 "OK" 表示處理完成且正常結束log.infoThis domain may be for sale!


# 處理 PostbackEvent 事件的函數
@handler.add(PostbackEvent)
def handle_postback(event):  # 當點選 rich menu 的按鈕後會觸發
    if event.postback.data == "action=input":  # 檢查是否為我們設定的 postback action
        # 取得使用者 user_id
        user_id = event.source.user_id
        # 將 user_id 加入 URL 中
        url = "https://cgusqlpj.ddns.net:443/wei/linebot/search.html?user_id=" + user_id

        message = TemplateSendMessage(
            alt_text="前往網頁",
            template=ButtonsTemplate(
                title="地址輸入",
                text="請點選下方按鈕輸入地址",  # 顯示在按鈕上方的訊息文字
                actions=[
                    URIAction(
                        label="前往填寫頁面", uri=url  # 按鈕名稱  # 點擊後導向的網址
                    )
                ],
            ),
        )
        # 回覆使用者訊息
        line_bot_api.reply_message(event.reply_token, message)


# 查詢個人資料按鈕
@handler.add(MessageEvent)
def echo(event):
    user_id = event.source.user_id  # 取得使用者的 user_id
    print("user_id =", user_id)

    if event.message.type == "text":
        stt = event.message.text  # 取得使用者輸入的文字
        sql = f"""SELECT city FROM city WHERE 1;"""  # 查詢所有城市
        addr = select(sql)  # 執行查詢
        if stt[0:3] in addr:  # 若輸入文字的第一個字在城市清單中，視為地址輸入完成
            line_bot_api.reply_message(event.reply_token, TextSendMessage("輸入完成"))

            sql = f"""UPDATE `userinformation` SET `addr` ='{stt}' WHERE `lineid` ='{user_id}';"""  # 更新地址
            insert(sql)

        elif stt == "查詢個人資料":  # 若使用者輸入 "查詢個人資料"
            # 查詢更新後的資料
            text = ""
            sql = f"""SELECT `name`, `addr` FROM `userinformation` WHERE `lineid` ='{user_id}';"""
            print(select(sql))
            text = (
                text
                + "姓名："
                + select(sql)[0].split(" ", 1)[0]
                + "\n"
                + "地址："
                + select(sql)[0].split(" ", 2)[1]
            )
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text))
        else:  # 其他情況當作名字
            line_bot_api.reply_message(event.reply_token, TextSendMessage("輸入地址"))

            # 新使用者將 user_id 和名字 stt 寫進資料庫
            sql = f"""INSERT INTO `userinformation`(`lineid`, `name`, `addr`) VALUES ('{user_id}', '{stt}', '');"""
            insert(sql)


@app.route("/web_page", methods=["POST"])
def web_page():
    input_text = request.form.get("input_text")  # 取得網頁回傳的內容
    id = request.form.get("id")  # 取得網頁回傳的 user_id

    # 建立按鈕樣板訊息
    template_message = TemplateSendMessage(
        alt_text="確認地址",  # 在無法顯示樣板訊息時的替代文字
        template=ButtonsTemplate(
            title="請確認地址是否正確：",  # 樣板標題
            text=input_text,  # 顯示的文字內容
            actions=[
                MessageAction(
                    label="正確",  # 按鈕顯示文字
                    text=input_text,  # 點擊按鈕時發送的訊息
                )
            ],
        ),
    )

    # 使用 LineBotApi 發送按鈕樣板訊息
    line_bot_api.push_message(id, template_message)

    return "ok"


# weichang.ddns.net
# http://cgusqlpj.ddns.net/phpmyadmin
if __name__ == "__main__":
    context = (
        "/etc/letsencrypt/live/cgusqlpj.ddns.net/fullchain.pem",
        "/etc/letsencrypt/live/cgusqlpj.ddns.net/privkey.pem",
    )
    app.run(host="0.0.0.0", port=8080, ssl_context=context)

# 80 8080 21 22 20 433 443 59...不要用
