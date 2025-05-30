import json
import pymysql  # type: ignore
import os
import re
import pycountry  # type: ignore

# 這裡是sql設定區 要入資料改這裡~
connection = pymysql.connect(
    host="cgusqlpj.ddns.net",
    port=3306,
    user="william",
    password="Chang0928",
    database="final_project",
    charset="utf8mb4",
)

countries = [country.name for country in pycountry.countries]

def adj_to_country(adj):
    patterns = ['ese', 'ian', 'an', 'ean', 'ic', 'ish']
    suffixes = ['a', 'o']
    for pattern in patterns:
        match = re.match(r'^(.*)(' + pattern + ')$', adj)
        if match:
            stem = match.group(1)
            # 直接比對
            if stem in countries:
                return stem
            # 加上常見尾碼再比對
            for suffix in suffixes:
                candidate = stem + suffix
                if candidate in countries:
                    return candidate
    return None

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


TABLE = "teams"

value_template = ["%s"] * 2
para = ", ".join(value_template)
# NBA 1
# F1 2
# MLB 3
# CPLB 4
# BWF 5
write_list = [
5
]

# NBA
if 1 in write_list:
    # 排序：根據檔名開頭的數字（如 22_XXX.json）
    def extract_number(name):
        # r"(\d+)_“ 是正則表達式，意思是「開頭的數字+底線」
        match = re.match(r"(\d+)_", name)  # 比對開頭是數字_ 的字串

        # match.group(1) 是抓到的數字
        return int(match.group(1)) if match else float("inf")


    # NBA球員資料夾路徑
    FOLDER_PATH = r"Player_info\NBA\json"
    # 把所有的檔名的數字透過extract_number轉換後排序
    file_list = sorted(
        [f for f in os.listdir(FOLDER_PATH) if f.endswith(".json")], key=extract_number
    )


    for file_name in file_list:
        file_path = os.path.join(FOLDER_PATH, file_name)


        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 擷取球隊中文名
        team_chinese_name = file_name.split("_")[1]
        # 取得英文隊名
        team_english_name = nba_teams.get(team_chinese_name, "")
        sport_type = "1"

        try:
            with connection.cursor() as cursor:


                
                sql = f"""
                    INSERT INTO {TABLE} 
                    (team_name,sport_type)
                    VALUES ({para})
                """
                cursor.execute(
                    sql,
                    (
                        team_english_name,
                        sport_type,
                    ),
                        )

                
            connection.commit()
            print(f"✅ {file_name} 已寫入 MySQL！")
        except Exception as e:
            print(f"❌ error occurs at {file_name}：", e)

# F1
if 2 in write_list:
   
    sport_type = 2
    FOLDER_PATH = r"Player_info\F1\f1_teams_info.json"

    with open(FOLDER_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    try:
        with connection.cursor() as cursor:
            for item in data:
                team_name = item["Nickname"]

                sql = f"""
                    INSERT INTO {TABLE} 
                    (team_name, sport_type)
                    VALUES ({para})
                """
                cursor.execute(
                    sql,
                    (
                        team_name,
                        sport_type,
                    ),
                )
        connection.commit()
        print(f"✅ {FOLDER_PATH} 已寫入 MySQL！")
    except Exception as e:
        print(f"❌ error occurs at {FOLDER_PATH}：", e)




# MLB
if 3 in write_list:
    print("MLB teams data writing is not implemented yet.")

# CPLB
if 4 in write_list:
    print("CPLB teams data writing is not implemented yet.")

# BWF
if 5 in write_list:
    FOLDER_PATH = r"Player_info\BWF\player_info.json"
    sport_type = 5
    with open(FOLDER_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    try:
        with connection.cursor() as cursor:
            for item in data:
                
                    
                team_name = item['country']

                # 檢查 team_name 是否已存在於資料庫
                cursor.execute(f"SELECT COUNT(*) FROM {TABLE} WHERE team_name = %s", (team_name,))
                exists = cursor.fetchone()[0]
                if not exists:
                    

                    sql = f"""
                        INSERT INTO {TABLE} 
                        (team_name,sport_type)
                        VALUES ({para})
                    """
                    cursor.execute(
                        sql,
                        (
                            team_name,  
                            sport_type,
                        
                            
                        ),
                    )
                else:
                    print(f"⚠️ {team_name} 已存在於 {TABLE}，跳過寫入。")
        connection.commit()
        print(f"✅ {FOLDER_PATH} 已寫入 MySQL！")
    except Exception as e:
        print(f"❌ error occurs at {FOLDER_PATH}：", e)