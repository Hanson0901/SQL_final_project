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

def select_sport_type():
    
    sport_map = {
        '1': 'F1',
        '2': 'MLB',
        '3': 'NBA',
        '4': 'BWF',
        '5': '中華職棒'
    }
    
    while True:
        print("\n請選擇賽事類型：")
        print("1) F1 一級方程式賽車")
        print("2) MLB 美國職棒")
        print("3) NBA 美國職籃")
        print("4) BWF 羽球賽事")
        print("5) 中華職棒")
        
        choice = input("輸入數字 (1-5): ").strip()
        
        if choice in sport_map:
            return sport_map[choice]
        print("輸入錯誤，請輸入有效的數字選項！")

type = select_sport_type()

driver = webdriver.Chrome()
url = f"https://eltaott.tv/channel/sports_program_detail#{type}"
driver.get(url)

try:
    # 顯式等待直到 F1 賽事表格載入完成
    WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "#programList div.contbox.belongDate"))
    )
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#programList tr"))
    )
    
    soup = BeautifulSoup(driver.page_source, "html.parser")

    CHANNEL_MAP = {
        'channel_101_icon.svg': '體育1台',
        'channel_105_icon.svg': '體育2台',
        'channel_110_icon.svg': '體育3台',
        'channel_111_icon.svg': '體育4台',
        'channel_540_icon.svg': '體育max1台',
        'channel_541_icon.svg': '體育max2台',
        'channel_542_icon.svg': '體育max3台',
        'channel_543_icon.svg': '體育max4台',
        'channel_544_icon.svg': '體育max5台',
        'channel_546_icon.svg': '體育max6台',
        'channel_547_icon.svg': '體育max7台',
        'channel_548_icon.svg': '體育max8台'
    }

    #os.makedirs('web_scretch', exist_ok=True)
    os.makedirs('web_scretch/data', exist_ok=True)
    filename = f'web_scretch/data/event{type}.json'
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
    
    all = soup.select('#programList div.contbox.belongDate')
    print("檢查匯入的資料")

    for Date in all:

        date= Date.get('data-belong_date')
        if(date <str(datetime.date.today()) ):
            continue
        events = Date.select(f'tr:has(td:nth-of-type(2):-soup-contains("{type}"))')
    
        for event in events:
            time = event.select_one('td:nth-of-type(1)').get_text(strip=True)
            title = event.select_one('td:nth-of-type(2)').get_text(strip=True)
            game = event.select_one('td:nth-of-type(3)').get_text(strip=True)
            channel = ''
            for span in event.select('td.channels span.channel'):
                img = span.find('img')
                icon_name = img['src'].split('/')[-1]
                if icon_name in CHANNEL_MAP:
                    channel = CHANNEL_MAP[icon_name]
                    break

            print(f"{date} | {time} | {title} | {game} | {channel}")
            json_data = {
                'date': date,
                'time': time,
                'title': title,
                'game': game,
                'channel': channel
            }
            json.dump(json_data, file, ensure_ascii=False, indent=4)
            file.write(',\n')

    # 刪除最後一個逗號
    file.seek(file.tell() - 3, 0)  # Move the cursor to the second last position
    file.truncate()  # 刪掉至最後
    file.write(']') #補回或新增一個]，讓json檔案結束
    # Close the JSON array
    file.close()
    #close the json file
except Exception as e:
    print("抓取失敗:", e)
finally:
    driver.quit()
