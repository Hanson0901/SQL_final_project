from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import pymysql
from datetime import datetime, date, time, timedelta

app = Flask(__name__)
app.secret_key = "yuuuuuuuriz"

#連資料庫
connection = pymysql.connect(
    # host='cgusqlpj.ddns.net',
    # port = 3306,
    host="localhost",
    user='uuriglass',
    password='laby800322',
    # database='final_project',
    database="test",
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

def fix_timedelta(row):
    for key, val in row.items():
        if isinstance(val, timedelta):
            row[key] = (datetime.min + val).time().strftime("%H:%M:%S")  # 把 timedelta 轉成 HH:MM:SS
        elif isinstance(val, (datetime, date)):
            row[key] = val.strftime("%Y-%m-%d")  # 把日期轉成 YYYY-MM-DD
    return row

#首頁
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin/super")
def super_admin():
    admin_id = session.get("admin_id")

    with connection.cursor() as cursor:
        # 再次驗證是否為最高權限
        cursor.execute("SELECT permission_level FROM admins WHERE admin_id = %s", (admin_id,))
        result = cursor.fetchone()

        if not result or result["permission_level"] != 2:
            return "❌ 權限不足", 403

        # 撈出所有管理員（不再篩選 permission_level）
        cursor.execute("SELECT * FROM admins")
        admins = cursor.fetchall()

    return render_template("super_admin.html", admins=admins, session=session)


@app.route("/api/admins/<int:admin_id>", methods=["PUT"])
def update_admin(admin_id):
    if session.get("permission_level") != 2:
        return jsonify(success=False, message="權限不足"), 403

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE admins SET user_name = %s, password = %s WHERE admin_id = %s
        """, (username, password, admin_id))
        connection.commit()

    return jsonify(success=True, message="✅ 修改成功")

@app.route("/api/admins/<int:admin_id>", methods=["DELETE"])
def delete_admin(admin_id):
    if session.get("permission_level") != 2:
        return jsonify(success=False, message="權限不足"), 403

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM admins WHERE admin_id = %s", (admin_id,))
        connection.commit()

    return jsonify(success=True, message="🗑️ 刪除成功")

@app.route("/api/admins/<int:admin_id>/upgrade", methods=["POST"])
def upgrade_admin(admin_id):
    if session.get("permission_level") != 2:
        return jsonify(success=False, message="權限不足"), 403

    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE admins SET permission_level = 2 WHERE admin_id = %s
        """, (admin_id,))
        connection.commit()

    return jsonify(success=True, message="🔼 已升級為最高權限")


@app.route("/foruser")
def foruser():
    return render_template("foruser.html")

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
@app.route("/match_search")
def match_search():
    return render_template('search.html')

