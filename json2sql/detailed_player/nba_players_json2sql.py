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


TABLE = "nba_players"

value_template = ["%s"] * 10
para = ", ".join(value_template)


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

i = 0
for file_name in file_list:
    file_path = os.path.join(FOLDER_PATH, file_name)

    # 擷取 team_id（從檔名開頭的數字）
    team_id = extract_number(file_name)

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    try:
        with connection.cursor() as cursor:

            for item in data:

                sql = f"""
                    INSERT INTO {TABLE} 
                    (player_id, jersey_number, fg_pct, ft_pct, three_pt_pct, points, off_reb, rebounds, assists, team_id)
                    VALUES ({para})
                """
                cursor.execute(
                    sql,
                    (
                        f"nba_{i}",
                        item.get("no"),
                        item.get("fg_pct"),
                        item.get("ft_pct"),
                        item.get("three_pt_pct"),
                        item.get("points"),
                        item.get("off_reb"),
                        item.get("rebounds"),
                        item.get("assists"),
                        team_id,
                    ),
                )

                i += 1
        connection.commit()
        print(f"✅ {file_name} 已寫入 MySQL！")
    except Exception as e:
        print(f"❌ error occurs at {file_name}：", e)
