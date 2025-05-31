from flask import Flask, request, abort
from flask_cors import CORS
from flask.logging import create_logger
from flask_apscheduler import APScheduler
import requests
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
    URIAction,
    TextMessage,
    QuickReply,
    QuickReplyItem,
    FlexMessage,
    FlexContainer,
    PushMessageRequest,
    ApiException
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent, PostbackEvent, FollowEvent

import json
from datetime import datetime, timedelta
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

class Config:
    SCHEDULER_API_ENABLED = True

app.config.from_object(Config())

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# 定時任務：每60秒請求 /remind
@scheduler.task('interval', id='call_remind', seconds=60)
def call_remind():
    try:
        # 假設本機運行在 5000 port
        resp = requests.get('https://cgusqlpj.ddns.net:928/remind')
        print("自動呼叫 /remind，狀態碼：", resp.status_code)
    except Exception as e:
        print("自動呼叫失敗：", e)

@app.route("/", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

previous_message = []  # 儲存上一條訊息
Type=""

@app.route("/remind", methods=["GET"])
def remind():
    # 確保資料庫連線仍然有效，若失效則重新連線
    try:
        db.ping(reconnect=True)
        print("資料庫連線正常")
        sql_connect("localhost", 3306, "hanson0901", "Hanson940901", "final_project")
    except:
        print("資料庫連線失效，重新連線中...")
        
    now = datetime.now()
    start_time = now+ timedelta(minutes=9)
    end_time = now + timedelta(minutes=10)

    print("🔍 查詢提醒範圍：", start_time.strftime("%Y-%m-%d %H:%M:%S"), "～", end_time.strftime("%Y-%m-%d %H:%M:%S"))

    try:
        cursor.execute("""
                SELECT rm.user_id, ms.game_no, ms.date, ms.time, st.sport_name,
                        t1.team_name AS team_a, t2.team_name AS team_b,
                        f1.match_name, f1.match_type
                FROM reminders rm
                JOIN matches_schedule ms ON rm.game_no = ms.game_no
                LEFT JOIN teams t1 ON ms.team_a = t1.team_id
                LEFT JOIN teams t2 ON ms.team_b = t2.team_id
                JOIN sport_type st ON ms.type = st.type
                LEFT JOIN f1_match_info f1 ON ms.game_no = f1.game_no
                WHERE CONCAT(ms.date, ' ', ms.time) BETWEEN %s AND %s
                        """, (start_time.strftime("%Y-%m-%d %H:%M:%S"), end_time.strftime("%Y-%m-%d %H:%M:%S")))
            # Make sure the 'date' and 'time' columns in your database are stored as strings in 'YYYY-MM-DD' and 'HH:MM:SS' format, or as DATETIME.



        results = cursor.fetchall()
        if not results:
            print("⚠️ 沒有要提醒的比賽")

        for row in results:
            user_id, game_no, date, time, sport_name, team_a, team_b, match_name, match_type = row

            if sport_name.lower() == "f1":
                    match_display = f"{match_name}（{match_type}）"
            else:
                    match_display = f"{team_a} vs {team_b}"

            cursor.execute("""
                    SELECT p.name
                    FROM match_platforms mp
                    JOIN platforms p ON mp.platform_id = p.platform_id
                    WHERE mp.game_no = %s
                """, (game_no,))
            platforms = [r[0] for r in cursor.fetchall()]
            platform_str = "、".join(platforms) if platforms else "無"

            message = f"📣 您預約的比賽即將開始！\n" \
                          f"📅 日期：{date} {time}\n" \
                          f"🎮 運動：{sport_name}\n" \
                          f"🏁 賽事：{match_display}\n"  \
                          f"📺 推薦平台：{platform_str}"

            print(f"🔔 推播至 {user_id}：{match_display}")

            try:
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    line_bot_api.push_message(
                        PushMessageRequest(
                            to=user_id,
                            messages=[TextMessage(text=message)]
                        )
                    )
                print("✅ 成功發送提醒\n" + "-" * 50)
            except ApiException as e:
                print("❌ 發送失敗")
                print("🔴 錯誤類型：", type(e))
                print("📩 回應內容：", e.body)
                print("-" * 50)
    except pymysql.Error as e:
        print("❌ 資料庫操作錯誤:", str(e))
        db.rollback()

    return "OK"



@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    global previous_message  # 明確宣告使用全域變數
    global Type
    user_id = event.source.user_id
    print(f"User ID: {user_id}")
    

    if event.message and hasattr(event.message, "text"):
        Message = event.message.text.strip()  # 移除前後空白
        print(f"Received message: {Message}")
        UID(user_id, Message)  # 更新使用者ID到previous_message
        pm = next((item["message"] for item in previous_message if item["user_id"] == user_id), None)
        # 用戶資料庫處理
        handle_user_data(user_id, Message, event)
        try:
            # 訊息處理邏輯
            if Message == "Feed Back":
                # 處理回饋流程
                pm = "Feed Back"
                previous_message = [item for item in previous_message if item["user_id"] != user_id]
                previous_message.append({"user_id": user_id, "message": pm})  # 更新使用者ID到previous_message
                quick_reply = QuickReply(
                    items=[
                        QuickReplyItem(action=MessageAction(label="NBA", text="NBA")),
                        QuickReplyItem(action=MessageAction(label="F1", text="F1")),
                        QuickReplyItem(action=MessageAction(label="MLB", text="MLB")),
                        QuickReplyItem(action=MessageAction(label="CPBL", text="CPBL")),
                        QuickReplyItem(action=MessageAction(label="BWF", text="BWF")),
                        QuickReplyItem(action=MessageAction(label="Cancel", text="Cancel"))
                    ]
                )
                self_reply(event, "請選擇賽事種類：", quick_reply)
            
            elif Message == "Cancel":
                # 處理取消回饋流程
                previous_message = [item for item in previous_message if item["user_id"] != user_id]
                previous_message.append({"user_id": user_id, "message": ""})  # 更新使用者ID到previous_message
                self_reply(event, "已取消回饋流程。")
            elif Message == "取消進入管理者":
                self_reply(event, "已取消進入管理者介面。")
            elif pm == "Feed Back" and Message in sport.keys():
                # 處理賽事選擇
                pm = "Feed Backing"  # 重設狀態
                previous_message = [item for item in previous_message if item["user_id"] != user_id]
                previous_message.append({"user_id": user_id, "message": pm})  # 更新使用者ID到previous_message
                self_reply(event, f"您選擇的賽事種類是：{Message}\n請輸入您的回報內容(限一個文字框):")
                Type = Message
            
            elif previous_message == "Feed Backing":
                # 處理回報內容
                previous_message = [item for item in previous_message if item["user_id"] != user_id]
                previous_message.append({"user_id": user_id, "message": ""})  # 更新使用者ID到previous_message
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
                carousel_template = CarouselTemplate(
                    columns=[
                        CarouselColumn(
                            thumbnail_image_url='https://www.milk.com.hk/content/images/size/w1000/2024/07/nba1-1.png',
                            title='NBA',
                            text='點擊前往 NBA 官網',
                            actions=[
                                URIAction(
                                    label='前往及時比分',
                                    uri='https://cgusqlpj.ddns.net:5000/NBAscore'
                                )
                            ]
                        ),
                        CarouselColumn(
                            thumbnail_image_url='https://miro.medium.com/v2/resize:fit:2560/1*rwpOxkNX0UN5A3BE28HLTQ.png',
                            title='F1',
                            text='點擊前往 F1 官網',
                            actions=[
                                URIAction(
                                label='前往及時比分',
                                uri='https://cgusqlpj.ddns.net:5000/F1Timing'
                                )
                            ]
                        ),
                        CarouselColumn(
                            thumbnail_image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Major_League_Baseball_logo.svg/1200px-Major_League_Baseball_logo.svg.png',
                            title='MLB',
                            text='點擊前往 MLB 官網',
                            actions=[
                                URIAction(
                             label='前往及時比分',
                                uri='https://cgusqlpj.ddns.net:5000/MLB_living'
                                )
                            ]
                        ),
                        CarouselColumn(
                            thumbnail_image_url='https://scontent.ftpe8-4.fna.fbcdn.net/v/t39.30808-6/312987768_174139705273413_768451481816410125_n.png?_nc_cat=110&ccb=1-7&_nc_sid=6ee11a&_nc_ohc=R9Tif76Q7dwQ7kNvwHl2pGW&_nc_oc=AdlWTd1wi63zzaWlMtGTN0NpQ0lYGMCq4K3LklVCAytMQQpjbDNSq9t4zJfdZ9RdofY&_nc_zt=23&_nc_ht=scontent.ftpe8-4.fna&_nc_gid=x3FYdY6mdI4RhUQHVG-mLQ&oh=00_AfLAFtuHo6XasRdpCC-7KQUXGicXrXQ_3C2ykUFnC1pokw&oe=683F66A9',
                            title='CPBL',
                            text='點擊前往 CPBL 官網',
                            actions=[
                                URIAction(
                                    label='前往及時比分',
                                    uri='https://cgusqlpj.ddns.net:5000/CPBL_living'
                                )
                            ]
                        ),
                        CarouselColumn(
                            thumbnail_image_url='https://is1-ssl.mzstatic.com/image/thumb/Purple221/v4/dc/b0/27/dcb027a7-7be4-f050-e127-df60254d1a38/AppIcon-0-1x_U007ephone-0-85-220-0.png/434x0w.webp',
                            title='BWF',
                            text='點擊前往 BWF 官網',
                            actions=[
                                URIAction(
                                    label='前往及時比分',
                                    uri='https://cgusqlpj.ddns.net:5000/BWFscore'
                                )
                            ]
                        ),
                    ]
                )
                template_message = TemplateMessage(
                    alt_text='請選擇賽事種類',
                    template=carousel_template
                )
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[template_message]
                        )
                    )
            elif Message in ["NBA", "F1", "MLB", "CPBL", "BWF"]:
                # 處理賽事比分顯示
                self_reply(event, f"您選擇的賽事種類是：{Message}\n正在查詢即時比分...")
            elif Message == '/gamemode creative':
                   with ApiClient(configuration) as api_client:
                        line_bot_api = MessagingApi(api_client)
                        send_admin_flex(line_bot_api, event.reply_token, rating=0)

            else:
                # 預設回應
                previous_message = [item for item in previous_message if item["user_id"] != user_id]
                previous_message.append({"user_id": user_id, "message":""})  # 更新使用者ID到previous_message
                self_reply(event, f"沒有以下指令：{Message}")
                

            
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

