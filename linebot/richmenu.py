from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
from linebot.models import RichMenu, RichMenuArea, RichMenuSize, RichMenuBounds, MessageAction, PostbackAction

line_bot_api = LineBotApi('Lb9dny2/fkX27brCeMljAJL066WKzVly2dUSvYW+SxybkVT5xDPXL3Z3LX6fRNMNvFLFwwIRluZS9QdRcR+gkS1zygXtGiyUhIkVzppFAsctOZO1S4C/lPfQCYeeRaPN+HiGVxTWD99+5spoWWFbbgdB04t89/1O/w1cDnyilFU=')

button1 = RichMenuArea(  # 設定 RichMenu 的第一個按鈕區域的標籤為 "Button 1"，並設定 PostbackAction 動作
    bounds=RichMenuBounds(x=0, y=0, width=1250, height=1686),
    action=PostbackAction(label='Button 1', data='action=input')
)

button2 = RichMenuArea(  # 設定 RichMenu 的第二個按鈕區域的標籤為 "查詢個人資料"，並設定 MessageAction 動作
    bounds=RichMenuBounds(x=1250, y=0, width=1250, height=1686),
    action=MessageAction(label='查詢個人資料', text='查詢個人資料')
)

rich_menu = RichMenu(
    size=RichMenuSize(width=2500, height=1686),  # 設定RichMenu大小
    selected=True,
    name='CGU',           # 設定 RichMenu 的名稱
    chat_bar_text='CGU',  # 設定 RichMenu 在聊天視窗中的標籤
    areas=[button1, button2]  # 設定 RichMenu 的按鈕區域
)
try:
    # 建立 Rich Menu
    rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu)
    print(f'Rich Menu created. rich_menu_id: {rich_menu_id}')

    # 上傳 Rich Menu 圖片
    with open('C:/xampp/htdocs/linebot/richmenu.png', 'rb') as f:
        line_bot_api.set_rich_menu_image(rich_menu_id, 'image/png', f)
        print('Rich Menu image uploaded.')

    # 設定 Rich Menu 至 Channel
    line_bot_api.link_rich_menu_to_user('U7cfed60a18cf3118741d22c91d070d41', rich_menu_id)
    line_bot_api.set_default_rich_menu(rich_menu_id)
    print('Rich Menu set as default.')

except LineBotApiError as e:
    print(f'Error creating Rich Menu: {e}')
