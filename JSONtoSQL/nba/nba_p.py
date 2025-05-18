import json
import pymysql
import os
import re


#這裡是sql設定區 要入資料改這裡~
connection = pymysql.connect(
    host='localhost',
    user='uuriglass',
    password='laby800322',
    database='nba',
    charset='utf8mb4'
)

FOLDER_PATH = 'players' 
TABLE = 'players'

value_template = ["%s"] * 11
para = ", ".join(value_template)

#排序：根據檔名開頭的數字（如 22_XXX.json）
def extract_number(name):
    #r"(\d+)_“ 是正則表達式，意思是「開頭的數字+底線」
    match = re.match(r"(\d+)_", name) #比對開頭是數字_ 的字串
    
    #match.group(1) 是抓到的數字
    return int(match.group(1)) if match else float('inf')

#把所有的檔名的數字透過extract_number轉換後排序
file_list = sorted(
    [f for f in os.listdir(FOLDER_PATH) if f.endswith('.json')],
    key=extract_number
)

for file_name in file_list:
    file_path = os.path.join(FOLDER_PATH, file_name)

    # 擷取 team_id（從檔名開頭的數字）
    team_id = extract_number(file_name)

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    try:
        with connection.cursor() as cursor:
            for item in data:
                sql = f"""
                    INSERT INTO {TABLE} 
                    (player, games, minutes, fg_pct, ft_pct, three_pt_pct, points, off_reb, rebounds, assists, team_id)
                    VALUES ({para})
                """
                cursor.execute(sql, (
                    item['player'],
                    item['games'],
                    item['minutes'],
                    item['fg_pct'],
                    item['ft_pct'],
                    item['three_pt_pct'],
                    item['points'],
                    item['off_reb'],
                    item['rebounds'],
                    item['assists'],
                    team_id
                ))
        connection.commit()
        print(f"✅ {file_name} 已寫入 MySQL！")
    except Exception as e:
        print(f"❌ error occurs at {file_name}：", e)

connection.close()
