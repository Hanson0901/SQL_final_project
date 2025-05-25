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


TABLE = "bwf_team"

value_template = ["%s"] * 2
para = ", ".join(value_template)

FOLDER_PATH = "Player_info\BWF\player_info.json"

with open(FOLDER_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

try:
    with connection.cursor() as cursor:
        for item in data:
            team_name = item["country"]
            cursor.execute(
                    "SELECT team_id FROM teams WHERE team_name = %s",
                    (team_name,)
                )
            team_result = cursor.fetchone()
            team_id = team_result[0] if team_result else None
            if team_id is None:
                print(f"❌ 未找到國家 {team_name} 的 ID，將跳過此球員。")


            # 檢查 team_name 是否已存在於資料庫
            cursor.execute(f"SELECT COUNT(*) FROM {TABLE} WHERE team_name = %s", (team_name,))
            exists = cursor.fetchone()[0]
            if not exists:

                sql = f"""
                    INSERT INTO {TABLE} 
                    (team_id,team_name)
                    VALUES ({para})
                """
                cursor.execute(
                    sql,
                    (
                        team_id,
                        item["country"]
                    )
                )   
    connection.commit()
    print(f"✅ {FOLDER_PATH} 已寫入 MySQL！")
except Exception as e:
    print(f"❌ error occurs at {FOLDER_PATH}：", e)

connection.close()
