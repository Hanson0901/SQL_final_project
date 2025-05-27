from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    RichMenuSize,
    RichMenuRequest,
    RichMenuArea,
    RichMenuBounds,
    MessageAction,
)
import requests
import json

app = Flask(__name__)


CHANNEL_ACCESS_TOKEN = "H+2kmGOeBxAqGHImKJpKJPLAtgAUqNa9TTAgY4wesr9kJbs14FJwNDaUFYL90z9Yh/MlJpQXU3A0nPdoDaVvyqZkQeV4fjfAb9Ez5YfOaOGP64bECzjzxeOHMUK/lTvCS009Elcpi6caa5hCeTPfIwdB04t89/1O/w1cDnyilFU="
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler("974e569266e988233dab6503bbdd1960")


@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info(
            "Invalid signature. Please check your channel access token/channel secret."
        )
        abort(400)

    return "OK"


def create_rich_menu_2():
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_blob_api = MessagingApiBlob(api_client)

        # Create rich menu
        headers = {
            "Authorization": "Bearer " + CHANNEL_ACCESS_TOKEN,
            "Content-Type": "application/json",
        }
        body = {
            "size": {"width": 2500, "height": 1686},
            "selected": True,
            "name": "圖文選單 1",
            "chatBarText": "賽事LINE BOT到",
            "areas": [
                {
                    "bounds": {"x": 0, "y": 0, "width": 2500, "height": 843},
                    "action": {
                        "type": "uri",
                        "uri": "http://35.221.155.196/foruser",
                    },
                },
                {
                    "bounds": {"x": 0, "y": 839, "width": 834, "height": 847},
                    "action": {"type": "message", "text": "Feed Back"},
                },
                {
                    "bounds": {"x": 835, "y": 838, "width": 835, "height": 848},
                    "action": {
                        "type": "uri",
                        "uri": "http://35.221.155.196/public_announcements",
                    },
                },
                {
                    "bounds": {"x": 1664, "y": 843, "width": 836, "height": 843},
                    "action": {"type": "message", "text": "及時比分"},
                },
            ],
        }

        response = requests.post(
            "https://api.line.me/v2/bot/richmenu",
            headers=headers,
            data=json.dumps(body).encode("utf-8"),
        )
        response = response.json()
        print(response)
        rich_menu_id = response["richMenuId"]

        # Upload rich menu image
        with open(r"LineBot/richmenu.png", "rb") as image:
            line_bot_blob_api.set_rich_menu_image(
                rich_menu_id=rich_menu_id,
                body=bytearray(image.read()),
                _headers={"Content-Type": "image/jpeg"},
            )

        line_bot_api.set_default_rich_menu(rich_menu_id)


create_rich_menu_2()

if __name__ == "__main__":
    app.run()
