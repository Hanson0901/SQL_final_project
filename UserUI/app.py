from flask import Flask, render_template, request, jsonify
import pymysql
from datetime import datetime, date, time, timedelta

def fix_timedelta(row):
    for key, val in row.items():
        if isinstance(val, timedelta):
            row[key] = (datetime.min + val).time().strftime("%H:%M:%S")  # 把 timedelta 轉成 HH:MM:SS
        elif isinstance(val, (datetime, date)):
            row[key] = val.strftime("%Y-%m-%d")  # 把日期轉成 YYYY-MM-DD
    return row
app = Flask(__name__)

#連資料庫
connection = pymysql.connect(
    host='cgusqlpj.ddns.net',
    port = 3306,
    user='uuriglass',
    password='laby800322',
    database='final_project',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

@app.route("/")
def home():
    return render_template("index.html")

player_table_map = {
        "1": "nba_players",
        "2": "f1_drivers",
        "3": "baseball_players",
        "4": "baseball_players",
        "5": "bwf_players"
    }

team_table_map = {
        "1": "nba_team",
        "2": "f1_team",
        "3": "bs_team",   # MLB
        "4": "bs_team",   # CPBL
        "5": "bwf_team"        
    }


#===============================比賽查詢=====================================#
@app.route("/search")
def search():
    return render_template('search.html')

@app.route("/api/search_matches")
def search_matches():
    from datetime import time, timedelta

    print("📥 接收到的參數：", request.args.to_dict())

    sport = request.args.get('sport')
    query_type = request.args.get('query_type')
    keyword = request.args.get('keyword')
    date = request.args.get('date')

    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT m.*, ta.team_name AS team_a_name, tb.team_name AS team_b_name
                FROM matches_schedule m
                JOIN teams ta ON m.team_a = ta.team_id
                JOIN teams tb ON m.team_b = tb.team_id
                WHERE m.type = %s
            """
            params = [sport]
            team_info = None

            if keyword and query_type == "team":
                try:
                    team_id = int(keyword)
                    sql += " AND (m.team_a = %s OR m.team_b = %s)"
                    params.extend([team_id, team_id])

                    # ⭐ 查隊名
                    cursor.execute("SELECT team_id, team_name FROM teams WHERE team_id = %s", (team_id,))
                    team_info = cursor.fetchone()

                except ValueError:
                    print("❌ 無效 team_id：", keyword)
                    return jsonify([])

            elif keyword and query_type == "player":
                table = player_table_map.get(sport)
                if not table:
                    print("❌ 找不到子表對應的 sport =", sport)
                    return jsonify([])

                cursor.execute(f"SELECT team_id FROM {table} WHERE player_id = %s", (keyword,))
                result = cursor.fetchone()
                if not result:
                    print(f"❌ 在 {table} 查無 player_id：", keyword)
                    return jsonify([])

                team_id = result["team_id"]
                sql += " AND (m.team_a = %s OR m.team_b = %s)"
                params.extend([team_id, team_id])

                cursor.execute("SELECT team_id, team_name FROM teams WHERE team_id = %s", (team_id,))
                team_info = cursor.fetchone()

            if date:
                sql += " AND m.date >= %s"
                params.append(date)

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            for row in rows:
                for k, v in row.items():
                    if isinstance(v, (time, timedelta)):
                        row[k] = v.strftime("%H:%M") if isinstance(v, time) else str(v)

            return jsonify({
                "team": team_info if query_type in ["player", "team"] else None,
                "matches": rows
            })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500



@app.route('/api/get_team_name_by_player')
def get_team_name_by_player():
    sport = request.args.get("sport")
    player_id = request.args.get("player_id")

    table = player_table_map.get(sport)
    if not table:
        return jsonify({"error": "invalid sport"}), 400

    try:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT t.team_name
                FROM {table} p
                JOIN teams t ON p.team_id = t.team_id
                WHERE p.player_id = %s
            """, (player_id,))
            result = cursor.fetchone()
            return jsonify({"team_name": result["team_name"] if result else None})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/get_team_name")
