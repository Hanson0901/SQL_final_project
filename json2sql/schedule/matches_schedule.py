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
def get_final_winner(score_str):
    scores = list(map(int, score_str.strip().split()))
    a_win, b_win = 0, 0
    for i in range(0, len(scores), 2):
        a, b = scores[i], scores[i+1]
        if a > b:
            a_win += 1
        elif b > a:
            b_win += 1
        # 判斷是否已經有人兩勝
        if a_win == 2:
            return "A"
        if b_win == 2:
            return "B"


TABLE = "matches_schedule"

value_template = ["%s"] *6
para = ", ".join(value_template)

FOLDER_PATH = r"Player_info\BWF\BWF_schedule.json"
type = 5  # BWF
with open(FOLDER_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)


try:
    with connection.cursor() as cursor:
        for item in data:
            team_a = item.get("team_a")
            team_b = item.get("team_b")

            point=item.get("point")
            
            winner = get_final_winner(point)
            if winner == "A":
                winner = team_a
            elif winner == "B":
                winner = team_b
            

            cursor.execute(
                "SELECT team_id FROM bwf_team WHERE team_name = %s",
                (team_a)
            )
            team_a_id = cursor.fetchone()

            cursor.execute(
                "SELECT team_id FROM bwf_team WHERE team_name = %s",
                (team_b)
            )
            team_b_id = cursor.fetchone()

            sql = f"""
                INSERT INTO {TABLE} 
                (type, team_a, team_b, date, time, point)
                VALUES ({para})
            """
            cursor.execute(
                sql,
                (   

                    type,
                    team_a_id,
                    team_b_id,
                    item.get("date"), 
                    item.get("time"),  
                    winner
                ),
            )
            connection.commit()
            print(f"✅ {team_a} vs {team_b} 已寫入 MySQL！")
except Exception as e:
    print(f"❌ 發生錯誤: {e}")
                



