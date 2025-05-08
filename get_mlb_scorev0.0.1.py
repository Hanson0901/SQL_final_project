from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import datetime
import os
# pip install selenium
# pip install beautifulsoup4

driver = webdriver.Chrome()
#輸入年月日

year = int(input("請輸入年份 (YYYY): "))
month = int(input("請輸入月份 (MM): "))
day = int(input("請輸入日期 (DD): "))
date=datetime.date(year,month,day)
print(date)

url=f"https://www.mlb.com/scores/{date}"
driver.get(url)

try:
    WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "div[class^='ScoresGamestyle__PaddingWrapper-sc']"))
    )
    soup = BeautifulSoup(driver.page_source, "html.parser")
    all =soup.select("div[class^='ScoresGamestyle__PaddingWrapper-sc']")
        
    os.makedirs('web_scretch/data', exist_ok=True)
    filename = f'web_scretch/data/mlb{date}.json'
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            first_char = f.read(1)
    else:
        first_char = ''

    file = open(filename, 'a', encoding='utf-8')

    if first_char != '[':
        file.write("[")
        file.seek(1)
    else:
    # 讓指針指向倒數第2個字（這裡你可能需要根據需求調整）
        file.seek(file.tell() - 1, 0)
        file.truncate()
        file.write(',\n')

    for game in all:
        teams=[]
        R=[]
        H=[]
        E=[]
        game_info = game.select("div[class^='TeamMatchupLayerstyle__InlineWrapper-sc'] div[data-test-id='teamRecordWrapper']")
        rhe_info = game.select("div[class^='GameInfoLayoutstyle__GameInfoWrapper-sc'] tbody tr")
        for team in game_info:
            a_tag=team.find('a', attrs={'data-team-name': True})
            team_name = a_tag['data-team-name']  # 直接取屬性值
            teams.append(team_name)
        for rhe in rhe_info:
            R.append(rhe.select_one('td:nth-of-type(1) div').text)
            H.append(rhe.select_one('td:nth-of-type(2) div').text)
            E.append(rhe.select_one('td:nth-of-type(3) div').text)
        print(teams[0],R[0],H[0],E[0])
        print(teams[1],R[1],H[1],E[1])
        json_data = {
                'date': str(date),
                'home_team': teams[0],
                'away_team': teams[1],
                'home_team_R': R[0],
                'away_team_R': R[1],
                'home_team_H': H[0],
                'away_team_H': H[1],
                'home_team_E': E[0],
                'away_team_E': E[1]
            }
        json.dump(json_data, file, ensure_ascii=False, indent=4)
        file.write(',\n')

    file.seek(file.tell() - 3, 0)  # Move the cursor to the second last position
    file.truncate()  # 刪掉至最後
    file.write(']') #補回或新增一個]，讓json檔案結束
    # Close the JSON array
    file.close()
    #close the json file
        
        
except Exception as e:
    print(f"發生錯誤: {e}") 
finally:
    driver.quit()