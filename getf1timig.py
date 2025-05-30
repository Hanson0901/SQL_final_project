from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import os
from fake_useragent import UserAgent



def get_timing(times):
    options = Options()

    # 設置完整 User-Agent
    user_agent = UserAgent().random
    options.add_argument(f"user-agent={user_agent}")

    # 其他反檢測設定
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)

# 執行 JavaScript 移除 webdriver 痕跡
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined})
        '''
    })
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    try:
        #driver.get(f"file:///home/cbes100070/Desktop/website_all/SQL_final_project/F1_website_store/F1_{times}.html")  # 使用本地文件URL
        driver.get("https://www.formula1.com/en/timing/f1-live-lite")
        time.sleep(5)  # 等待頁面加載
        try:
        
            iframe = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "sp_message_iframe_1149950"))
            )
            driver.switch_to.frame(iframe)
            
            # 等待並點擊同意按鈕
            accept_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(translate(., "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "accept all")]'))
            )
            accept_button.click()
            print("成功點擊 Accept All 按鈕")
            
            # 切換回主文件
            driver.switch_to.default_content()
        except Exception as e:
            print(f"Cookie處理失敗: {str(e)}")

            # 等待數據加載
        WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".w-full.grid"))
        )
        
        time.sleep(10)  # 等待數據加載
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        print(soup.prettify())  # 打印HTML內容以便調試
        team_colors = {
            'Red Bull Racing': '#1E41FF',
            'Ferrari': '#E10600',
            'Mercedes': '#6CD3BF',
            'McLaren': '#FF8700',
            'Aston Martin': '#229971',
            'Alpine': '#2293D1',
            'Williams': '#64C4FF',
            'Haas F1 Team': '#B6BABD',
            'Sauber': '#52E252',
            'Racing Bulls': '#6692FF',
            'RB': '#6692FF'  # 備用名稱
        }

        # 等待數據加載完成

        # 解析數據
        rows = soup.select('tr[class="grid grid-cols-[50px_auto_70px_50px_60px] rounded-md tablet:grid-cols-[50px_auto_90px_70px_90px] auto-cols-auto relative text-xs font-normal text-center py-5 even:bg-grey-90"]')
        data = []
        
        for row in rows:
            pos = row.select_one('td:nth-of-type(1)').text if row.select_one('td:nth-of-type(1)') else 'N/A'
            driver_tag = row.select_one('span[class="driverName font-bold"]')
            if driver_tag:
                driver_name = driver_tag.select_one('span[class="font-normal hidden tablet:inline"]').text + ' ' + driver_tag.select_one('span[class="uppercase"]').text
            else:
                driver_name = 'N/A'
            driver_team = row.select_one('span[class="text-grey-60 font-titillium text-13 ml-2.5 hidden desktop:inline-block"]').text if row.select_one('span[class="text-grey-60 font-titillium text-13 ml-2.5 hidden desktop:inline-block"]') else 'N/A'
            tyre_tag = row.select_one('td:nth-of-type(4)')
            for img in tyre_tag.find_all('img'):
                src = img['src']
                if 'hard' in src:
                    tyre = '硬胎'
                elif 'medium' in src:
                    tyre = '中胎'
                elif 'soft' in src:
                    tyre = '軟胎'
                else:
                    tyre = '未知'
            gap = row.select_one('span[class="inline-block bg-grey-80 rounded-2xl w-auto min-w-16 text-center py-1 px-2.5 mx-auto uppercase"]').text if row.select_one('span[class="inline-block bg-grey-80 rounded-2xl w-auto min-w-16 text-center py-1 px-2.5 mx-auto uppercase"]') else 'N/A'
            tyres_used = row.select_one('td:nth-of-type(5)').text if row.select_one('td:nth-of-type(5)') else 'N/A'
            team_color = team_colors.get(driver_team, '#000000')  # 預設黑色
            data.append({
                    "Position": pos,
                    "Driver": driver_name,
                    "Team": driver_team,
                    "TeamColor": team_color,
                    "Gap": gap,
                    "Tyre": tyre,
                    "Tyres_Used": tyres_used
                })

        df = pd.DataFrame(data)
        print(df)

    except Exception as e:
        print(f"爬取失敗: {str(e)}")
    finally:
        driver.quit()
        return df