@app.route("/api/search_matches")
def search_matches():

    print("📥 接收到的參數：", request.args.to_dict())

    sport = request.args.get('sport')
    query_type = request.args.get('query_type')
    keyword = request.args.get('keyword')
    date = request.args.get('date')
    
    if sport == "2":
        sql = """
            SELECT m.*, ta.team_name AS team_a_name
            FROM matches_schedule m
            JOIN teams ta ON m.team_a = ta.team_id
            WHERE m.type = %s
        """
        params = [sport]

        if date:
            sql += " AND m.date = %s"
            params.append(date)

    else:
        sql = """
            SELECT m.*, ta.team_name AS team_a_name, tb.team_name AS team_b_name
            FROM matches_schedule m
            JOIN teams ta ON m.team_a = ta.team_id
            JOIN teams tb ON m.team_b = tb.team_id
            WHERE m.type = %s
        """
        params = [sport]

        if date:
            sql += " AND m.date = %s"
            params.append(date)


    try:
        with connection.cursor() as cursor:
            team_info = None
            
            if query_type == "team":
                
                if sport == "2":
                    team_info = {"team_name": "F1 所有賽事"}
                elif keyword:
                    
                    try:
                        team_id = int(keyword)
                        sql += " AND (m.team_a = %s OR m.team_b = %s)"
                        params.extend([team_id, team_id])

                        # 查隊名
                        cursor.execute("SELECT team_id, team_name FROM teams WHERE team_id = %s", (team_id,))
                        team_info = cursor.fetchone()
                    except ValueError:
                        print("❌ 無效 team_id：", keyword)
                        return jsonify([])
                else:
                    return jsonify([])  # 非 F1 但沒給 keyword，也不查
            elif keyword and query_type == "player":
                table = player_table_map.get(sport)
                if not table:
                    print("找不到子表對應的 sport =", sport)
                    return jsonify([])

                cursor.execute(f"SELECT team_id FROM {table} WHERE player_id = %s", (keyword,))
                result = cursor.fetchone()
                if not result:
                    print(f"在 {table} 查無 player_id：", keyword)
                    return jsonify([])

                team_id = result["team_id"]
                sql += " AND (m.team_a = %s OR m.team_b = %s)"
                params.extend([team_id, team_id])

                cursor.execute("SELECT team_id, team_name FROM teams WHERE team_id = %s", (team_id,))
                team_info = cursor.fetchone()

            if sport != "2" and date:
                sql += " AND m.date = %s"
                params.append(date)

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            print("執行 SQL:", sql)
            print("參數:", params)

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

    print("參數：", query_type, keyword, sport_type)


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
                            t.team_name,
                            x.*
                        FROM players p
                        JOIN {table} x ON p.player_id = x.player_id
                        LEFT JOIN nationality n ON p.nationality_id = n.id
                        LEFT JOIN teams t ON x.team_id = t.team_id 
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
                    # BWF → 國籍當隊伍名稱顯示
                    cursor.execute("""
                        SELECT n.id AS team_id, n.country_name AS team_name
                        FROM nationality n
                        WHERE n.nationality_id = %s
                    """, (team_id,))
                    return jsonify(cursor.fetchall())

                if not table:
                    return jsonify({"error": "Unknown sport_type"}), 400

                # ✅ 只撈出 xx_team 的資訊
                cursor.execute(f"""
                    SELECT *
                    FROM {table}
                    WHERE team_id = %s
                """, (team_id,))

                return jsonify(cursor.fetchall())


            elif query_type == "event":
                if sport_type == "2":  # F1 → 用 type，只抓 match_name
                    cursor.execute("""
                        SELECT m.match_name, m.date, m.time, m.point, m.type
                        FROM matches_schedule m
                        WHERE m.type = %s
                    """, (sport_type,))
                    rows = cursor.fetchall()
                    rows = [fix_timedelta(row) for row in rows]
                    return jsonify(rows)

                # 其他類型 → 用 game_no 查詢
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
                rows = [fix_timedelta(row) for row in rows]
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
                        WHERE sport_type = %s AND team_name NOT LIKE '%%Grand Prix%%'
                    """, (sport_type,))
                    return jsonify(cursor.fetchall())


            elif query_type == "event":
                if sport_type == "2":  # F1 → 不用 game_no，只抓 match_name
                    cursor.execute("""
                        SELECT m.game_no, m.match_name AS match_name
                        FROM matches_schedule m
                        WHERE m.type = %s
                    """, (sport_type,))

                    rows = cursor.fetchall()

                    return jsonify([
                        {
                            "id": row["game_no"],
                            "name": f'{row["match_name"]}'
                        }for row in rows
                    ])
                
                else:
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


@app.route("/admin_entry", methods=["POST"])
def admin_entry():
    data = request.get_json()
    entered_key = data.get("admin_key")
    expected_key = "8432"  # ✅ 你可以改成你想要的密碼

    if entered_key == expected_key:
        return jsonify(success=True)
    else:
        return jsonify(success=False)
    
#最高ADMIN
top_admin = [
    {
        "username" : "uuriglass",
        "password" : "ssalgiruu"
    }
]

is_top = False;

#==================================登入/註冊介面==============================#
@app.route('/foradmin')
def foradmin():
    return render_template("foradmin.html")

# 登入
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # ✅ 檢查欄位
    if not username or not password:
        return jsonify(success=False, message="請輸入帳號與密碼"), 400

    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # ✅ 預防 SQL Injection，已使用 %s 是對的
            cursor.execute(
                "SELECT * FROM admins WHERE user_name = %s AND password = %s",
                (username, password)
            )
            matched = cursor.fetchone()

            if matched:
                #判斷是不是最高管理員
                is_top = any(u['username'] == username and u['password'] == password for u in top_admin)
    
                session['username'] = matched['user_name']
                session['admin_id'] = matched['admin_id']
                session["permission_level"] = matched["permission_level"]
                session['is_top'] = is_top;

                return jsonify(success=True,
                                username=matched['user_name'],
                                admin_id=matched['admin_id'],
                                is_super =  session.get("permission_level") == 2,
                                is_top=is_top
                              )
                
            else:
                return jsonify(success=False, message="帳號或密碼錯誤")
    except Exception as e:
        return jsonify(success=False, message=f"登入時發生錯誤: {str(e)}"), 500

# 註冊
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify(success=False, message='帳號和密碼不得為空')

    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 檢查帳號是否已存在
            cursor.execute("SELECT * FROM admins WHERE user_name = %s", (username,))
            if cursor.fetchone():
                return jsonify(success=False, message='帳號已存在')

            # 插入新使用者
            cursor.execute(
                "INSERT INTO admins (user_name, password) VALUES (%s, %s)",
                (username, password)
            )
            connection.commit()

            # 取得剛新增的 ID
            new_id = cursor.lastrowid

        return jsonify(success=True, message=f'註冊成功, 您的 ID 為 {new_id}, 使用者名稱為 {username}')
    except Exception as e:
        return jsonify(success=False, message=f'註冊失敗: {str(e)}'), 500
#==================================登入/註冊介面==============================#


@app.route('/control_panel')
def dashboard():

    if "admin_id" not in session:
        return redirect(url_for("index"))

    is_super = session.get("permission_level") == 2

    return render_template("adminUI.html", is_super=is_super)


#=================================SQL=======================================#
@app.route("/sql")
def sql():
    return render_template("sql.html")

@app.route("/api/search_match_advanced")
def search_match_advanced():
    sport = request.args.get("sport")
    date = request.args.get("date")
    team_a = request.args.get("team_a")
    team_b = request.args.get("team_b")

    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            conditions = []
            params = []

            if sport:
                conditions.append("m.type = %s")
                params.append(sport)

            if date:
                conditions.append("m.date = %s")
                params.append(date)

            if team_a:
                conditions.append("m.team_a = %s")
                params.append(team_a)

            if team_b:
                conditions.append("m.team_b = %s")
                params.append(team_b)

            where_clause = " AND ".join(conditions) if conditions else "1=1"

            cursor.execute(f"""
                SELECT m.*, 
                       ta.team_name AS team_a_name, 
                       tb.team_name AS team_b_name
                FROM matches_schedule m
                LEFT JOIN teams ta ON m.team_a = ta.team_id
                LEFT JOIN teams tb ON m.team_b = tb.team_id
                WHERE {where_clause}
            """, params)

            matches = cursor.fetchall()

            # 轉換時間
            for m in matches:
                if isinstance(m["time"], timedelta):
                    total_seconds = int(m["time"].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    m["time"] = f"{hours:02}:{minutes:02}"

            return jsonify(matches=matches)

    except Exception as e:
        print("❌ 查詢錯誤：", e)
        return jsonify(matches=[], error=str(e)), 500


@app.route("/api/add-many", methods=["POST"])
def add_many():
    data = request.get_json()
    new_matches = data.get("matches", [])

    if not new_matches:
        return jsonify(success=False, message="沒有資料可新增"), 400

    added = 0

    try:
        with connection.cursor() as cursor:
            for m in new_matches:
                if m.get("type") == "2":
                    # ✅ F1 處理：用 match_name 找 team_id
                    match_name = m.get("match_name")
                    if not match_name or not m.get("date") or not m.get("time"):
                        continue

                    # 查隊伍是否已存在
                    cursor.execute("SELECT team_id FROM teams WHERE team_name = %s AND sport_type = 2", (match_name,))
                    team = cursor.fetchone()

                    if team:
                        team_a_id = team["team_id"]
                    else:
                        # ✅ 若不存在就新增隊伍（F1場站）
                        cursor.execute("INSERT INTO teams (team_name, sport_type) VALUES (%s, 2)", (match_name,))
                        team_a_id = cursor.lastrowid

                    # 檢查是否有重複
                    cursor.execute("""
                        SELECT COUNT(*) AS count FROM matches_schedule 
                        WHERE team_a = %s AND date = %s AND time = %s
                    """, (team_a_id, m["date"], m["time"]))
                    if cursor.fetchone()["count"] > 0:
                        continue

                    # 寫入 F1 賽事（team_b 為 NULL）
                    cursor.execute("""
                        INSERT INTO matches_schedule (type, team_a, team_b, date, time, point)
                        VALUES (2, %s, NULL, %s, %s, %s)
                    """, (team_a_id, m["date"], m["time"], m.get("point")))
                    added += 1

                else:
                    # 🏀⚾ 一般比賽處理
                    if not all(k in m for k in ("team_a", "team_b", "date", "time")):
                        continue

                    # 取得隊伍名稱
                    cursor.execute("SELECT team_name FROM teams WHERE team_id = %s", (m["team_a"],))
                    team_a_name = cursor.fetchone()
                    cursor.execute("SELECT team_name FROM teams WHERE team_id = %s", (m["team_b"],))
                    team_b_name = cursor.fetchone()

                    if not team_a_name or not team_b_name:
                        continue

                    # 查 type
                    cursor.execute("SELECT sport_type FROM teams WHERE team_id = %s", (m["team_a"],))
                    sport = cursor.fetchone()
                    if not sport:
                        continue
                    sport_type = sport["sport_type"]

                    # 檢查是否重複
                    cursor.execute("""
                        SELECT COUNT(*) AS count FROM matches_schedule 
                        WHERE team_a = %s AND team_b = %s AND date = %s AND time = %s
                    """, (m["team_a"], m["team_b"], m["date"], m["time"]))
                    if cursor.fetchone()["count"] > 0:
                        continue

                    cursor.execute("""
                        INSERT INTO matches_schedule (type, team_a, team_b, date, time, point)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (sport_type, m["team_a"], m["team_b"], m["date"], m["time"], m.get("point")))
                    added += 1

        connection.commit()
        return jsonify(success=True, count=added)

    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