def get_team_name():
    team_id = request.args.get("team_id")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT team_name FROM teams WHERE team_id = %s", (team_id,))
            result = cursor.fetchone()
            if result:
                return jsonify({"team_name": result["team_name"]})
            else:
                return jsonify({"team_name": None})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/get_player_name")
def get_player_name():
    player_id = request.args.get("player_id")
    sport = request.args.get("sport")

    table = player_table_map.get(sport)
    if not table:
        return jsonify({"player_name": None})

    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT name FROM {table} WHERE player_id = %s", (player_id,))
            result = cursor.fetchone()
            if result:
                return jsonify({"player_name": result["name"]})
            else:
                return jsonify({"player_name": None})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/get_options")
def get_options():
    sport_type = request.args.get("sport_type", type=int)
    query_type = request.args.get("query_type")  # "team" or "player"


    print("🧪 查詢 options：", query_type, sport_type)
    try:
        with connection.cursor() as cursor:
            if query_type == "team":
                cursor.execute(
                    "SELECT team_id AS id, team_name AS name FROM teams WHERE sport_type = %s",
                    (sport_type,)
                )
            elif query_type == "player":
                cursor.execute(
                    "SELECT player_id AS id, name FROM players WHERE sport_type = %s",
                    (sport_type,)
                )
            else:
                return jsonify([])

            return jsonify(cursor.fetchall())

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#===============================比賽查詢=====================================#




#===============================混合查詢=====================================#
@app.route("/mix_search")
def mix_search():
    return render_template('mix_search.html')
    
@app.route("/api/mix_search")
def api_mix_search():
    query_type = request.args.get("type")  # player / team / match
    keyword = request.args.get("keyword", "").strip().lower()
    sport_type = request.args.get("sport_type")

    print("🔍 參數：", query_type, keyword, sport_type)


    try:
        with connection.cursor() as cursor:
            if query_type == "player":
                table = player_table_map.get(sport_type)
                if not table:
                    return jsonify({"error": "Unknown sport_type"}), 400

                print(f"👉 SQL: 查詢 {table} 球員 ID")

                if(sport_type != "5"):
                    cursor.execute(f"""
                        SELECT 
                            p.name, 
                            p.player_id, 
                            p.age, 
                            n.country_name AS country, 
                            t.team_name,  -- ✅ 新增
                            x.*
                        FROM players p
                        JOIN {table} x ON p.player_id = x.player_id
                        LEFT JOIN nationality n ON p.nationality_id = n.id
                        LEFT JOIN teams t ON x.team_id = t.team_id  -- ✅ 新增 JOIN
                        WHERE x.player_id = %s
                    """, (keyword,))
                    return jsonify(cursor.fetchall())
                else:
                    cursor.execute(f"""
                        SELECT p.name, p.player_id, p.age, n.country_name AS country, x.*
                        FROM players p
                        JOIN {table} x ON p.player_id = x.player_id
                        LEFT JOIN nationality n ON p.nationality_id = n.id
                        WHERE x.player_id = %s
                    """, (keyword,))
                    return jsonify(cursor.fetchall())

            
            elif query_type == "team":
                
                team_id = keyword  # keyword 傳的是 team_id
                print(f"👉 SQL: 查詢 team_id = {team_id} 的隊伍")

                table = team_table_map.get(sport_type)
                if not table and sport_type == "5":
                    # BWF → 根據國籍名當隊名顯示
                    cursor.execute("""
                        SELECT n.id AS team_id, n.country_name AS team_name
                        FROM nationality n
                        WHERE n.nationality_id = %s
                    """, (team_id,))
                    return jsonify(cursor.fetchall())

                if not table:
                    return jsonify({"error": "Unknown sport_type"}), 400

                if sport_type in ["1", "3", "4"]:  # 1: NBA, 3: MLB, 4: CPBL 這些有 city_id
                    cursor.execute(f"""
                        SELECT t.*, x.*, c.city_name AS city_name, c.abbr AS abbr
                        FROM teams t
                        LEFT JOIN {table} x ON t.team_id = x.team_id
                        LEFT JOIN city_info c ON x.city_id = c.city_id
                        WHERE t.team_id = %s
                    """, (team_id,))
                else:
                    cursor.execute(f"""
                        SELECT t.*, x.*
                        FROM teams t
                        LEFT JOIN {table} x ON t.team_id = x.team_id
                        WHERE t.team_id = %s
                    """, (team_id,))
                return jsonify(cursor.fetchall())


            elif query_type == "event":
                try:
                    game_no = int(keyword)
                except ValueError:
                    return jsonify({"error": "無效的 game_no"}), 400

                cursor.execute("""
                    SELECT m.*, ta.team_name AS team_a_name, tb.team_name AS team_b_name
                    FROM matches_schedule m
                    JOIN teams ta ON m.team_a = ta.team_id
                    JOIN teams tb ON m.team_b = tb.team_id
                    WHERE m.game_no = %s AND m.type = %s
                """, (game_no, sport_type))

                rows = cursor.fetchall()
                rows = [fix_timedelta(row) for row in rows]  # 🔧 轉換 timedelta
                return jsonify(rows)

            else:
                return jsonify({"error": "query_type not supported"}), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/get_keywords")
