from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd



def get_timing():
    options = Options()
    options.add_argument("--headless")  # 無頭模式
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1200")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get("C:/Users/cbes1/Desktop/F1%20-%20The%20Official%20Home%20of%20Formula%201%C2%AE%20Racing.mhtml")
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # 等待數據加載完成
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".w-full.grid"))
        )
        
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
            data.append({
                    "Position": pos,
                    "Driver": driver_name,
                    "Team": driver_team,
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
