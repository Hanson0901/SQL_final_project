from flask import Flask, request, jsonify, redirect, url_for, render_template, session
import json
import os
import pymysql
import pymysql.cursors
from datetime import datetime

app = Flask(__name__)
app.secret_key = "yuuuuuuuriz"

connection = pymysql.connect(
    host='localhost',
    # port = 3306,
    user='uuriglass',
    password='laby800322',
    database='test',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

#最高ADMIN
top_admin = [
        {
            "username" : "uuriglass",
            "password" : "ssalgiruu"
        }
]

is_top = False;

#==================================登入/註冊介面==============================#
@app.route('/')
def index():
    return render_template("login.html")

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
                session['is_top'] = is_top;

                return jsonify(success=True,
                                username=matched['user_name'],
                                admin_id=matched['admin_id'],
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
    return render_template("adminUI.html")



#=================================SQL=======================================#
@app.route("/sql")
def sql():
    return render_template("sql.html")

@app.route("/api/search")
def search():
    keyword = request.args.get("keyword", "").strip().lower()
    if not keyword:
        return jsonify(matches=[])

    try:
        results = []
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 1. 搜尋隊伍名稱
            cursor.execute("""
                SELECT team_id, team_name 
                FROM teams 
                WHERE LOWER(team_name) LIKE %s
            """, (f"%{keyword}%",))
            teams = cursor.fetchall()

            if not teams:
                return jsonify(matches=[])

            # 2. 抓對應 team_id（不要轉成字串）
            team_ids = [t['team_id'] for t in teams]
            format_strings = ','.join(['%s'] * len(team_ids))

            # 3. 撈比賽資料（team_a 或 team_b 其中一隊出現）
            sql = f"""
                SELECT m.*, 
                       ta.team_name AS team_a_name, 
                       tb.team_name AS team_b_name
                FROM matches_schedule m
                LEFT JOIN teams ta ON m.team_a = ta.team_id
                LEFT JOIN teams tb ON m.team_b = tb.team_id
                WHERE m.team_a IN ({format_strings}) OR m.team_b IN ({format_strings})
            """
            cursor.execute(sql, team_ids + team_ids)
            matches = cursor.fetchall()

            for m in matches:
                results.append({
                    "id": m["game_no"],
                    "match": f"{m['team_a_name']} vs {m['team_b_name']}",
                    "date": str(m["date"]),
                    "time": str(m["time"]),
                    "point": m["point"]
                })

        return jsonify(matches=results)

    except Exception as e:
        print("❌ 後端錯誤：", e)
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
                if not all(k in m for k in ("team_a", "team_b", "date", "time")):
                    continue

                # 取得隊伍名稱（當作 match_name 顯示用）
                cursor.execute("SELECT team_name FROM teams WHERE team_id = %s", (m["team_a"],))
                team_a_name = cursor.fetchone()
                cursor.execute("SELECT team_name FROM teams WHERE team_id = %s", (m["team_b"],))
                team_b_name = cursor.fetchone()

                if not team_a_name or not team_b_name:
                    continue

                match_name = f"{team_a_name['team_name']} vs {team_b_name['team_name']}"

                # 取得隊伍所屬的運動類型
                cursor.execute("SELECT sport_type FROM teams WHERE team_id = %s", (m["team_a"],))
                sport = cursor.fetchone()
                if not sport:
                    continue
                sport_type = sport["sport_type"]

                # 檢查是否有重複
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
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

    return jsonify(success=True, count=added)

@app.route("/api/match/<int:id>")
def get_match(id):
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT m.*, 
                       ta.team_name AS team_a_name,
                       tb.team_name AS team_b_name,
                       m.type AS sport_type
                FROM matches_schedule m
                LEFT JOIN teams ta ON m.team_a = ta.team_id
                LEFT JOIN teams tb ON m.team_b = tb.team_id
                WHERE m.game_no = %s
            """, (id,))
            match = cursor.fetchone()

        if match:
            match_data = {
                "id": match["game_no"],
                "match": f"{match['team_a_name']} vs {match['team_b_name']}",
                "team_a": match["team_a"],
                "team_b": match["team_b"],
                "sport_type": match["sport_type"],
                "date": str(match["date"]),
                "time": str(match["time"]),
                "point": match["point"]

            }
            return jsonify(success=True, match=match_data)

        return jsonify(success=False, message="找不到比賽"), 404

    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


@app.route("/api/teams")
def get_teams():
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT team_id, team_name, sport_type FROM teams")
            teams = cursor.fetchall()
        return jsonify(teams)
    except Exception as e:
        return jsonify([], 500)


@app.route("/api/edit/<int:id>", methods=["POST"])
def edit_match(id):
    data = request.json
    try:
        with connection.cursor() as cursor:
            # 檢查是否存在
            cursor.execute("SELECT * FROM matches_schedule WHERE game_no = %s", (id,))
            if not cursor.fetchone():
                return jsonify(success=False, message="找不到比賽"), 404

            cursor.execute("""
                UPDATE matches_schedule
                SET team_a = %s, team_b = %s, date = %s, time = %s, point = %s
                WHERE game_no = %s
            """, (
                data["team_a"], data["team_b"],
                data["date"], data["time"], data["point"],
                id
            ))

        connection.commit()
        return jsonify(success=True)

    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

@app.route("/api/delete/<int:id>", methods=["DELETE"])
def delete_match(id):
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM matches_schedule WHERE game_no = %s", (id,))
            if cursor.rowcount == 0:
                return jsonify(success=False, message="找不到比賽"), 404

        connection.commit()
        return jsonify(success=True)

    except Exception as e:
        print("❌ 刪除錯誤：", e)
        return jsonify(success=False, message=str(e)), 500

#=================================SQL=======================================#


@app.route('/update-summary')
def update_summary():
    return render_template("update_summary.html")


#=========================Announcement====================================#

@app.route('/announcements')
def announcements():
    username = session.get('username')
    admin_id = session.get('admin_id')

    if not username or not admin_id:
        return redirect(url_for('index'))
    
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
        return redirect(url_for('index'))
    
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
    app.run(port=5050, host='0.0.0.0', debug=True)
