from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="william",
        password="Chang0928",
        database="final_project",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/action', methods=['GET'])
def action():
    conn = get_db_connection()
    uid = request.args.get('uid')
    username = request.args.get('username')
    if not uid or not username:
        return jsonify({'error': 'Missing uid or username'}), 400
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO users (user_id, user_name) VALUES (%s, %s)"
            cursor.execute(sql, (uid, username))
            conn.commit()
        return jsonify({'message': 'User saved successfully'})
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)