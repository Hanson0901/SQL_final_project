import json
import pymysql  # type: ignore
import os
import re
def null_if_dash(val):
    return None if val == "-" or val == "" else val

# 這裡是sql設定區 要入資料改這裡~
connection = pymysql.connect(
    host="cgusqlpj.ddns.net",
    port=3306,
    user="william",
    password="Chang0928",
    database="final_project",
    charset="utf8mb4",
)


TABLE = "bwf_players"

value_template = ["%s"] * 10
para = ", ".join(value_template)

FOLDER_PATH = "Player_info\BWF\player_info.json"

with open(FOLDER_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

try:
    with connection.cursor() as cursor:
        for item in data:

            

            team_name = item["country"]
            cursor.execute(
                    "SELECT team_id FROM bwf_team WHERE team_name = %s",
                    (team_name,)
                )
            team_result = cursor.fetchone()
            team_id = team_result[0] if team_result else None

            sql = f"""
                INSERT INTO {TABLE} 
                (player_id, age, hand, world_rank, world_tour_rank, world_rank_title, world_tour_rank_title, point_title,point,team_id)
                VALUES ({para})
            """
            cursor.execute(
                sql,
                (
                    f"bwf_{item['id']}",
                    (
                        int(item["age"])
                        if item["age"].isdigit()
                        else (
                            None
                            if item["age"] == "-" or item["age"] == ""
                            else item["age"]
                        )
                    ),
                    null_if_dash(item["hand"]),
                    (
                        int(item["world_rank"])
                        if item["world_rank"].isdigit()
                        else (
                            None
                            if item["world_rank"] == "-" or item["world_rank"] == ""
                            else item["world_rank"]
                        )
                    ),
                    null_if_dash(item["world_tour_rank"]),
                    null_if_dash(item["world_rank_title"]),
                    null_if_dash(item["world_tour_rank_title"]),
                    null_if_dash(item["point_title"]),
                    (
                        int(item["point"])
                        if item["point"].isdigit()
                        else (
                            None
                            if item["point"] == "-" or item["point"] == ""
                            else item["point"]
                        )
                    ),
                    team_id
                ),
            )
    connection.commit()
    print(f"✅ {FOLDER_PATH} 已寫入 MySQL！")
except Exception as e:
    print(f"❌ error occurs at {FOLDER_PATH}：", e)

connection.close()
