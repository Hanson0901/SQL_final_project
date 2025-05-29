from flask import Flask, request, abort
from flask_cors import CORS
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
    QuickReplyItem,
    FlexMessage,
    FlexContainer,
    PushMessageRequest
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent, PostbackEvent

import json
from datetime import datetime
sport={
    "NBA":1,
    "F1":2,
    "MLB":3,
    "CPBL":4,
    "BWF":5
}

reverse_sport = {v: k for k, v in sport.items()}

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
CORS(app, origins=["https://cgusqlpj.ddns.net:2222"])  # 只允許你的前端來源
# 設定 CORS，允許來自特定來源的請求
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
Type=""
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
    global Type
    user_id = event.source.user_id
    print(f"User ID: {user_id}")
    
    if event.message and hasattr(event.message, "text"):
        Message = event.message.text.strip()  # 移除前後空白
        print(f"Received message: {Message}")
        # 用戶資料庫處理
        handle_user_data(user_id, Message, event)
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
            
                
            elif previous_message == "Feed Back" and Message in sport.keys():
                # 處理賽事選擇
                previous_message = "Feed Backing"  # 重設狀態
                self_reply(event, f"您選擇的賽事種類是：{Message}\n請輸入您的回報內容(限一個文字框):")
                Type = Message
            
            elif previous_message == "Feed Backing":
                # 處理回報內容
                previous_message = ""
                try:
                    today = datetime.now().strftime("%Y-%m-%d")
                    print("f_type:", sport[Type])
                    insert_sql = """
                        INSERT INTO feedbacks (user_id, f_type, content, send_date,f_time,f_status)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_sql, (user_id, sport[Type], Message, today, datetime.now().strftime("%H:%M"), "未處理"))
                    db.commit()
                    print("回報內容已儲存")
                    #self_reply(event, "感謝您的回報！")
                except Exception as e:
                    print(f"資料庫操作錯誤: {e}")
                    db.rollback()
                reply = TextMessage(text=f"感謝您的回報：{Message}\n我們會儘快處理您的意見！")
                self_reply(event, reply.text)


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
            elif Message == '我是屁眼':
                   with ApiClient(configuration) as api_client:
                        line_bot_api = MessagingApi(api_client)
                        send_admin_flex(line_bot_api, event.reply_token, rating=0)
                
            else:
                # 預設回應
                self_reply(event, f"收到訊息：{Message}")
                

            
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

@app.route('/linebot/claim', methods=['POST'])
def claim_feedback():
    data = request.get_json()
    print("收到訊息")
    print(data)  # 你可以印出收到的內容
    
    #傳送給該uid的使用者
    user_id = data.get('uid')
    content= data.get('text')
    type = data.get('type')
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.push_message(
        PushMessageRequest(
            to=user_id,
            messages=[TextMessage(text=f"您的意見反映：\n分類:{reverse_sport[type]}\n內容{content}]\n已被認領並進入處理中，感謝您的回饋！")]
            )
        )
    return "OK"




@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    print(f"📩 收到 postback：{data}")

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        if data.startswith("rating="):
            score = int(data.split("=")[1])
            send_admin_flex(line_bot_api, event.reply_token, rating=score)


def send_admin_flex(line_bot_api, reply_token, rating):
    # ⭐ 使用 Unicode 星星表情作為 Text 元件，避免 ... 問題
    star_row = []
    for i in range(1, 6):
        star_row.append({
            "type": "text",
            "text": "⭐" if i <= rating else "☆",
            "size": "xl",
            "align": "center",
            "action": {
                "type": "postback",
                "data": f"rating={i}"
            },
            "flex": 1
        })

    admin_flex = {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": "https://i.postimg.cc/fLSSMrpQ/Manager.png",
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "我是管理者",
                    "weight": "bold",
                    "size": "xxl",
                    "margin": "none"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "sm",
                    "margin": "md",
                    "contents": star_row
                },
                {
                    "type": "text",
                    "text": f"目前評分：{rating}.0",
                    "margin": "md",
                    "size": "sm",
                    "color": "#666666"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "營業時間",
                                    "color": "#aaaaaa",
                                    "size": "sm",
                                    "flex": 3
                                },
                                {
                                    "type": "text",
                                    "text": "10:00 - 23:00",
                                    "wrap": True,
                                    "color": "#666666",
                                    "size": "sm",
                                    "flex": 8
                                }
                            ]
                        },
                        {
                            "type": "text",
                            "text": "是否要進入管理者介面？",
                            "margin": "md",
                            "size": "sm",
                            "color": "#444444"
                        }
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "horizontal",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "height": "sm",
                    "action": {
                        "type": "uri",
                        "label": "進入",
                        "uri": "https://cgusqlpj.ddns.net:2222/"
                    },
                    "flex": 2
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "不要",
                        "text": "取消進入管理者"
                    },
                    "flex": 2
                }
            ],
            "flex": 0
        }
    }

    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=[FlexMessage(alt_text="管理者模式與評分功能", contents=FlexContainer.from_json(json.dumps(admin_flex)))]
        )
    )

# weichang.ddns.net
# http://cgusqlpj.ddns.net/phpmyadmin
if __name__ == "__main__":
    context = (
        "/etc/letsencrypt/live/cgusqlpj.ddns.net/fullchain.pem",
        "/etc/letsencrypt/live/cgusqlpj.ddns.net/privkey.pem",
    )
    app.run(host="0.0.0.0", port=928, ssl_context=context)

# 80 8080 21 22 20 433 443 59...不要用
