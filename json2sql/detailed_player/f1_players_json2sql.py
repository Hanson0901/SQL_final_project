import json
import pymysql  # type: ignore
import os
import re
from geopy.geocoders import Nominatim   # type: ignore


# 這裡是sql設定區 要入資料改這裡~
connection = pymysql.connect(
    host="cgusqlpj.ddns.net",
    port=3306,
    user="william",
    password="Chang0928",
    database="final_project",
    charset="utf8mb4",
)


TABLE = "f1_drivers"

value_template = ["%s"] * 5
para = ", ".join(value_template)

sport_type = 2
FOLDER_PATH = r"Player_info\F1\f1_drivers_full_data.json"
with open(FOLDER_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

try:
    with connection.cursor() as cursor:

        id = 0
        for item in data:
            team = item.get("Team")
           
            
            cursor.execute(
                "SELECT team_id FROM f1_team WHERE team_name = %s",
                (team,)
            )
            team_result = cursor.fetchone()
            team_id = team_result[0] if team_result else None

            if team_id is None:
                print(f"❌ 未找到國家 {team} 的 ID，將跳過此球員。")
              
            

            sql = f"""
                INSERT INTO {TABLE} 
                (player_id,team_id,number,ranking,pts)
                VALUES ({para})
            """

            cursor.execute(
                sql,
                (
                    f"f1_{id}",
                    team_id,
                    item.get("Number"),
                    item.get("Rank"),
                    item.get("Points")
                ),
            )
            id += 1
    connection.commit()
    print(f"✅ {FOLDER_PATH} 已寫入 MySQL！")
except Exception as e:
    print(f"❌ error occurs at {FOLDER_PATH}：", e)