def UID(user_id, message):
    previous_message.append({"user_id": user_id, "message": message})

@handler.add(FollowEvent)
def handle_follow(event):
        user_id = event.source.user_id
        try:
            check_sql = "SELECT user_id FROM users WHERE user_id = %s"
            sql_connect("localhost", 3306, "hanson0901", "Hanson940901", "final_project")

            cursor.execute(check_sql, (user_id,))
            result = cursor.fetchone()
        
            if not result:
                with ApiClient(configuration) as api_client:
                    messaging_api = MessagingApi(api_client)
                    msg = TextMessage(text="歡迎來到『賽事LINE BOT 到』！\n請輸入您的暱稱以儲存您的資料。", quick_reply=None)
                    messaging_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[msg]
                        )
                    )
            else:
                with ApiClient(configuration) as api_client:
                    messaging_api = MessagingApi(api_client)
                    msg = TextMessage(text="歡迎回來！您的資料已存在。", quick_reply=None)
                    messaging_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[msg]
                        )
                    )
        except Exception as e:
            print(f"處理 follow 事件時發生錯誤: {e}")


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

@app.route('/linebot/handled', methods=['POST'])
def handled_feedback():
    data = request.get_json()
    print("收到訊息")
    print(data)
    user_id = data.get('uid')
    content = data.get('text')
    type = data.get('type')
    reply = data.get('reply') if data.get('reply')!="" else "無回覆"

    status = data.get('status')
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.push_message(
            PushMessageRequest(
                to=user_id,
                messages=[TextMessage(text=f"您的意見反映：\n分類:{reverse_sport[type]}\n內容:{content} \n管理員:{status}\n回覆為:{reply}\n感謝您的回饋！")]
            )
        )




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
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
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
                }
            ],
            "flex": 0
        }
    }

    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=[FlexMessage(alt_text="管理者模式", contents=FlexContainer.from_json(json.dumps(admin_flex)))]
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
