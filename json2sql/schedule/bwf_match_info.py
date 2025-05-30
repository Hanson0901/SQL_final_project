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

def name_split(name):
    parts = name.strip().split()
    if not parts:
        return "", ""
    # 如果第一個是全大寫
    if parts[0].isupper():
        name1 = " ".join(parts[1:]) if len(parts) > 1 else ""
        name2 = parts[0]
        return name1, name2
    # 找到第一個全大寫的單字（非第一個）
    for i in range(1, len(parts)):
        if parts[i].isupper():
            name1 = " ".join(parts[:i])
            name2 = " ".join(parts[i:])
            return name1, name2
    # 沒有全大寫的，第一個為name1，其餘為name2
    name1 = parts[0]
    name2 = " ".join(parts[1:]) if len(parts) > 1 else ""
    return name1, name2

def is_first_upper(name):
    parts = name.strip().split()
    if not parts:
        return False
    return parts[0].isupper()

TABLE = "bwf_match_info"

value_template = ["%s"] *11
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

            # 先查詢 team_id
            cursor.execute(
                "SELECT team_id FROM bwf_team WHERE team_name = %s",
                (team_a,)
            )
            team_a_id = cursor.fetchone()[0]
            
            
            cursor.execute(
                "SELECT team_id FROM bwf_team WHERE team_name = %s",
                (team_b,)
            )
            team_b_id = cursor.fetchone()[0]
            
            
            date = item.get("date")
            time = item.get("time")
            
            point_str = item.get("point", "")
            # 轉成分數 list，空的補 0
            point_list = [int(x) if x.strip().isdigit() else 0 for x in point_str.strip().split()]
            while len(point_list) < 6:
                point_list.append(0)

            # 先查詢 game_no
            game_no = None
            query = f"""
                SELECT game_no FROM matches_schedule
                WHERE team_a = %s AND team_b = %s AND date = %s AND time = %s
                LIMIT 1
            """
            cursor.execute(query, (team_a_id, team_b_id, date, time))
            result = cursor.fetchone()
            if result:
                game_no = result[0]
            else:
                print(f"⚠️ 找不到 {team_a} vs {team_b} {date} {time} 的 game_no")

           

            sql = f"""
                INSERT INTO {TABLE} 
                (game_no, player_1, player_2, player_3, player_4, game_1_a, game_2_a, game_3_a, game_1_b, game_2_b, game_3_b)
                VALUES ({para})
            """

            player_id_lst=[]
            for player_index in ['player_1', 'player_2', 'player_3', 'player_4']:
                player_name = item.get(player_index)
                if not player_name:
                    print(f"⚠️ {player_index} 的選手名稱為空，將填入 NULL")
                    player_id_lst.append(None)
                    continue
                if is_first_upper(player_name):
                    name1, name2 = name_split(player_name)
                    player_name = name1+" " + name2

                cursor.execute(
                "SELECT player_id FROM players WHERE name = %s",
                (player_name,)
                )
                player_id = cursor.fetchone()
                if player_id:
                    player_id_lst.append(player_id[0])
                else:
                    print(f"❌ 找不到 {player_name} 的 player_id，將填入 NULL")
                    
                

            
            print(f"\n正在處理 {team_a} vs {team_b} 的比賽資料...")
            print(f'team_a_id: {team_a_id}, team_b_id: {team_b_id}')
            print(f'player_id_lst: {player_id_lst}')

            game_1_a = point_list[0]
            game_2_a = point_list[2]
            game_3_a = point_list[4]
            game_1_b = point_list[1]
            game_2_b = point_list[3]
            game_3_b = point_list[5]

            
            # 將 None 處理為 NULL，否則用值
            values = [
                game_no if game_no is not None else None,
                player_id_lst[0] if len(player_id_lst) > 0 else None,
                player_id_lst[1] if len(player_id_lst) > 1 else None,
                player_id_lst[2] if len(player_id_lst) > 2 else None,
                player_id_lst[3] if len(player_id_lst) > 3 else None,
                game_1_a if game_1_a is not None else None,
                game_2_a if game_2_a is not None else None,
                game_3_a if game_3_a is not None else None,
                game_1_b if game_1_b is not None else None,
                game_2_b if game_2_b is not None else None,
                game_3_b if game_3_b is not None else None,
            ]
            cursor.execute(sql, values)
            connection.commit()
            print(f"✅ {team_a} vs {team_b} 已寫入 MySQL！")
except Exception as e:
    print(f"❌ 發生錯誤: {e}")
    print(f"執行的 SQL: SELECT game_no FROM matches_schedule WHERE team_a = {team_a_id} AND team_b = {team_b_id} AND date = '{date}' AND time = '{time}'")
                