def get_keywords():
    query_type = request.args.get("type")
    sport_type = request.args.get("sport_type")

    try:
        with connection.cursor() as cursor:
            if query_type == "player":
                subtable = player_table_map.get(sport_type)
                if not subtable:
                    return jsonify([])

                cursor.execute(f"""
                    SELECT p.player_id AS id, p.name
                    FROM players p
                    JOIN {subtable} x ON p.player_id = x.player_id
                """)
                return jsonify(cursor.fetchall())

            elif query_type == "team":
                if sport_type == "5":
                    cursor.execute("""
                        SELECT nid AS id, country_name AS name 
                        FROM nationality
                    """)
                    return jsonify(cursor.fetchall())
                
                elif sport_type in ("3", "4"):  # MLB / CPBL 特別處理
                    league = "MLB" if sport_type == "3" else "CPBL"
                    cursor.execute("""
                        SELECT team_id AS id, team_name AS name 
                        FROM bs_team
                        WHERE league = %s
                    """, (league,))
                    return jsonify(cursor.fetchall())
                
                else:
                    cursor.execute("""
                        SELECT team_id AS id, team_name AS name 
                        FROM teams 
                        WHERE sport_type = %s
                    """, (sport_type,))
                    return jsonify(cursor.fetchall())


            elif query_type == "event":
                cursor.execute("""
                    SELECT m.game_no, ta.team_name AS team_a_name, tb.team_name AS team_b_name
                    FROM matches_schedule m
                    JOIN teams ta ON m.team_a = ta.team_id
                    JOIN teams tb ON m.team_b = tb.team_id
                    WHERE m.type = %s
                """, (sport_type,))

                rows = cursor.fetchall()
                return jsonify([
                    {
                        "id": row["game_no"],
                        "name": f'{row["team_a_name"]} vs {row["team_b_name"]}'
                    } for row in rows
                ])



            return jsonify([])

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
#===============================混合查詢=====================================#



#===============================比賽預約=====================================#
@app.route("/recent_match")
def recent_match():
    return render_template("recent_match.html")