@app.route("/api/match/<int:game_no>")
def get_match_by_id(game_no):
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT m.*, ta.team_name AS team_a_name, tb.team_name AS team_b_name
                FROM matches_schedule m
                LEFT JOIN teams ta ON m.team_a = ta.team_id
                LEFT JOIN teams tb ON m.team_b = tb.team_id
                WHERE m.game_no = %s
            """, (game_no,))
            match = cursor.fetchone()

            if not match:
                return jsonify(success=False, message="查無此比賽")

            # ✅ 轉換時間 (timedelta) 成 HH:MM
            if isinstance(match["time"], timedelta):
                total_seconds = int(match["time"].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                match["time"] = f"{hours:02}:{minutes:02}"

            # ✅ 轉換日期成 YYYY-MM-DD 字串
            if isinstance(match["date"], (datetime, date)):
                match["date"] = match["date"].strftime("%Y-%m-%d")

            return jsonify(success=True, match=match)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

@app.route("/api/teams")
def get_teams():
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT team_id, team_name, sport_type 
                FROM teams 
                WHERE (sport_type != 2 OR team_name LIKE %s)
            """, ("%Grand Prix%",))
            teams = cursor.fetchall()
        return jsonify(teams)
    except Exception as e:
        print("❌ get_teams 失敗：", e)
        return jsonify([], 500)


