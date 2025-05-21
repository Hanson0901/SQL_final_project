import json
import pymysql  # type: ignore
import os
import re

chinese_teams = [
    "波士頓賽爾提克",
    "布魯克林籃網",
    "紐約尼克",
    "費城76人",
    "多倫多暴龍",
    "芝加哥公牛",
    "克里夫蘭騎士",
    "底特律活塞",
    "印第安納溜馬",
    "密爾瓦基公鹿",
    "亞特蘭大老鷹",
    "夏洛特黃蜂",
    "邁阿密熱火",
    "奧蘭多魔術",
    "華盛頓巫師",
    "丹佛金塊",
    "明尼蘇達灰狼",
    "奧克拉荷馬雷霆",
    "波特蘭拓荒者",
    "猶他爵士",
    "金州勇士",
    "洛杉磯快艇",
    "洛杉磯湖人",
    "鳳凰城太陽",
    "沙加緬度國王",
    "達拉斯獨行俠",
    "休士頓火箭",
    "曼非斯灰熊",
    "紐奧良鵜鶘",
    "聖安東尼奧馬刺",
]

english_teams = [
    "Boston Celtics",
    "Brooklyn Nets",
    "New York Knicks",
    "Philadelphia 76ers",
    "Toronto Raptors",
    "Chicago Bulls",
    "Cleveland Cavaliers",
    "Detroit Pistons",
    "Indiana Pacers",
    "Milwaukee Bucks",
    "Atlanta Hawks",
    "Charlotte Hornets",
    "Miami Heat",
    "Orlando Magic",
    "Washington Wizards",
    "Denver Nuggets",
    "Minnesota Timberwolves",
    "Oklahoma City Thunder",
    "Portland Trail Blazers",
    "Utah Jazz",
    "Golden State Warriors",
    "Los Angeles Clippers",
    "Los Angeles Lakers",
    "Phoenix Suns",
    "Sacramento Kings",
    "Dallas Mavericks",
    "Houston Rockets",
    "Memphis Grizzlies",
    "New Orleans Pelicans",
    "San Antonio Spurs",
]


# 這裡是sql設定區 要入資料改這裡~
connection = pymysql.connect(
    host="cgusqlpj.ddns.net",
    port=3306,
    user="william",
    password="Chang0928",
    database="final_project",
    charset="utf8mb4",
)


TABLE = "matches_schedule"
type = 1
value_template = ["%s"] * 6
para = ", ".join(value_template)

FOLDER_PATH = r"Player_info\NBA\nba_schedule.json"

with open(FOLDER_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

try:
    with connection.cursor() as cursor:
        for item in data:
            sql = f"""
                INSERT INTO {TABLE} 
                (date,type, game_no, teams, stadium, time)
                VALUES ({para})
            """
            cursor.execute(
                sql,
                (
                    item["date"],
                    type,
                    item["game_no"],
                    item["teams"],
                    item["stadium"],
                    item["time"],
                ),
            )
    connection.commit()
    print(f"✅ {FOLDER_PATH} 已寫入 MySQL！")
except Exception as e:
    print(f"❌ error occurs at {FOLDER_PATH}：", e)

connection.close()
