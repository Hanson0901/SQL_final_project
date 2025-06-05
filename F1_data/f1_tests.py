import fastf1
from flask import Flask, jsonify
from flask_cors import CORS
import asyncio

app = Flask(__name__)
CORS(app)

fastf1.Cache.enable_cache('f1_cache')
live_data = {}

@app.route('/api/live')
def get_live_data():
    return jsonify(live_data)

async def live_timing_client():
    client = fastf1.livetiming.SocketClient()
    client.register(update_handler)
    await client.connect()

def update_handler(data):
    global live_data
    # 解析原始livetiming數據
    for entry in data:
        if 'Position' in entry:
            live_data['positions'] = entry['Position']
        elif 'CarData' in entry:
            live_data['telemetry'] = entry['CarData']
        elif 'SessionInfo' in entry:
            live_data['session'] = entry['SessionInfo']

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(live_timing_client())
    app.run(port=5000)
