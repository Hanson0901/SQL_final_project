from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
from linebot.models import (
    RichMenu,
    RichMenuArea,
    RichMenuSize,
    RichMenuBounds,
    MessageAction,
    URIAction,
)

CHANNEL_ACCESS_TOKEN = LineBotApi(
    "H+2kmGOeBxAqGHImKJpKJPLAtgAUqNa9TTAgY4wesr9kJbs14FJwNDaUFYL90z9Yh/MlJpQXU3A0nPdoDaVvyqZkQeV4fjfAb9Ez5YfOaOGP64bECzjzxeOHMUK/lTvCS009Elcpi6caa5hCeTPfIwdB04t89/1O/w1cDnyilFU="
)

button1 = RichMenuArea(
    bounds=RichMenuBounds(x=0, y=0, width=2500, height=843),
    action=URIAction(label="button 1", uri="https://cgusqlpj.ddns.net:2222/foruser"),
)
button2 = RichMenuArea(
    bounds=RichMenuBounds(x=0, y=843, width=843, height=843),
    action=MessageAction(label="button 2", text="Feed Back"),
)
button3 = RichMenuArea(
    bounds=RichMenuBounds(x=843, y=843, width=843, height=843),
    action=URIAction(
        label="button 3", uri="https://cgusqlpj.ddns.net:2222/public_announcements"
    ),
)
button4 = RichMenuArea(
    bounds=RichMenuBounds(x=1686, y=843, width=843, height=843),
    action=MessageAction(label="button 4", text="即時比分"),
)

rich_menu = RichMenu(
    size=RichMenuSize(width=2500, height=1686),
    selected=True,
    name="圖文選單 1",
    chat_bar_text="查看更多資訊",
    areas=[
        button1,
        button2,
        button3,
        button4,
    ],
)


if __name__ == "__main__":
    try:
        # 建立 Rich Menu
        rich_menu_id = CHANNEL_ACCESS_TOKEN.create_rich_menu(rich_menu=rich_menu)
        print(f"Rich Menu created. rich_menu_id: {rich_menu_id}")

        # 上傳 Rich Menu 圖片
        with open(r"LineBot\richmenu.png", "rb") as f:
            CHANNEL_ACCESS_TOKEN.set_rich_menu_image(rich_menu_id, "image/png", f)
            print("Rich Menu image uploaded.")

        # 設定 Rich Menu 至 Channel
        CHANNEL_ACCESS_TOKEN.set_default_rich_menu(rich_menu_id)
        print("Rich Menu set as default.")

    except LineBotApiError as e:
        print(f"Error creating Rich Menu: {e}")