@app.route("/api/edit/<int:game_no>", methods=["POST"])
def edit_match(game_no):
    data = request.get_json()
    team_a = data.get("team_a")
    team_b = data.get("team_b")
    date = data.get("date")
    time = data.get("time")
    point = data.get("point")

    try:
        with connection.cursor() as cursor:
            # 查目前是什麼運動類型
            cursor.execute("SELECT type FROM matches_schedule WHERE game_no = %s", (game_no,))
            result = cursor.fetchone()
            if not result:
                return jsonify(success=False, message="查無此比賽")

            sport_type = result["type"]

            if sport_type == 2:
                # F1：只更新 team_a、date、time、point，不動 team_b
                cursor.execute("""
                    UPDATE matches_schedule
                    SET team_a = %s, date = %s, time = %s, point = %s
                    WHERE game_no = %s
                """, (team_a, date, time, point, game_no))
            else:
                # 其他運動：更新 team_a、team_b、date、time、point
                cursor.execute("""
                    UPDATE matches_schedule
                    SET team_a = %s, team_b = %s, date = %s, time = %s, point = %s
                    WHERE game_no = %s
                """, (team_a, team_b, date, time, point, game_no))

        connection.commit()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500



@app.route("/api/delete/<int:game_no>", methods=["DELETE"])
def delete_match(game_no):
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM matches_schedule WHERE game_no = %s", (game_no,))
        connection.commit()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


