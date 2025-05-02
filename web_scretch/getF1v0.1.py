from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.get("https://eltaott.tv/channel/sports_program_detail#F1")

try:
    # 顯式等待直到 F1 賽事表格載入完成
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#programList tr"))
    )
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    # 精準定位 F1 賽事（包含兩層篩選）
    #all = soup.select('#programList')
    #for Date in all:
       # date=(Date.find('div.contbox.belongDate')).get('id')
    #print(date)
    f1_events = soup.select('#programList tr:has(td:nth-of-type(2):contains("F1"))')
    
    for event in f1_events:
        time = event.select_one('td:nth-of-type(1)').get_text(strip=True)
        title = event.select_one('td:nth-of-type(2)').get_text(strip=True)
        game = event.select_one('td:nth-of-type(3)').get_text(strip=True)
        platform = ''
        for span in event.select('td.channels span.channel'):
            img = span.find('img')
            if img and img.get('src') == 'https://piceltaott-elta.cdn.hinet.net/public/assets/images/channels/channel_105_icon.svg':
                platform=('體育2台')
            elif img and img.get('src') == 'https://piceltaott-elta.cdn.hinet.net/public/assets/images/channels/channel_544_icon.svg':
                platform=('體育max5台')
        print(f"{time} | {title} | {game} | {platform}")

except Exception as e:
    print("抓取失敗:", e)
finally:
    driver.quit()
