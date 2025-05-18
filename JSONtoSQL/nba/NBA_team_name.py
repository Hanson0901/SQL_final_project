from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import json

# 初始化 webdriver
options = Options()
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
options.add_experimental_option("detach", True)
options.add_experimental_option('excludeSwitches', ['enable-logging']) #把多餘的log關掉
driver = webdriver.Chrome(options=options)

url = 'https://en.wikipedia.org/wiki/National_Basketball_Association'
driver.get(url)

table = driver.find_element(By.CSS_SELECTOR, 'table.wikitable.sortable.plainrowheaders.jquery-tablesorter')

rows = table.find_elements(By.CSS_SELECTOR, 'tbody > tr')

count = 1
teams = []
for row in rows:
    data = []
    cols = row.find_elements(By.CSS_SELECTOR, 'td')  # 資料欄位
    header = row.find_elements(By.CSS_SELECTOR, 'th')[-1]  # 有些資料放在 th 裡（例如球隊名）
    data = [cell.text.strip() for cell in cols]
    if data:  
        teams.append({
                'team_id' : count,
                'team_name' : header.text,
                'abbr' : "",
                'city' : data[0],
                'arena' : data[1]
            })
    count += 1


#建立 Franchise → Abbreviation 對照表
abbr_url = "https://en.wikipedia.org/wiki/Wikipedia:WikiProject_National_Basketball_Association/National_Basketball_Association_team_abbreviations"
res = requests.get(abbr_url)
soup = BeautifulSoup(res.text, 'html.parser')

# 找出第一張表格
table = soup.find('table', {'class': 'wikitable'})

abbr_map = {}

for row in table.find_all('tr')[1:]:  # 跳過標題列
    cells = row.find_all('td')
    if len(cells) >= 2:
        franchise = cells[0].text.strip()
        abbr = cells[1].text.strip()
        abbr_map[franchise[0:3]] = abbr

for team in teams:
    name = team['team_name']

    for franchise in abbr_map:
        if abbr_map[franchise].lower() in name.lower():
            
            team['abbr'] = franchise
            break
    else:
        team['abbr'] = 'N/A'

with open("teamname.json", "w+", encoding="utf-8") as f:
    json.dump(teams, f, ensure_ascii=False, indent=2)

print("Finish~")
driver.quit()