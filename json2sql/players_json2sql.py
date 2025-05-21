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


TABLE = "players"

value_template = ["%s"] * 5
para = ", ".join(value_template)

# NBA 1
# F1 2
# MLB 3
# CPLB 4
# BWF 5
write_list = [
    2,
    3,
    4,
]


# NBA
if 1 in write_list:

    sport_type = 1

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
                        (player_id, sport_type, name, nationality, age)
                        VALUES ({para})
                    """
                    cursor.execute(
                        sql,
                        (
                            f"nba_{i}",
                            sport_type,
                            item.get("name"),
                            item.get("nationality"),
                            (
                                int(item["age"])
                                if str(item.get("age", "")).isdigit()
                                else (
                                    None
                                    if item.get("age") in ("-", "", None)
                                    else item.get("age")
                                )
                            ),
                        ),
                    )
                    i += 1
            connection.commit()
            print(f"✅ {file_name} 已寫入 MySQL！")
        except Exception as e:
            print(f"❌ error occurs at {file_name}：", e)

# F1
if 2 in write_list:
    pass

# MLB
if 3 in write_list:
    pass
# CPLB
if 4 in write_list:
    pass

# BWF
if 5 in write_list:

    FOLDER_PATH = "Player_info\BWF\player_info.json"
    sport_type = 5
    with open(FOLDER_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    try:
        with connection.cursor() as cursor:
            for item in data:

                def null_if_dash(val):
                    return None if val == "-" or val == "" else val

                sql = f"""
                    INSERT INTO {TABLE} 
                    (player_id, sport_type, name, nationality, age)
                    VALUES ({para})
                """
                cursor.execute(
                    sql,
                    (
                        f"bwf_{item['id']}",
                        sport_type,
                        f"{null_if_dash(item['name1'])} {null_if_dash(item['name2'])}".strip(),
                        null_if_dash(item["country"]),
                        (
                            int(item["age"])
                            if item["age"].isdigit()
                            else (
                                None
                                if item["age"] == "-" or item["age"] == ""
                                else item["age"]
                            )
                        ),
                    ),
                )
        connection.commit()
        print(f"✅ {FOLDER_PATH} 已寫入 MySQL！")
    except Exception as e:
        print(f"❌ error occurs at {FOLDER_PATH}：", e)
    # connection.close()

connection.close()
