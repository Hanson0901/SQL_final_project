import json
import pymysql  # type: ignore
import os
import re


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
type = 4
value_template = ["%s"] * 6
para = ", ".join(value_template)

FOLDER_PATH = "Player_info\CPBL\cpbl_schedule.json"

with open(FOLDER_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

try:
    with connection.cursor() as cursor:
        for item in data:
            sql = f"""
                INSERT INTO {TABLE} 
                (date, type ,game_no, teams, stadium, time)
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
