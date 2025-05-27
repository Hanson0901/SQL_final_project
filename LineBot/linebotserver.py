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
sql_connect("localhost", 3306, "hanson0901", "Hanson940901", "final_project")


@app.route("/", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

previous_message = ""  # 儲存上一條訊息
@handler.add(MessageEvent)
def handle_message(event):
    user_id = event.source.user_id
    print(f"User ID: {user_id}")
    
    if event.message and hasattr(event.message, "text"):
        Message = event.message.text
        print(f"Received message: {Message}")
        if Message == "Feed Back":
            reply = TemplateSendMessage(
                alt_text='選擇種類',
                template=ButtonsTemplate(
                    title='選擇種類',
                    text='請點選下方按鈕輸入選擇',
                    actions=[
                        MessageAction(
                            label='NBA',
                            text='NBA'
                        )
                        ,
                        MessageAction(
                            label='F1',
                            text='F1'
                        ),
                        MessageAction(
                            label='MLB',
                            text='MLB'
                        ),
                        MessageAction(
                            label='CPBL',
                            text='CPBL'
                        ),
                        MessageAction(
                            label='BWF',
                            text='BWF'
                        )
                    ]
                )
            )
            line_bot_api.reply_message(
            event.reply_token,
            [reply]
            )
        elif Message == "及時比分":
            reply = TextSendMessage(text="正在查詢最新比分...")
            line_bot_api.reply_message(
                event.reply_token,
                [reply]
            )
        else:
            reply = TextSendMessage(text=f"收到訊息：{Message}")
            line_bot_api.reply_message(
                event.reply_token,
                [reply]
            )
        previous_message = Message  # 儲存當前訊息為上一條訊息
        # 先檢查使用者是否已存在
        try:
            check_sql = "SELECT user_id FROM users WHERE user_id = %s"
            cursor.execute(check_sql, (user_id,))
            result = cursor.fetchone()
            
            if not result:  # 如果資料庫沒有該使用者
                insert_sql = """
                    INSERT INTO users (user_id, user_name) 
                    VALUES (%s, %s)
                """
                cursor.execute(insert_sql, (user_id, Message))
                db.commit()
                print("新使用者已儲存")
                
                # 傳送歡迎訊息
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="歡迎新朋友！資料已儲存")
                )
            else:
                print("使用者已存在，不重複儲存")
                
        except Exception as e:
            print(f"資料庫操作錯誤: {e}")
            db.rollback()  # 回滾交易



# weichang.ddns.net
# http://cgusqlpj.ddns.net/phpmyadmin
if __name__ == "__main__":
    context = (
        "/etc/letsencrypt/live/cgusqlpj.ddns.net/fullchain.pem",
        "/etc/letsencrypt/live/cgusqlpj.ddns.net/privkey.pem",
    )
    app.run(host="0.0.0.0", port=928, ssl_context=context)

# 80 8080 21 22 20 433 443 59...不要用