@app.route('/api/matches')
def get_matches():
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    m.game_no,
                    CONCAT(ta.team_name, ' vs ', tb.team_name) AS match_name,
                    m.type,
                    m.date,
                    m.time,
                    p.name AS platform_name
                FROM matches_schedule m
                JOIN teams ta ON m.team_a = ta.team_id
                JOIN teams tb ON m.team_b = tb.team_id
                JOIN match_platforms mp ON m.game_no = mp.game_no
                JOIN platforms p ON mp.platform_id = p.platform_id
                ORDER BY m.date, m.time
            """)
            rows = cursor.fetchall()

        matches = {}
        for row in rows:
            # 安全解析時間
            raw_time = row["time"]
            if isinstance(raw_time, timedelta):
                total_seconds = int(raw_time.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                time_str = f"{hours:02d}:{minutes:02d}"
            else:
                time_str = str(raw_time)

            # 日期分類
            date = row["date"].strftime("%Y-%m-%d")
            if date not in matches:
                matches[date] = []

            matches[date].append({
                "name": row["match_name"],
                "time": time_str,
                "platform": row["platform_name"],
                "type": row["type"] 
            })

        return jsonify(matches)

    except Exception as e:
        print("❌ matches 查詢錯誤：", e)
        return jsonify({"error": str(e)}), 500

@app.route('/api/bookings/user/<uid>', methods=['GET'])
def get_user_bookings(uid):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    m.date,
                    CONCAT(ta.team_name, ' vs ', tb.team_name) AS match_name,
                    m.type,
                    m.time,
                    p.name AS platform_name
                FROM reminders r
                JOIN matches_schedule m ON r.game_no = m.game_no
                JOIN teams ta ON m.team_a = ta.team_id
                JOIN teams tb ON m.team_b = tb.team_id
                JOIN match_platforms mp ON m.game_no = mp.game_no
                JOIN platforms p ON mp.platform_id = p.platform_id
                WHERE r.user_id = %s
            """, (uid,))
            rows = cursor.fetchall()

        result = {}
        for row in rows:
            date = row["date"].strftime("%Y-%m-%d")

            # ✅ 安全轉 time_str
            raw_time = row["time"]
            if isinstance(raw_time, timedelta):
                total_seconds = int(raw_time.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                time_str = f"{hours:02d}:{minutes:02d}"
            else:
                time_str = str(raw_time)

            if date not in result:
                result[date] = []

            result[date].append({
                "name": row["match_name"],
                "time": time_str,
                "platform": row["platform_name"],
                "type": row["type"]
            })

        return jsonify(result)

    except Exception as e:
        print("❌ bookings 查詢錯誤：", e)
        return jsonify({"error": str(e)}), 500

@app.route('/api/bookings/user/<uid>', methods=['POST'])
def save_user_bookings(uid):
    data = request.json 

    try:
        with connection.cursor() as cursor:
            # 刪掉舊資料
            cursor.execute("DELETE FROM reminders WHERE user_id = %s", (uid,))

            # 新增資料
            for date, matches in data.items():
                for match in matches:
                    # 依名稱、日期、時間找出對應的 game_no
                    cursor.execute("""
                        SELECT m.game_no
                        FROM matches_schedule m
                        JOIN teams ta ON m.team_a = ta.team_id
                        JOIN teams tb ON m.team_b = tb.team_id
                        WHERE m.date = %s
                        AND m.time = %s
                        AND CONCAT(ta.team_name, ' vs ', tb.team_name) = %s
                    """, (date, match["time"] + ":00", match["name"]))
                    result = cursor.fetchone()
                    if result:
                        game_no = result["game_no"]
                        cursor.execute("""
                            INSERT INTO reminders (user_id, game_no)
                            VALUES (%s, %s)
                        """, (uid, game_no))

        connection.commit()
        return jsonify({"status": "saved"}), 200

    except Exception as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/bookings/user/<uid>', methods=['DELETE'])
def delete_user_bookings(uid):
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM reminders WHERE user_id = %s", (uid,))
        connection.commit()
        return jsonify({"status": "deleted"}), 200
    except Exception as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/platform/rank/<uid>')
def platform_rank(uid):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    p.platform_id,
                    p.name AS platform_name,
                    COUNT(*) AS usage_count
                FROM reminders r
                JOIN match_platforms mp ON r.game_no = mp.game_no
                JOIN platforms p ON mp.platform_id = p.platform_id
                WHERE r.user_id = %s
                GROUP BY p.platform_id
                ORDER BY usage_count DESC
            """, (uid,))
            data = cursor.fetchall()
        return jsonify(data)
    except Exception as e:
        print("❌ 平台統計錯誤：", e)
        return jsonify({"error": str(e)}), 500


#===============================比賽預約=====================================#



if __name__ == "__main__":
    app.run(port = 5050, host='0.0.0.0', debug=True)
