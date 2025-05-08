# app.py
from flask import Flask, render_template, request
import datetime
from get_mlb_score import get_mlb_score

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        year = int(request.form['year'])
        month = int(request.form['month'])
        day = int(request.form['day'])
        date = datetime.date(year, month, day)
    else:
        date = datetime.date.today()- datetime.timedelta(days=1)
    date_str = date.strftime("%Y-%m-%d")
    games = get_mlb_score(date_str)
    return render_template('index.html', games=games, date=date_str)

if __name__ == '__main__':
    app.run(debug=True)
