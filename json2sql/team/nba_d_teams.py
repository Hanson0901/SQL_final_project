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

nba_teams = {
    "費城76人": "Philadelphia 76ers",
    "芝加哥公牛": "Chicago Bulls",
    "密爾瓦基公鹿": "Milwaukee Bucks",
    "紐約尼克": "New York Knicks",
    "亞特蘭大老鷹": "Atlanta Hawks",
    "華盛頓巫師": "Washington Wizards",
    "底特律活塞": "Detroit Pistons",
    "夏洛特黃蜂": "Charlotte Hornets",
    "波士頓塞爾蒂克": "Boston Celtics",
    "印第安那溜馬": "Indiana Pacers",
    "多倫多暴龍": "Toronto Raptors",
    "邁阿密熱火": "Miami Heat",
    "克里夫蘭騎士": "Cleveland Cavaliers",
    "布魯克林籃網": "Brooklyn Nets",
    "奧蘭多魔術": "Orlando Magic",
    "鳳凰城太陽": "Phoenix Suns",
    "休士頓火箭": "Houston Rockets",
    "明尼蘇達灰狼": "Minnesota Timberwolves",
    "曼斐斯灰熊": "Memphis Grizzlies",
    "洛杉磯快艇": "Los Angeles Clippers",
    "波特蘭拓荒者": "Portland Trail Blazers",
    "丹佛金塊": "Denver Nuggets",
    "金州勇士": "Golden State Warriors",
    "聖安東尼奧馬刺": "San Antonio Spurs",
    "沙加緬度國王": "Sacramento Kings",
    "洛杉磯湖人": "Los Angeles Lakers",
    "奧克拉荷馬雷霆": "Oklahoma City Thunder",
    "達拉斯獨行俠": "Dallas Mavericks",
    "猶他爵士": "Utah Jazz",
    "紐奧良鵜鶘": "New Orleans Pelicans"
}


nba_teams_TABLE = "nba_team"
city_info_TABLE = "city_info"
teams_TABLE = "teams"

value_template = ["%s"] * 2
para = ", ".join(value_template)


# 排序：根據檔名開頭的數字（如 22_XXX.json）
def extract_number(name):
    # r"(\d+)_“ 是正則表達式，意思是「開頭的數字+底線」
    match = re.match(r"(\d+)_", name)  # 比對開頭是數字_ 的字串

    # match.group(1) 是抓到的數字
    return int(match.group(1)) if match else float("inf")


# NBA球員資料夾路徑
file_path = r"Player_info\NBA\team_d.json"
# 把所有的檔名的數字透過extract_number轉換後排序


with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

for team in data:
    team_english_name = team.get("team_name", "")
    city_full = team.get("city", "")
    city_name = city_full.split(",")[0] if "," in city_full else city_full

    sport_type = "1"

    try:
        with connection.cursor() as cursor:
            # 查 city_id
            cursor.execute(
                "SELECT city_id FROM city_info WHERE city_name = %s",
                (city_name,)
            )
            city_result = cursor.fetchone()
            city_id = city_result[0] if city_result else None
            if city_id is None:
                print(f"❌ City '{city_name}' not found in city_info table.")

            # 查 team_id
            cursor.execute(
                "SELECT team_id FROM teams WHERE team_name = %s",
                (team_english_name,)
            )
            team_result = cursor.fetchone()
            team_id = team_result[0] if team_result else None

            # 寫入 nba_teams
            sql = f"""
                INSERT INTO {nba_teams_TABLE} 
                (team_id, city_id, team_name, arena)
                VALUES (%s, %s, %s, %s)
            """
            arena = team.get("arena", "")
            cursor.execute(
                sql,
                (
                    team_id,
                    city_id,
                    team_english_name,
                    arena,
                ),
            )

        connection.commit()
        print(f"✅  已寫入 MySQL！")
    except Exception as e:
        print(f"❌ error occurs at：", e)