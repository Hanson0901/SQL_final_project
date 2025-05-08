# app.py
from flask import Flask, render_template, request, jsonify  # 新增 jsonify
import datetime
from get_mlb_score import get_mlb_score

app = Flask(__name__)

@app.route('/finalpj', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        year = int(request.form['year'])
        month = int(request.form['month'])
        day = int(request.form['day'])
        date = datetime.date(year, month, day)
    else:
        date = datetime.date.today() - datetime.timedelta(days=1)
    
    date_str = date.strftime("%Y-%m-%d")
    games = get_mlb_score(date_str)
    return render_template('index.html', games=games, date=date_str)

# 新增 API 路由
@app.route('/api/mlb_games')
def api_games():
    date_str = request.args.get('date', datetime.date.today().strftime("%Y-%m-%d"))
    games = get_mlb_score(date_str)
    return jsonify(games=games)  # 直接返回序列化後的數據


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
