# app.py
from flask import Flask, render_template, jsonify
import pandas as pd
import random
from datetime import datetime
from getf1timig import get_timing

app = Flask(__name__)

# 模擬F1即時數據生成
def generate_live_data():
    teams = {
        'Red Bull': {'color': '#3671C6', 'tyre_color': {'Soft': '#DA292C', 'Medium': '#FFD700', 'Hard': '#FFFFFF'}},
        'Ferrari': {'color': '#E8000D', 'tyre_color': {'Soft': '#DA292C', 'Medium': '#FFD700', 'Hard': '#FFFFFF'}},
        'Mercedes': {'color': '#6CD3BF', 'tyre_color': {'Soft': '#DA292C', 'Medium': '#FFD700', 'Hard': '#FFFFFF'}},
        'McLaren': {'color': '#FF8700', 'tyre_color': {'Soft': '#DA292C', 'Medium': '#FFD700', 'Hard': '#FFFFFF'}}
    }
    
    data = []
    for team in teams:
        for i in range(2):
            lap_time = 92.5 + random.uniform(-1, 1)
            data.append({
                'position': len(data)+1,
                'driver': f"{team} Driver {i+1}",
                'team': team,
                'lap_time': f"{int(lap_time//60)}:{lap_time%60:06.3f}",
                'gap': f"+{random.uniform(0.1, 15.5):.3f}" if len(data) > 0 else "LEADER",
                'tyre': random.choice(['Soft', 'Medium', 'Hard']),
                'team_color': teams[team]['color'],
                'tyre_color': teams[team]['tyre_color'][random.choice(['Soft', 'Medium', 'Hard'])]
            })
    return pd.DataFrame(data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_live_data')
def get_live_data():
    df = get_timing()
    return jsonify({
        'last_updated': datetime.now().strftime("%H:%M:%S"),
        'data': df.to_dict(orient='records')
    })

if __name__ == '__main__':
    app.run(debug=True)
