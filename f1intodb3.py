import pymysql
import json

with open('f1\\f1_schedule.json', 'r', encoding='utf-8') as f:
    schedule = json.load(f)
conn = pymysql.connect(
    host='cgusqlpj.ddns.net',
    user='hanson0901',
    password='Hanson940901',
    database='final_project'
)
cursor = conn.cursor()

cursor.execute("SELECT game_no FROM f1_match_info")
game_nos = [row[0] for row in cursor.fetchall()]

# 2. 準備要插入的 (game_no, platform_id) 組合
values = []
for game_no in game_nos:
    values.append((game_no, 2))
    values.append((game_no, 6))

# 3. 批次插入 match_platforms
insert_sql = """
INSERT IGNORE INTO match_platforms (game_no, platform_id)
VALUES (%s, %s)
"""
cursor.executemany(insert_sql, values)
conn.commit()
print("資料已成功插入 match_platforms 表格。")
cursor.close()
conn.close()