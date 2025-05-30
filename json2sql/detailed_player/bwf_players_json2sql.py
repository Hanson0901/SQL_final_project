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

value_template = ["%s"] * 9
para = ", ".join(value_template)

FOLDER_PATH = r"Player_info\BWF\player_info.json"

with open(FOLDER_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# ...existing code...
try:
    with connection.cursor() as cursor:
        for item in data:
            id = f"bwf_{item['id']}"
            try:
                cursor.execute(
                    "SELECT player_id FROM bwf_players WHERE player_id = %s",
                    (id,)
                )
                if cursor.fetchone() is not None:
                    print(f"❌ {id} 已存在於 MySQL，跳過寫入！")
                    continue

                team_name = item["country"]
                cursor.execute(
                    "SELECT team_id FROM bwf_team WHERE team_name = %s",
                    (team_name,)
                )
                team_result = cursor.fetchone()
                team_id = team_result[0] if team_result else None

                sql = f"""
                    INSERT INTO {TABLE} 
                    (player_id, age, world_rank, world_tour_rank, world_rank_title, world_tour_rank_title, point_title,point,team_id)
                    VALUES ({para})
                """
                cursor.execute(
                    sql,
                    (
                        id,
                        (
                            int(item["age"])
                            if item["age"].isdigit()
                            else (
                                None
                                if item["age"] == "-" or item["age"] == ""
                                else item["age"]
                            )
                        ),
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
                print(f"✅ {id} 已寫入 MySQL！")
            except Exception as e:
                if "a foreign key constraint fails" in str(e):
                    print(f"❌ 外鍵錯誤，跳過 {id}：{e}")
                    continue
                else:
                    print(f"❌ 其他錯誤，跳過 {id}：{e}")
                    continue
finally:
    connection.close()