#=================================SQL=======================================#


#=========================Announcement====================================#

@app.route('/announcements')
def announcements():
    username = session.get('username')
    admin_id = session.get('admin_id')

    if not username or not admin_id:
        return redirect(url_for('foradmin'))
    
    return render_template("announcements.html", admin_id=admin_id, username=username, is_top = is_top)

#查資料表
@app.route('/announcements.json')
def announcements_json():
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT a.*, u.user_name AS admin_name
                FROM announcements a
                LEFT JOIN admins u ON a.admin_id = u.admin_id
                ORDER BY a.a_datetime DESC
            """)
            announcements = cursor.fetchall()
        return jsonify(announcements)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

# 公告處理
@app.route('/api/announce', methods=['POST'])
def announce():
    data = request.get_json()
    content = data.get("content")
    admin_id = data.get("admin_id")
    datetime = data.get("datetime")

    if not content or admin_id is None or not datetime:
        return jsonify(success=False, message="缺少必要欄位")

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO announcements (admin_id, a_datetime, content)
                VALUES (%s, %s, %s)
            """, (admin_id, datetime, content))
            print(datetime)
        connection.commit()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

#刪除公告
@app.route('/api/announce/<a_datetime>', methods=['DELETE'])
def delete_announcement(a_datetime):
    admin_id = request.args.get("admin_id")
    is_top = is_top = request.args.get("is_top") == "true"

    try:
        with connection.cursor() as cursor:
            if is_top:
                # 最高管理員可以不管 admin_id
                cursor.execute("""
                    DELETE FROM announcements 
                    WHERE a_datetime = %s
                """, (a_datetime,))
            else:
                # 一般管理員只能刪自己的
                cursor.execute("""
                    DELETE FROM announcements 
                    WHERE a_datetime = %s AND admin_id = %s
                """, (a_datetime, admin_id))

        connection.commit()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

