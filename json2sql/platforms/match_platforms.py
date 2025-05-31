import json
import pymysql  # type: ignore


# 這裡是sql設定區 要入資料改這裡~
connection = pymysql.connect(
    host="cgusqlpj.ddns.net",
    port=3306,
    user="william",
    password="Chang0928",
    database="final_project",
    charset="utf8mb4",
)


TABLE = "match_platforms"

value_template = ["%s"] * 2
para = ", ".join(value_template)

FOLDER_PATH = r"Player_info\BWF\BWF_schedule.json"

with open(FOLDER_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)
platform_id_lst=[]
try:
    with connection.cursor() as cursor:
        for item in data:
            team_a = item.get("team_a")
            team_b = item.get("team_b")
            date = item.get("date")
            time = item.get("time")
            
            # 取得 team_id
            cursor.execute("SELECT team_id FROM bwf_team WHERE team_name = %s", (team_a,))
            team_a_id = cursor.fetchone()
            if team_a_id:
                team_a_id = team_a_id[0]
            else:
                print(f"❌ 找不到 {team_a} 的 team_id")
                continue

            cursor.execute("SELECT team_id FROM bwf_team WHERE team_name = %s", (team_b,))
            team_b_id = cursor.fetchone()
            if team_b_id:
                team_b_id = team_b_id[0]
            else:
                print(f"❌ 找不到 {team_b} 的 team_id")
                continue

            cursor.execute(
                "SELECT game_no FROM matches_schedule WHERE team_a = %s AND team_b = %s AND date = %s AND time = %s ORDER BY game_no DESC LIMIT 1",
                (team_a_id, team_b_id, date, time)
            )
            result = cursor.fetchone()
            if result:
                game_no = result[0]

            channels= item.get('channels')
            for channel in channels:
                channel = channel.strip()

                cursor.execute(
                        "SELECT platform_id FROM platforms WHERE name = %s",
                        (channel,)
                    )
                platform_result = cursor.fetchone()
                
                platform_id = platform_result[0] if platform_result else None
                platform_id_lst.append(platform_id)
                

            for platform_id in platform_id_lst:
               
                # sql = f"""
                #     INSERT INTO {TABLE} 
                #     (game_no,platform_id)
                #     VALUES ({para})
                # """
                # cursor.execute(
                #     sql,
                #     (
                #         game_no,
                #         platform_id  
                #     ),
                # )
                # connection.commit()
                print(f"✅ {team_a} vs {team_b} 已寫入 MySQL！")
      
            
except Exception as e:
    print(f"❌ error occurs at {FOLDER_PATH}：", e)

