from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from flask.logging import create_logger
from linebot.models import MessageEvent,TextSendMessage,PostbackEvent,URIAction,TemplateSendMessage,ButtonsTemplate,MessageAction
import pymysql
import re
from flask import render_template  # 放到最上面 import 區

@app.route('/search')
def serve_search():
    return render_template('search.html')

def sql_connect(host, port, user, passwd, database):
    global db,cursor
    try:
        db= pymysql.connect(host=host, user=user, passwd=passwd, database=database, port=int(port))
        print("連線成功")
        cursor = db.cursor()
        return True
    except pymysql.Error as e:
        print("連線錯誤: " + str(e))
        return False

def reconnect():
    global db, cursor
    try:
        db.ping(reconnect=True)
        cursor = db.cursor()
    except:
        print("❌ MySQL 重新連線失敗")

def select(sql):
    reconnect()
    cursor.execute(sql) # 執行sql語句
    result=cursor.fetchall() # 取得查詢結果
    result = list(result)
    for i in range(len(result)):
        result[i] = str(result[i])
        result[i] = re.sub(r"[.,'`()]", '', result[i]) # 移除結果中的特殊字符
    return result

def insert(sql):
    reconnect()
    cursor.execute(sql) # 執行sql語句
    db.commit() # 提交事務，確認寫入資料庫

app = Flask(__name__)  # 初始化 Flask 應用程式
LOG = create_logger(app)  # 建立日誌記錄器
line_bot_api = LineBotApi('Lb9dny2/fkX27brCeMljAJL066WKzVly2dUSvYW+SxybkVT5xDPXL3Z3LX6fRNMNvFLFwwIRluZS9QdRcR+gkS1zygXtGiyUhIkVzppFAsctOZO1S4C/lPfQCYeeRaPN+HiGVxTWD99+5spoWWFbbgdB04t89/1O/w1cDnyilFU=')  # 初始化 LINE Bot API 物件並設定 Channel Access Token
handler = WebhookHandler('f8964fb6998fb317ad7ad7af09840fa0')  # 初始化 Webhook 處理器並設定 Channel Secret
sql_connect('localhost', 3306, 'root', '', 'city1')

# 設定 Webhook 接收的路徑和 HTTP 方法
@app.route("/", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', None)
    body = request.get_data(as_text=True)
    
    print("=== LINE Webhook DEBUG ===")
    print("Signature:", signature)
    print("Body:", body)

    if not signature:
        print("❌ 沒有收到 Signature！")
        return 'No Signature', 400

    try:
        handler.handle(body, signature)
    except InvalidSignatureError as e:
        print("❌ Invalid Signature!", str(e))
        return 'Invalid Signature', 400

    return 'OK'
    #signature = request.headers['X-Line-Signature']  # 取得 Line Signature 用於驗證請求的合法性
    #print("signature:", signature)
    #body = request.get_data(as_text=True)  # 取得請求的內容
    #LOG.info("Request body: " + body)  # 將請求內容記錄到 LOG 中
    #try:
    #    handler.handle(body, signature)  # 使用 handler 處理接收到的事件
    #except InvalidSignatureError:
    #    abort(400)  # 若 Line Signature 驗證失敗，則回傳 400 錯誤
    #return 'OK'  # 回傳 "OK" 表示處理完成且正常結束

    # 輸入地址button  
# 處理 PostbackEvent 事件的處理函式
@handler.add(PostbackEvent)
def handle_postback(event):
    # 檢查是否為特定 Rich Menu action 的觸發事件
    if event.postback.data == 'action=input':
        # 取得使用者的 user id
        user_id = event.source.user_id
        # 將 user id 傳送至網頁
        url = 'https://561f-220-128-241-246.ngrok-free.app/search?user_id=' + user_id

        message = TemplateSendMessage(
            alt_text='前往網頁，若無法顯示按鈕模樣請的替代文字',
            template=ButtonsTemplate(
                title='地址輸入', # 標題
                text='請點選下方按鈕進入輸入地址', # 文字內容
                actions=[
                    URIAction(
                        label='前往網頁', # 按鈕標籤
                        uri=url # 跳轉至網頁
                    )
                ]
            )
        )
        # 使用 Line Bot API 的 reply_message 方法回覆訊息給使用者
        line_bot_api.reply_message(event.reply_token, message)

# 查詢個人資料button
@handler.add(MessageEvent)
def echo(event):
    user_id = event.source.user_id #取得使用者的user_id
    print("user_id =", user_id)

    if event.message.type == 'text':
        stt = event.message.text #取得使用者輸入的訊息內容
        sql=f'''SELECT city FROM city WHERE 1;''' # 查詢城市資料的 SQL 語句
        addr = select(sql) # 執行 SQL 查詢並取得城市資料
        if stt[0:3] in addr:  # 如果使用者輸入的前三個字在城市資料中，表示輸入完成
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage('輸入完成')
            )
            sql = f'''UPDATE `userinformation`SET `addr` ='{stt}' WHERE `lineid` = '{user_id}';''' # 更新使用者的地址至資料庫
            insert(sql)
        elif stt == '查詢個人資料!':
            text = ''
            sql=f'''SELECT `name`,`addr` FROM `userinformation` WHERE lineid = '{user_id}';''' # 查詢使用者的姓名和地址
            print(select(sql))
            text = text + '姓名：' + select(sql)[0].split(' ',1)[0] + '\n' + '地址：'+select(sql)[0].split(' ',2)[1]
            line_bot_api.reply_message( # 回覆查詢使用者的個人資料
                event.reply_token,
                TextSendMessage(text)
            )
        else: # 其他情況視為輸入名字
            line_bot_api.reply_message( # 回覆請使用者輸入地址
                event.reply_token,
                TextSendMessage('輸入地址')
            )
            # 將使用者輸入的名字與userid新增至資料庫
            sql=f'''INSERT INTO `userinformation`(`lineid`, `name`, `addr`) VALUES ('{user_id}','{stt}','');'''
            insert(sql)

@app.route("/web_page", methods=['POST'])
def web_page():
    input_text = request.form.get('input_text')  # 取得網頁回傳的內容
    id = request.form.get('id')  # 取得網頁回傳的user_id

    # 建立按鈕樣板訊息
    template_message = TemplateSendMessage(
        alt_text='確認地址',  # 在無法顯示按鈕樣板訊息時的替代文字
        template = ButtonsTemplate(
            title = '請確認地址是否正確，',  # 標題
            text = input_text,  # 文字內容
            actions=[
                MessageAction(
                    label = '正確',  # 按鈕標籤
                    text = input_text  # 點擊按鈕後回覆的文字訊息
                )
            ]
        )
    )

    # 使用 LineBotApi 發送按鈕樣板訊息
    line_bot_api.push_message(id, template_message)

    return 'ok'

if __name__ == "__main__":
    app.run(port=8000)  # 設定使用port 8000
