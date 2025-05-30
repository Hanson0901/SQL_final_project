import json
import pymysql  # type: ignore
import os
import re
from geopy.geocoders import Nominatim # type: ignore

def city_to_country(city_name):
    geolocator = Nominatim(user_agent="your_app_name")
    location = geolocator.geocode(city_name, language="en")
    if location:
        # location.address 會是 "城市, 州/省, 國家"
        country = location.address.split(',')[-1].strip()
        return country
    else:
        return None
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


TABLE = "players"

value_template = ["%s"] * 5
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
                    city_name = item.get("nationality").split(",")[0].strip() if item.get("nationality") else None
                    # print(f"city_name={city_name}")
                    nationality=city_to_country(city_name)
                    # print(f"nationality={nationality}")
                     # 查 team_id
                    cursor.execute(
                        "SELECT id FROM nationality WHERE country_name = %s",
                        (nationality,)
                    )
                    city_result = cursor.fetchone()
                    city_id = city_result[0] if city_result else None

                    if city_id is None:
                        print(f"❌ 未找到國家 {nationality} 的 ID，將跳過此球員。")
                        print(f"❌ 未找到國家 {city_name} 的 ID，將跳過此球員。")

                    # print(f"city_id={city_id}")
                    sql = f"""
                        INSERT INTO {TABLE} 
                        (player_id, sport_type, name, nationality_id, age)
                        VALUES ({para})
                    """

                    
                    cursor.execute(
                        sql,
                        (
                            f"nba_{i}",
                            sport_type,
                            item.get("name"),
                            city_id,
                            item.get("age")
                        ),
                    )
                    i += 1
            connection.commit()
            print(f"✅ {file_name} 已寫入 MySQL！")
        except Exception as e:
            print(f"❌ error occurs at {file_name}：", e)

# F1
if 2 in write_list:
    FOLDER_PATH = r"Player_info\F1\f1_drivers_full_data.json"
    sport_type = 2
    with open(FOLDER_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    try:
        with connection.cursor() as cursor:

            id = 0
            for item in data:
                nationality = item.get("Country")
                nationality =   city_to_country(nationality)
                print(f"nationality={nationality}")
                cursor.execute(
                    "SELECT id FROM nationality WHERE country_name = %s",
                    (nationality,)
                )
                city_result = cursor.fetchone()
                city_id = city_result[0] if city_result else None

                if city_id is None:
                    print(f"❌ 未找到國家 {nationality} 的 ID，將跳過此球員。")
                    
                

                sql = f"""
                    INSERT INTO {TABLE} 
                    (player_id, sport_type, name, nationality_id, age)
                    VALUES ({para})
                """

                cursor.execute(
                    sql,
                    (
                        f"f1_{id}",
                        sport_type,
                        item.get("Name"),
                        city_id,
                        item.get("Age")
                    ),
                )
                id += 1
        connection.commit()
        print(f"✅ {FOLDER_PATH} 已寫入 MySQL！")
    except Exception as e:
        print(f"❌ error occurs at {FOLDER_PATH}：", e)
# MLB
if 3 in write_list:
    pass
# CPLB
if 4 in write_list:
    pass

# BWF
if 5 in write_list:

    FOLDER_PATH = r"Player_info\BWF\player_info.json"
    sport_type = 5
    with open(FOLDER_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    try:
        with connection.cursor() as cursor:
            for item in data:
                
                
                name = f"{item['name1']} {item['name2']}"
                
                nationality = item.get("country")

                cursor.execute(
                    "SELECT name FROM players WHERE name = %s",
                    (name,)
                )
                name_result = cursor.fetchone()
                name_id = name_result[0] if name_result else None
                
                if name_id is not None:
                    print(f"⚠️ 已經找到過這名選手: {name}，跳過")
                    continue
                
                id=f"bwf_{item['id']}"
                # print(f"nationality={nationality}")
                cursor.execute(
                    "SELECT id FROM nationality WHERE country_name = %s",
                    (nationality,)
                )
                city_result = cursor.fetchone()
                # print(f"id={id}")
                city_id = city_result[0] if city_result else None
                if city_id is None:
                    print(f"❌ 未找到國家 {nationality} 的 ID，將跳過此球員。")
                    print(f"city_id={city_id}")
            
                sql = f"""
                    INSERT INTO {TABLE} 
                    (player_id, sport_type, name, nationality_id, age)
                    VALUES ({para})
                """
                
                cursor.execute(
                    sql,
                    (
                        id,
                        sport_type,
                        name,
                        city_id,
                        int(item["age"]) if str(item.get("age", "")).isdigit() else None
                        
                    ),
                )
                connection.commit()
                print(f"✅ {id} 已寫入 MySQL！")
    except Exception as e:
        print(f"❌ error occurs at {FOLDER_PATH}：", e)
    # connection.close()

connection.close()
