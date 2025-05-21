import json
import pymysql

# 連接 MySQL
conn = pymysql.connect(
    host='cgusqlpj.ddns.net',
    user='hanson0901',
    password='Hanson940901',
    database='final_project'
)
cursor = conn.cursor()

# 讀取 JSON
with open('C:\\Users\\cbes1\\Desktop\\SQL_final_projecet\\f1\\f1_drivers_full_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 插入資料
for driver in data:
    sql1 = """
        INSERT INTO F1_driver
        (number, team_name, pts)
        VALUES ( %s, %s, %s)
    """
    values = (
        int(driver.get('Number')),
        driver.get('Team'),
        driver.get('Country'),
        int(driver.get('Age')),
        int(driver.get('Points'))
    )
    cursor.execute(sql1, values)

conn.commit()
cursor.close()
conn.close()
