from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app, origins=["https://cgusqlpj.ddns.net:5000"])


NBA_SCORE_FILE = "nba_score.json"
BWF_SCORE_FILE = "bwf_score.json"


def read_nba_score():
    with open(NBA_SCORE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def write_nba_score(data):
    with open(NBA_SCORE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


def read_bwf_score():
    try:
        with open(BWF_SCORE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # 檔案不存在或內容錯誤時回傳空陣列
        return []


def write_bwf_score(data):
    with open(BWF_SCORE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_score")
def get_score():
    score = read_nba_score()
    return jsonify(score)


@app.route("/update_score", methods=["POST"])
def update_score():
    data = request.json
    score = read_nba_score()
    # 只在有傳入時才更新
    if "score1" in data:
        score["score1"] = data["score1"]
    if "score2" in data:
        score["score2"] = data["score2"]
    if "logo1" in data:
        score["logo1"] = data["logo1"]
    if "logo2" in data:
        score["logo2"] = data["logo2"]
    write_nba_score(score)
    return jsonify(score)


@app.route("/get_bwf_simple", methods=["GET"])
def get_bwf_simple():
    try:
        data = read_bwf_score()
        if not isinstance(data, list):
            data = []
    except Exception as e:
        print("get_bwf_simple error:", e)
        data = []
    return jsonify(data)


@app.route("/update_bwf_simple", methods=["POST"])
def update_bwf_simple():
    try:
        data = request.get_json(force=True)
        if not isinstance(data, list):
            return jsonify({"error": "Invalid data format"}), 400
        if not data:  # 空陣列不覆蓋
            return jsonify({"error": "Empty data, not saved"}), 400
        write_bwf_score(data)
        return jsonify({"status": "ok"})
    except Exception as e:
        import traceback

        print("update_bwf_simple error:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@app.route("/NBAscore")
def nba_score():
    return render_template("NBA_score.html")


@app.route("/BWFscore")
def bwf_score():
    return render_template("BWF_score.html")


@app.route("/BWF_official")
def bwf_official():
    return render_template("BWF_official.html")


@app.route("/NBA_official")
def nba_official():
    return render_template("NBA_official.html")


if __name__ == "__main__":
    context = (
        "/opt/lampp/etc/pem/fullchain.pem",
        "/opt/lampp/etc/pem/privkey.pem"
    )
    app.run(host="0.0.0.0", port=5001, debug=True, ssl_context=context)
