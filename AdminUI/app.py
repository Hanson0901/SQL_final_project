from flask import Flask, request, jsonify, redirect, url_for, render_template
import json
import os

DATA_PATH = 'AdminUI/mock_data.json'

def load_data():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username == 'admin' and password == '1234':
        return jsonify(success=True)
    else:
        return jsonify(success=False)

@app.route('/control_panel')
def dashboard():
    return render_template("adminUI.html")

from flask import Flask, render_template

@app.route('/sql')
def sql_area():
    return render_template("sql.html")

@app.route('/announcements')
def announcements():
    return render_template("announcements.html")

@app.route('/feedback')
def feedback():
    return render_template("feedback.html")

@app.route('/update-summary')
def update_summary():
    return render_template("update_summary.html")

def load_data():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


#JS拿資料的區域 (給前端 JS 用的)
@app.route("/api/search")
def search():
    keyword = request.args.get("keyword", "").strip().lower()
    if not keyword:
        return jsonify(matches=[])
    db = load_data()
    results = [m for m in db if keyword in m["match"].lower()]
    return jsonify(matches=results)

@app.route("/api/add-many", methods=["POST"])
def add_many():
    data = request.json
    new_matches = data.get("matches", [])

    if not new_matches:
        return jsonify(success=False, message="沒有資料可新增"), 400

    db = load_data()
    added = 0

    for m in new_matches:
        if not all(k in m for k in ("id", "match", "date", "time")):
            continue
        if any(existing["id"] == m["id"] for existing in db):
            continue
        db.append(m)
        added += 1

    save_data(db)
    return jsonify(success=True, count=added)

@app.route("/api/match/<int:id>")
def get_match(id):
    db = load_data()
    match = next((m for m in db if m["id"] == id), None)
    if match:
        return jsonify(success=True, match=match)
    return jsonify(success=False, message="找不到比賽"), 404

@app.route("/api/edit/<int:id>", methods=["POST"])
def edit_match(id):
    data = request.json
    db = load_data()
    match = next((m for m in db if m["id"] == id), None)
    if not match:
        return jsonify(success=False, message="找不到比賽"), 404

    match.update({
        "match": data.get("match", match["match"]),
        "date": data.get("date", match["date"]),
        "time": data.get("time", match["time"])
    })

    save_data(db)
    return jsonify(success=True)

@app.route("/api/delete/<int:id>", methods=["DELETE"])
def delete_match(id):
    db = load_data()
    new_db = [m for m in db if m["id"] != id]
    if len(new_db) == len(db):
        return jsonify(success=False, message="找不到比賽"), 404

    save_data(new_db)
    return jsonify(success=True)


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
    author = data.get('author', '').strip()
    datetime = data.get('datetime', '').strip()
    timestamp = data.get('timestamp')

    if not content or not author or not datetime:
        return jsonify(success=False, message="缺少必要欄位")

    # 讀取舊資料並加入新公告
    announcements = load_announcements()
    announcements.append({
        "datetime": datetime,
        "author": author,
        "content": content,
        "timestamp" : timestamp
    })
    save_announcements(announcements)

    return jsonify(success=True)

@app.route('/announcements.json')
def announcements_json():
    return jsonify(load_announcements())


@app.route('/api/announce/<int:timestamp>', methods=['DELETE'])
def delete_announcement(timestamp):
    announcements = load_announcements()
    new_announcements = [a for a in announcements if a.get("timestamp") != timestamp]

    if len(new_announcements) == len(announcements):
        return jsonify(success=False, message="找不到對應公告"), 404

    save_announcements(new_announcements)
    return jsonify(success=True)

if __name__ == "__main__":
    app.run(port = 5050, host='0.0.0.0', debug=True)