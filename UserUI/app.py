from flask import Flask, render_template, request, jsonify
import os
import json

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/mix_search")
def mix_search():
    return render_template("mix_search.html")

@app.route('/result')
def result():
    query_type = request.args.get('type')
    keyword = request.args.get('keyword')
    return render_template('result.html', query_type=query_type, keyword=keyword)

@app.route("/search")
def search():
    return render_template("search.html")

@app.route("/recent_match")
def recent_match():
    return render_template("recent_match.html")


#讀取比賽清單json 和 儲存預約資料 以 timestamp為單位
MATCHES_PATH = 'UserUI/matches.json'
BOOKINGS_PATH = 'UserUI/bookings.json'

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.route('/api/matches')
def get_matches():
    return jsonify(load_json(MATCHES_PATH))


@app.route('/api/bookings/archive', methods=['POST'])
def archive_bookings():
    data = request.json  # 應該長這樣：{ timestamp: { date: [matches] } }
    archive = load_json(BOOKINGS_PATH)
    archive.update(data)
    save_json(BOOKINGS_PATH, archive)
    return jsonify({"status": "saved"}), 200

# ✅ 查詢某個 UID 的預約資料
@app.route('/api/bookings/user/<uid>', methods=['GET'])
def get_user_bookings(uid):
    archive = load_json(BOOKINGS_PATH)
    user_data = archive.get(uid, {})
    return jsonify(user_data)

# ✅ 儲存某個 UID 的預約資料（整包覆蓋）
@app.route('/api/bookings/user/<uid>', methods=['POST'])
def save_user_bookings(uid):
    user_data = request.json  # 格式：{ "2025-05-15": [...], "2025-05-22": [...] }~
    archive = load_json(BOOKINGS_PATH)
    archive[uid] = user_data  # 覆蓋該使用者資料
    save_json(BOOKINGS_PATH, archive)
    return jsonify({"status": "saved"}), 200

# ✅ 刪除某個 UID 的所有預約資料
@app.route('/api/bookings/user/<uid>', methods=['DELETE'])
def delete_user_bookings(uid):
    archive = load_json(BOOKINGS_PATH)
    if uid in archive:
        del archive[uid]
        save_json(BOOKINGS_PATH, archive)
        return jsonify({"status": "deleted"}), 200
    return jsonify({"error": "UID not found"}), 404

# ✅ 查看全部使用者的預約資料（開發用）
@app.route('/api/bookings/all', methods=['GET'])
def get_all_bookings():
    return jsonify(load_json(BOOKINGS_PATH))

if __name__ == "__main__":
    app.run(port = 5050, host='0.0.0.0', debug=True)
