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


app = Flask(__name__)  # 初始化 Flask 應用程式
LOG = create_logger(app)  # 設定日誌紀錄器
line_bot_api = LineBotApi(
    "H+2kmGOeBxAqGHImKJpKJPLAtgAUqNa9TTAgY4wesr9kJbs14FJwNDaUFYL90z9Yh/MlJpQXU3A0nPdoDaVvyqZkQeV4fjfAb9Ez5YfOaOGP64bECzjzxeOHMUK/lTvCS009Elcpi6caa5hCeTPfIwdB04t89/1O/w1cDnyilFU="
)  # 初始化 LINE Bot API，帶入對應的 Channel Access Token
handler = WebhookHandler(
    "11882e6d285791298ae7897a1445ac3c"
)  # 初始化 Webhook 處理器並設定 Channel Secret
sql_connect("localhost", 3306, "william", "Chang0928", "final_project")


@app.route("/", methods=["POST"])
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
    print(f"User ID: {user_id}")
    # 回覆收到的訊息並將訊息內容存成 username
    if event.message and hasattr(event.message, "text"):
        username = event.message.text
        print(f"Received message: {username}")
    # 將 user_id 和 username 寫入資料庫
    try:
        insert_sql = (
            f"INSERT INTO users (user_id, user_name) VALUES ('{user_id}', '{username}')"
        )
        cursor.execute(insert_sql)
        db.commit()  # 提交到資料庫
        print("User saved successfully")
    except Exception as e:
        print(f"Error saving user: {e}")


# weichang.ddns.net
# http://cgusqlpj.ddns.net/phpmyadmin
if __name__ == "__main__":
    context = (
        "/etc/letsencrypt/live/cgusqlpj.ddns.net/fullchain.pem",
        "/etc/letsencrypt/live/cgusqlpj.ddns.net/privkey.pem",
    )
    app.run(host="0.0.0.0", port=928, ssl_context=context)

# 80 8080 21 22 20 433 443 59...不要用
