import json
import pymysql

connection = pymysql.connect(
    host='localhost',
    user='uuriglass',
    password='laby800322',
    database='nba',
    charset='utf8mb4'
)

TABLE = 'teams'
data_count = 5
value = ["%s"] * data_count


para = ", ".join(value) 
# print(para)


with open('teamname.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

try:
    with connection.cursor() as cursor:
        for item in data:
            sql = f"""
                    INSERT INTO {TABLE} 
                    (team_id, team, city, abbreviation, arena)
                    VALUES ({para})
                """
            cursor.execute(sql, (item['team_id'], item['team_name'], item['city'], item['abbr'], item['arena']))
    connection.commit()
    print("✅ Commit success!")
except Exception as e:
    print("❌ Commit error:", e)
finally:
    connection.close()
