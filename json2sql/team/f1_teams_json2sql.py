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


TABLE = "f1_team"

value_template = ["%s"] * 9
para = ", ".join(value_template)


FOLDER_PATH = r"Player_info\F1\f1_teams_info.json"

with open(FOLDER_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

try:
    with connection.cursor() as cursor:
        for item in data:
            team_name = item["Nickname"]
             # 查 team_id
            cursor.execute(
                "SELECT team_id FROM teams WHERE team_name = %s",
                (team_name,)
            )
            team_result = cursor.fetchone()
            team_id = team_result[0] if team_result else None
            if team_id is None:
                print(f"❌ team '{team_name}' not found in teams table.")

            sql = f"""
                INSERT INTO {TABLE} 
                (team_id, team_name, ranking, team_point, entry_year, engine_supplier, full_name, car_type, team_chief)
                VALUES ({para})
            """

            cursor.execute(
                sql,
                (
                    team_id,
                    team_name,
                    item.get("Rank"),
                    item.get("Team Points"),
                    item.get("First Team Entry"),
                    item.get("Power Unit"),
                    item.get("Full Team Name"),
                    item.get("Chassis"),
                    item.get("Team Chief"),
                ),
            )
    connection.commit()
    print(f"✅ {FOLDER_PATH} 已寫入 MySQL！")
except Exception as e:
    print(f"❌ error occurs at {FOLDER_PATH}：", e)

