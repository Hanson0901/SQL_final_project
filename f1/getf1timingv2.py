import fastf1
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import json

chrome_options = Options()
chrome_options.add_argument('--headless')  # Uncomment if you want to run headless
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.formula1.com/en/racing/2025")
WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".f1-container.container"))
)
soup = BeautifulSoup(driver.page_source, 'html.parser')
GP=[]
gp= soup.find_all('p', class_='f1-heading tracking-normal text-fs-18px leading-tight normal-case font-bold non-italic f1-heading__body font-formulaOne overflow-hidden')
for p in gp:
    print(p.text.strip())
    GP.append(p.text.strip())

# 啟用快取（需先建立 cache_dir 目錄）
fastf1.Cache.enable_cache('f1\\f1_cache')
points={
    1: 25,
    2: 18,
    3: 15,
    4: 12,
    5: 10,
    6: 8,
    7: 6,
    8: 4,
    9: 2,
    10: 1
}
def get_f1_live_timing():
    
    schedule = fastf1.get_event_schedule(2025)
    schedule['Session5Date'] = pd.to_datetime(schedule['Session5Date'], utc=True)
    schedule['RaceDate'] = schedule['Session5Date'].dt.strftime('%Y-%m-%d')    # 只選取比賽名稱與正賽時間
    schedule['Racetime'] = schedule['Session5Date'].dt.strftime('%H:%M')  # 只選取正賽時間
    races = schedule[['EventName', 'Country', 'Location', 'RaceDate','Racetime', 'Session5']]
    races = races.rename(columns={'Session5': 'RaceType'})
    
    with open('f1\\f1_schedule.json', 'w', encoding='utf-8') as f:
        races.to_json(f, orient='records', force_ascii=False, indent=4)
    print(races)
    '''
    try:
        # 獲取當前賽事 session（範例：2025年意大利正賽）
        for i in GP:
            session = fastf1.get_session(2025, i, 'R')  # 可以替換為 'Qualifying', '

        # 重點！必須先載入數據
            session.load(laps=True, telemetry=True, messages=True)  # 明確指定需加載的數據類型
        
        # 取得位置數據（此時數據已載入）
            pos_data = session.pos_data
        
        # 取得所有圈速資料
            laps = session.laps
        
        # 整理數據（完整範例）
            merged_data = []
            for driver in session.drivers:
                driver_info = session.get_driver(driver)
                team = driver_info.TeamName
                latest_lap = laps.pick_drivers(driver).iloc[-1]  # 取最新一圈
            
                merged_data.append({
                'Position': pos_data[driver]['Position'] if driver in pos_data and 'Position' in pos_data[driver] else session.drivers.index(driver) + 1,
                'Driver': getattr(driver_info, 'FullName', driver),
                'DriverNumber': getattr(driver_info, 'Number', driver),
                'Team': team,
                #'LapTime': latest_lap['LapTime'] if 'LapTime' in latest_lap and not pd.isna(latest_lap['LapTime']) else "DNF"
                'points': int(points.get(session.drivers.index(driver) + 1) if session.drivers.index(driver) + 1 in points else 0),
                })
            print(f"成功獲取 {i} 的數據")
            print(pd.DataFrame(merged_data))
            with open(f'f1\\f1_live_timing.json', 'w', encoding='utf-8') as f:
                json.dump(merged_data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"數據獲取失敗: {str(e)}")
        return pd.DataFrame()
        '''

# 使用範例
df = get_f1_live_timing()
if not df.empty:
    print(df)
else:
    print("無可用數據")