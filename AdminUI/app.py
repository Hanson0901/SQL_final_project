from flask import Flask, request, jsonify, redirect, url_for, render_template, session
import json
import os

app = Flask(__name__)
app.secret_key = "yuuuuuuuriz"

# 管理員資料
ADMIN_PATH = 'AdminUI/user.json'
def load_admin_data():
    if not os.path.exists(ADMIN_PATH):
        return []
    with open(ADMIN_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_admin_data(data):
    with open(ADMIN_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.route('/')
def index():
    return render_template("login.html")

# 登入
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    users = load_admin_data()
    matched = next((u for u in users if u.get('username') == username and u.get('password') == password), None)

    if matched:
        session['username'] = username
        session['admin_id'] = matched['id']
        return jsonify(success=True)
    else:
        return jsonify(success=False)

# 註冊
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify(success=False, message='帳號和密碼不得為空')

    users = load_admin_data()
    if any(u.get('username') == username for u in users):
        return jsonify(success=False, message='帳號已存在')

    new_id = len(users) + 1
    users.append({'id': new_id, 'username': username, 'password': password})
    save_admin_data(users)

    return jsonify(success=True, message=f'註冊成功, 您的 ID 為 {new_id}, 使用者名稱為 {username}')

@app.route('/control_panel')
def dashboard():
    return render_template("adminUI.html")

@app.route('/announcements')
def announcements():
    username = session.get('username')
    admin_id = session.get('admin_id')

    if not username or not admin_id:
        return redirect(url_for('index'))
    
    return render_template("announcements.html", admin_id=admin_id, username=username)

@app.route('/feedback')
def feedback():
    username = session.get('username')
    admin_id = session.get('admin_id')

    if not username or not admin_id:
        return redirect(url_for('index'))
    
    return render_template("feedback.html", username=username, admin_id=admin_id)

@app.route('/update-summary')
def update_summary():
    return render_template("update_summary.html")

# 公告處理
ANNOUNCE_FILE = 'AdminUI/announcements.json'

def load_announcements():
    if not os.path.exists(ANNOUNCE_FILE):
        return []
    with open(ANNOUNCE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_announcements(data):
    with open(ANNOUNCE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.route('/api/announce', methods=['POST'])
def announce():
    data = request.get_json()
    content = data.get('content', '').strip()
    admin_id = int(data.get('admin_id'))
    datetime = data.get('datetime', '').strip()
    timestamp = data.get('timestamp')

    if not content or admin_id is None or not datetime:
        return jsonify(success=False, message="缺少必要欄位")

    announcements = load_announcements()
    announcements.append({
        "datetime": datetime,
        "admin_id": admin_id,
        "content": content,
        "timestamp": timestamp
    })
    save_announcements(announcements)
    return jsonify(success=True)

@app.route('/announcements.json')
def announcements_json():
    announcements = load_announcements()
    admins = load_admin_data()
    id_to_name = {admin['id']: admin['username'] for admin in admins}
    
    for a in announcements:
        admin_id = int(a.get("admin_id"))
        a["admin_name"] = id_to_name.get(admin_id, f"id:{admin_id}")
    
    return jsonify(announcements)

# 意見回饋處理
FEEDBACK_PATH = "AdminUI/feedback.json"

def load_feedback():
    if not os.path.exists(FEEDBACK_PATH):
        return {}
    with open(FEEDBACK_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_feedback(data):
    with open(FEEDBACK_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

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

    feedback_data = load_feedback()
    if uid not in feedback_data:
        feedback_data[uid] = {}

    feedback_data[uid][date] = {
        'type': fb_type,
        'time': time,
        'feedback': feedback_content,
        'status': '未處理'
    }
    save_feedback(feedback_data)
    return jsonify(success=True, message='已收到回饋！')

@app.route('/api/feedback/all', methods=['GET'])
def get_all_feedback():
    feedback_data = load_feedback()
    admins = load_admin_data()
    id_to_name = {admin['id']: admin['username'] for admin in admins}
    for uid, records in feedback_data.items():
        for date, fb in records.items():
            admin_id = fb.get("admin_id")
            if admin_id is not None:
                fb["admin_name"] = id_to_name.get(admin_id, f"id:{admin_id}")
    return jsonify(feedback_data)

@app.route('/api/feedback/<uid>/<date>', methods=['POST'])
def update_feedback(uid, date):
    data = request.get_json()
    feedback_data = load_feedback()

    if uid not in feedback_data or date not in feedback_data[uid]:
        return jsonify(success=False, message='找不到指定的回饋')

    fb = feedback_data[uid][date]

    if 'admin_id' in data and ('status' not in data or data['status'] == '處理中'):
        fb['admin_id'] = int(data['admin_id'])
        fb['status'] = '處理中'
        save_feedback(feedback_data)
        return jsonify(success=True, message='已認領')

    fb['status'] = data.get('status', fb['status'])
    fb['admin_id'] = data.get('admin_id', int(fb.get('admin_id')))
    fb['reply_date'] = data.get('reply_date', fb.get('reply_date', ''))
    fb['reply_time'] = data.get('reply_time', fb.get('reply_time', ''))
    fb['reason'] = data.get('reason', fb.get('reason', ''))

    if fb['status'] in ['已處理', '不採納']:
        fb['reply'] = fb['reason']
    elif 'reply' in fb:
        del fb['reply']

    save_feedback(feedback_data)
    return jsonify(success=True, message='資料已更新')

@app.route('/api/announce/<int:timestamp>', methods=['DELETE'])
def delete_announcement(timestamp):
    announcements = load_announcements()
    new_announcements = [a for a in announcements if a.get("timestamp") != timestamp]

    if len(new_announcements) == len(announcements):
        return jsonify(success=False, message="找不到對應公告"), 404

    save_announcements(new_announcements)
    return jsonify(success=True)

if __name__ == "__main__":
    app.run(port=5050, host='0.0.0.0', debug=True)
