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
matches_sql = """
INSERT INTO matches_schedule (type, team_a, team_b, date, time, point)
VALUES (%s, %s, %s, %s, %s, %s)
"""

matches_values = []
for item in schedule:
    # 跳過沒有比賽日期的項目（如 Pre-Season Testing）
    if not item["RaceDate"] or not item["Racetime"]:
        continue
    matches_values.append((
        2,          # type
        None,       # team_a
        None,       # team_b
        item["RaceDate"],
        item["Racetime"],
        None        # point
    ))

cursor.executemany(matches_sql, matches_values)
conn.commit()

insert_sql = """
INSERT INTO f1_match_info (game_no, match_name, match_type)
VALUES (%s, %s, %s)
"""

for item in schedule:
    # 跳過沒有比賽日期的項目
    if not item["RaceDate"] or not item["Racetime"]:
        continue

    # 查詢 matches_schedule 的 game_no
    select_sql = """
    SELECT game_no FROM matches_schedule
    WHERE date=%s AND time=%s
    LIMIT 1
    """
    cursor.execute(select_sql, (item["RaceDate"], item["Racetime"]))
    result = cursor.fetchone()
    if result:
        game_no = result[0]
        cursor.execute(insert_sql, (game_no, item["EventName"], item["RaceType"]))

conn.commit()
cursor.close()
conn.close()
print("資料已成功插入 matches_schedule 和 f1_match_info 表格。")