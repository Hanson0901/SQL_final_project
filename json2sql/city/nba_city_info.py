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
write_list = ['players', 'teams']  
# ['players', 'teams']  # ['players']  # ['teams']

TABLE = "city_info"


value_template = ["%s"] * 2
para = ", ".join(value_template)
country_id = 235 
if 'players' in write_list:
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

        # 擷取 team_id（從檔名開頭的數字）
        team_id = extract_number(file_name)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        try:
            with connection.cursor() as cursor:

                for item in data:
                    nationality = item.get("nationality").split(",")[0].strip() if item.get("nationality") else None
                    # 檢查是否已存在相同 nationality
                    check_sql = f"SELECT COUNT(*) FROM {TABLE} WHERE city_name = %s"
                    cursor.execute(check_sql, (nationality,))
                    exists = cursor.fetchone()[0]
                    if exists:
                        print(f"已存在: {nationality}")
                    else:
                        print(f"新增: {nationality}")
                    
            
                        sql = f"""
                            INSERT INTO {TABLE} 
                            (city_name, country_id)
                            VALUES ({para})
                        """

                        
                        cursor.execute(
                            sql,
                            (
                                nationality,
                                country_id,
                            ),
                        )
            connection.commit()
            print(f"✅ {file_name} 已寫入 MySQL！")
        except Exception as e:
            print(f"❌ error occurs at {file_name}：", e)

if  'teams' in write_list:
    teams_file_path=r"Player_info\NBA\team_d.json"
    with open(teams_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        team_name = item.get("team_name")
        try:
            with connection.cursor() as cursor:
                nationality = item.get("city").split(",")[0].strip() if item.get("city") else None
                # 檢查是否已存在相同 nationality
                check_sql = f"SELECT COUNT(*) FROM {TABLE} WHERE city_name = %s"
                cursor.execute(check_sql, (nationality,))
                exists = cursor.fetchone()[0]
                if exists:
                    print(f"已存在: {nationality}")
                else:
                    print(f"新增: {nationality}")
                

                    sql = f"""
                        INSERT INTO {TABLE} 
                        (city_name, country_id)
                        VALUES ({para})
                    """

                    
                    cursor.execute(
                        sql,
                        (
                            nationality,
                            country_id,
                        ),
                    )
                connection.commit()
                print(f"✅ {team_name} 已寫入 MySQL！")
        except Exception as e:
            print(f"❌ error occurs at {team_name}：", e)