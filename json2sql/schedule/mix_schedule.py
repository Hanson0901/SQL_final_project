import json
import pymysql  # type: ignore
from itertools import permutations




def null_if_dash(val):
    return None if val == "-" or val == "" else val




def get_final_winner(score_str):
    scores = list(map(int, score_str.strip().split()))
    a_win, b_win = 0, 0
    for i in range(0, len(scores), 2):
        a, b = scores[i], scores[i+1]
        if a > b:
            a_win += 1
        elif b > a:
            b_win += 1
        if a_win == 2:
            return "A"
        if b_win == 2:
            return "B"

connection = pymysql.connect(
    host="cgusqlpj.ddns.net",
    port=3306,
    user="william",
    password="Chang0928",
    database="final_project",
    charset="utf8mb4",
)

FOLDER_PATH = r"Player_info\BWF\BWF_schedule.json"
type = 5  # BWF
with open(FOLDER_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)


not_find = set()  # 用來記錄找不到的選手
try:
    with connection.cursor() as cursor:
        for item in data:
            team_a = item.get("team_a")
            team_b = item.get("team_b")
            date = item.get("date")
            time = item.get("time")
            point_str = item.get("point", "")

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

            # 取得勝方
            winner = get_final_winner(point_str)
            if winner == "A":
                winner_team = team_a
            elif winner == "B":
                winner_team = team_b
            else:
                winner_team = None

            # 先寫入 matches_schedule
            sql_match = """
                INSERT INTO matches_schedule
                (type, team_a, team_b, date, time, point)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                sql_match,
                (
                    type,
                    team_a_id,
                    team_b_id,
                    date,
                    time,
                    winner_team
                ),
            )
            connection.commit()

            # 取得剛剛寫入的 game_no
            cursor.execute(
                "SELECT game_no FROM matches_schedule WHERE team_a = %s AND team_b = %s AND date = %s AND time = %s ORDER BY game_no DESC LIMIT 1",
                (team_a_id, team_b_id, date, time)
            )
            result = cursor.fetchone()
            if result:
                game_no = result[0]
            else:
                print(f"⚠️ 找不到 {team_a} vs {team_b} {date} {time} 的 game_no")
                continue

            # 處理分數
            point_list = [int(x) if x.strip().isdigit() else 0 for x in point_str.strip().split()]
            while len(point_list) < 6:
                point_list.append(0)

            game_1_a = point_list[0]
            game_2_a = point_list[2]
            game_3_a = point_list[4]
            game_1_b = point_list[1]
            game_2_b = point_list[3]
            game_3_b = point_list[5]

            # 處理選手
            player_id_lst = []
            for player_index in ['player_1', 'player_2', 'player_3', 'player_4']:
                player_name = item.get(player_index)
                if not player_name:
                    player_id_lst.append(None)
                    continue
                
                
                words = player_name.split()

                all_combinations = list(permutations(words))

                found = False
                for combo_name in all_combinations:
                    combo_full_name = ' '.join(combo_name)
                    cursor.execute(
                        "SELECT player_id FROM players WHERE name = %s",
                        (combo_full_name,)
                    )
                    player_id = cursor.fetchone()
                    if player_id:
                        player_id_lst.append(player_id[0])
                        found = True
                        break  # 找到就跳出
                if not found:
                    print(f"❌ 找不到 {player_name} 的 player_id")
                    not_find.add(player_name)
                    

                    
            # 寫入 bwf_match_info
            sql_info = """
                INSERT INTO bwf_match_info
                (game_no, player_1, player_2, player_3, player_4, game_1_a, game_2_a, game_3_a, game_1_b, game_2_b, game_3_b)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = [
                game_no,
                player_id_lst[0] if len(player_id_lst) > 0 else None,
                player_id_lst[1] if len(player_id_lst) > 1 else None,
                player_id_lst[2] if len(player_id_lst) > 2 else None,
                player_id_lst[3] if len(player_id_lst) > 3 else None,
                game_1_a,
                game_2_a,
                game_3_a,
                game_1_b,
                game_2_b,
                game_3_b,
            ]
            cursor.execute(sql_info, values)

            #寫入 match_platforms 
            platform_id_lst = []
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
               
                sql = f"""
                    INSERT INTO match_platforms
                    (game_no,platform_id)
                    VALUES (%s, %s)
                """
                cursor.execute(
                    sql,
                    (
                        game_no,
                        platform_id  
                    ),
                )
                connection.commit()
                print(f"✅ {team_a} vs {team_b} 已寫入 MySQL！")


            connection.commit()
            print(f"✅ {team_a} vs {team_b} 已寫入 matches_schedule 與 bwf_match_info！")
except Exception as e:
    print(f"❌ 發生錯誤: {e}")
