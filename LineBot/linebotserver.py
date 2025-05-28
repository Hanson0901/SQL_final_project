from flask import Flask, request, abort
from flask.logging import create_logger
import pymysql
import re
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TemplateMessage,
    CarouselTemplate,
    CarouselColumn,
    MessageAction,
    TextMessage,
    QuickReply,
    QuickReplyItem
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent


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
CHANNEL_ACCESS_TOKEN = "H+2kmGOeBxAqGHImKJpKJPLAtgAUqNa9TTAgY4wesr9kJbs14FJwNDaUFYL90z9Yh/MlJpQXU3A0nPdoDaVvyqZkQeV4fjfAb9Ez5YfOaOGP64bECzjzxeOHMUK/lTvCS009Elcpi6caa5hCeTPfIwdB04t89/1O/w1cDnyilFU="
CHANNEL_SECRET = "11882e6d285791298ae7897a1445ac3c"
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)
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
'''@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    print(f"User ID: {user_id}")
    
    if event.message and hasattr(event.message, "text"):
        global previous_message 
        Message = event.message.text
        print(f"Received message: {Message}")

        if Message == "Feed Back":
            with ApiClient(configuration) as api_client:
                messaging_api = MessagingApi(api_client)

                quick_reply = QuickReply(
                items=[
                    QuickReplyItem(action=MessageAction(label="NBA", text="NBA")),
                    QuickReplyItem(action=MessageAction(label="F1", text="F1")),
                    QuickReplyItem(action=MessageAction(label="MLB", text="MLB")),
                    QuickReplyItem(action=MessageAction(label="CPBL", text="CPBL")),
                    QuickReplyItem(action=MessageAction(label="BWF", text="BWF")),
                ]
            )
            msg = TextMessage(
                text="請選擇賽事種類：",
                quick_reply=quick_reply
            )
            messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[msg]
                )
            )
        elif  previous_message=="Feed Back" and Message in ["NBA", "F1", "MLB", "CPBL", "BWF"]:
            with ApiClient(configuration) as api_client:
                messaging_api = MessagingApi(api_client)
                reply = TextMessage(text=f"您選擇的賽事種類是：{Message}\n請輸入您的回報內容")
                messaging_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[reply]
                    )
                )

            
        elif Message == "及時比分":
            with ApiClient(configuration) as api_client:
                messaging_api = MessagingApi(api_client)

                quick_reply = QuickReply(
                items=[
                    QuickReplyItem(action=MessageAction(label="NBA", text="NBA")),
                    QuickReplyItem(action=MessageAction(label="F1", text="F1")),
                    QuickReplyItem(action=MessageAction(label="MLB", text="MLB")),
                    QuickReplyItem(action=MessageAction(label="CPBL", text="CPBL")),
                    QuickReplyItem(action=MessageAction(label="BWF", text="BWF")),
                ]
            )
            msg = TextMessage(
                text="請選擇賽事種類：",
                quick_reply=quick_reply
            )
            messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[msg]
                )
            )
        elif  previous_message=="及時比分" and Message in ["NBA", "F1", "MLB", "CPBL", "BWF"]:
            with ApiClient(configuration) as api_client:
                messaging_api = MessagingApi(api_client)
                reply = TextMessage(text=f"您選擇的賽事種類是：{Message}\n正在查詢即時比分...")
                messaging_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[reply]
                    )
                )
        else:
            with ApiClient(configuration) as api_client:
                messaging_api = MessagingApi(api_client)
                reply = TextMessage(text=f"收到訊息：{Message}")
                messaging_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[reply]
                    )
                )
        previous_message = Message  # 更新上一條訊息
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
                with ApiClient(configuration) as api_client:
                    messaging_api = MessagingApi(api_client)
                    welcome_message = TextMessage(text="歡迎新朋友！資料已儲存")
                    messaging_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[welcome_message]
                        )
                    )
            
                
        except Exception as e:
            print(f"資料庫操作錯誤: {e}")
            db.rollback()  # 回滾交易
'''

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    global previous_message  # 明確宣告使用全域變數
    user_id = event.source.user_id
    print(f"User ID: {user_id}")
    
    if event.message and hasattr(event.message, "text"):
        Message = event.message.text.strip()  # 移除前後空白
        print(f"Received message: {Message}")
        
        try:
            # 訊息處理邏輯
            if Message == "Feed Back":
                # 處理回饋流程
                previous_message = "Feed Back"
                quick_reply = QuickReply(
                    items=[
                        QuickReplyItem(action=MessageAction(label="NBA", text="NBA")),
                        QuickReplyItem(action=MessageAction(label="F1", text="F1")),
                        QuickReplyItem(action=MessageAction(label="MLB", text="MLB")),
                        QuickReplyItem(action=MessageAction(label="CPBL", text="CPBL")),
                        QuickReplyItem(action=MessageAction(label="BWF", text="BWF"))
                    ]
                )
                self_reply(event, "請選擇賽事種類：", quick_reply)
                
            elif previous_message == "Feed Back" and Message in ["NBA", "F1", "MLB", "CPBL", "BWF"]:
                # 處理賽事選擇
                previous_message = ""  # 重設狀態
                self_reply(event, f"您選擇的賽事種類是：{Message}\n請輸入您的回報內容")
                
            elif Message == "及時比分":
                # 處理比分查詢
                quick_reply = QuickReply(
                    items=[
                        QuickReplyItem(action=MessageAction(label="NBA", text="NBA")),
                        QuickReplyItem(action=MessageAction(label="F1", text="F1")),
                        QuickReplyItem(action=MessageAction(label="MLB", text="MLB")),
                        QuickReplyItem(action=MessageAction(label="CPBL", text="CPBL")),
                        QuickReplyItem(action=MessageAction(label="BWF", text="BWF"))
                    ]
                )
                self_reply(event, "請選擇賽事種類：", quick_reply)
                
            elif Message in ["NBA", "F1", "MLB", "CPBL", "BWF"]:
                # 處理賽事比分顯示
                self_reply(event, f"您選擇的賽事種類是：{Message}\n正在查詢即時比分...")
                
            else:
                # 預設回應
                self_reply(event, f"收到訊息：{Message}")
                
            # 用戶資料庫處理
            handle_user_data(user_id, Message, event)
            
        except Exception as e:
            print(f"處理訊息時發生錯誤: {e}")
            db.rollback()

def self_reply(event, text, quick_reply=None):
    with ApiClient(configuration) as api_client:
        messaging_api = MessagingApi(api_client)
        msg = TextMessage(text=text, quick_reply=quick_reply)
        messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[msg]
            )
        )

def handle_user_data(user_id, message_text, event):
    try:
        check_sql = "SELECT user_id FROM users WHERE user_id = %s"
        cursor.execute(check_sql, (user_id,))
        result = cursor.fetchone()
        
        if not result:
            insert_sql = "INSERT INTO users (user_id, user_name) VALUES (%s, %s)"
            cursor.execute(insert_sql, (user_id, message_text))
            db.commit()
            print("新使用者已儲存")
            self_reply(event, "歡迎新朋友！資料已儲存")
            
    except Exception as e:
        print(f"資料庫操作錯誤: {e}")
        db.rollback()

# weichang.ddns.net
# http://cgusqlpj.ddns.net/phpmyadmin
if __name__ == "__main__":
    context = (
        "/etc/letsencrypt/live/cgusqlpj.ddns.net/fullchain.pem",
        "/etc/letsencrypt/live/cgusqlpj.ddns.net/privkey.pem",
    )
    app.run(host="0.0.0.0", port=928, ssl_context=context)

# 80 8080 21 22 20 433 443 59...不要用