#修改公告
@app.route("/api/announce/<a_datetime>", methods=["PUT"])
def update_announcement(a_datetime):
    data = request.get_json()
    content = data.get("content", "").strip()
    new_admin_id = data.get("admin_id")
    new_datetime = data.get("new_datetime")
    
    if not content or not new_admin_id or not new_datetime:
        return jsonify(success=False, message="缺少公告內容或管理者 ID")

    # 加上這一行：取得原作者 ID（主鍵的一部分）
    original_admin_id = data.get("original_admin_id")

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE announcements
                SET content = %s, admin_id = %s, a_datetime = %s
                WHERE a_datetime = %s AND admin_id = %s
            """, (content, new_admin_id, new_datetime, a_datetime, original_admin_id))
        connection.commit()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500
#=========================Announcement====================================#


#=========================feedback========================================#
@app.route('/feedback')
def feedback():
    username = session.get('username')
    admin_id = session.get('admin_id')

    if not username or not admin_id:
        return redirect(url_for('foradmin'))
    
    return render_template("feedback.html", username=username, admin_id=admin_id, is_top = is_top)

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    uid = data.get('uid')
    date = data.get('date')
    fb_type = data.get('type')
    time = data.get('time')
    feedback_content = data.get('feedback')

    if not all([uid, date, fb_type, time, feedback_content]):
        return jsonify(success=False, message='缺少必要欄位')

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO feedbacks (user_id, send_date, f_time, f_type, content, f_status)
                VALUES (%s, %s, %s, %s, %s, '未處理')
            """, (uid, date, time, fb_type, feedback_content))
        connection.commit()
        return jsonify(success=True, message='已收到回饋！')
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


@app.route('/api/feedback/all', methods=['GET'])
def get_all_feedback():
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    f.*, r.reply, r.reason, r.reply_date, r.reply_time,
                    COALESCE(a.user_name, CONCAT('ID:', f.admin_id)) AS admin_name
                FROM feedbacks f
                LEFT JOIN feedback_replies r
                    ON f.user_id = r.user_id AND f.send_date = r.send_date AND f.f_time = r.f_time
                LEFT JOIN admins a
                    ON f.admin_id = a.admin_id
                ORDER BY f.send_date DESC, f.f_time DESC
            """)
            results = cursor.fetchall()
        return jsonify(results)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


@app.route('/api/feedback/<uid>/<date>', methods=['POST'])
def update_feedback(uid, date):
    data = request.get_json()
    time = data.get("time")  # 前端要提供 f_time

    if not time:
        return jsonify(success=False, message="缺少時間欄位")

    try:
        with connection.cursor() as cursor:
            # 更新主表 status/admin_id
            if 'admin_id' in data and ('status' not in data or data['status'] == '處理中'):
                cursor.execute("""
                    UPDATE feedbacks
                    SET admin_id = %s, f_status = '處理中'
                    WHERE user_id = %s AND send_date = %s AND f_time = %s
                """, (data['admin_id'], uid, date, time))
                connection.commit()
                return jsonify(success=True, message="已認領")

            # 完整處理（已處理、不採納）
            cursor.execute("""
                UPDATE feedbacks
                SET f_status = %s, admin_id = %s
                WHERE user_id = %s AND send_date = %s AND f_time = %s
            """, (data.get('status'), data.get('admin_id'), uid, date, time))

            # 更新 reply 表（可插入或更新）
            cursor.execute("""
                SELECT user_id FROM feedback_replies
                WHERE user_id = %s AND send_date = %s AND f_time = %s
            """, (uid, date, time))
            exists = cursor.fetchone()

            if exists:
                cursor.execute("""
                    UPDATE feedback_replies
                    SET reply = %s, reason = %s, reply_date = %s, reply_time = %s
                    WHERE user_id = %s AND send_date = %s AND f_time = %s
                """, (
                    data.get("reply"),
                    data.get("reason"),
                    data.get("reply_date"),
                    data.get("reply_time"),
                    uid, date, time
                ))
            else:
                cursor.execute("""
                    INSERT INTO feedback_replies
                    (user_id, send_date, f_time, reply, reason, reply_date, reply_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    uid, date, time,
                    data.get("reply"),
                    data.get("reason"),
                    data.get("reply_date"),
                    data.get("reply_time")
                ))

        connection.commit()
        return jsonify(success=True, message="更新成功")
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

#=========================feedback========================================#

if __name__ == "__main__":
    app.run(port = 5050, host='0.0.0.0', debug=True)
