import requests
import json

CHANNEL_ACCESS_TOKEN = "H+2kmGOeBxAqGHImKJpKJPLAtgAUqNa9TTAgY4wesr9kJbs14FJwNDaUFYL90z9Yh/MlJpQXU3A0nPdoDaVvyqZkQeV4fjfAb9Ez5YfOaOGP64bECzjzxeOHMUK/lTvCS009Elcpi6caa5hCeTPfIwdB04t89/1O/w1cDnyilFU="


def create_rich_menu():
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

    # 上傳圖片
    with open(r"LineBot\richmenu.jpg", "rb") as image:
        img_headers = {
            "Authorization": "Bearer " + CHANNEL_ACCESS_TOKEN,
            "Content-Type": "image/jpeg",
        }
        requests.post(
            f"https://api.line.me/v2/bot/richmenu/{rich_menu_id}/content",
            headers=img_headers,
            data=image,
        )

    # 設定預設 rich menu
    requests.post(
        f"https://api.line.me/v2/bot/user/all/richmenu/{rich_menu_id}",
        headers={"Authorization": "Bearer " + CHANNEL_ACCESS_TOKEN},
    )


if __name__ == "__main__":
    create_rich_menu()
