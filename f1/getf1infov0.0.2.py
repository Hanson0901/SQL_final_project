from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import json



options = Options()
options.add_argument('--headless')  # 無頭模式
driver = webdriver.Chrome(options=options)

def get_age(birth_str, format='%d/%m/%Y'):
    """
    birth_str: 出生日期字串，例如 '1999-11-13'
    format: 日期格式，預設為 '%Y-%m-%d'
    """
    birth_date = datetime.strptime(birth_str, format)
    today = datetime.today()
    # 計算年齡
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

def get_driver_details(driver_url):
    driver.get(driver_url)
    time.sleep(3)  # 確保動態內容載入
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # 解析關鍵資料
    data = {}
    name_tag= soup.select_one('h1[class="f1-heading tracking-normal text-fs-24px tablet:text-fs-42px leading-tight normal-case font-bold non-italic f1-heading__body font-formulaOne"]')
    if name_tag:
        data['Name'] = name_tag.text
    number_tag=soup.select_one('p[class="f1-heading tracking-normal text-fs-24px tablet:text-fs-42px leading-tight normal-case font-normal non-italic f1-heading__body font-formulaOne f1-utils-inline-image--loose text-greyDark"]')
    if number_tag:
        data['Number'] = number_tag.text
    team_tag=soup.select_one('dd:nth-of-type(1)[class="f1-text font-titillium tracking-normal font-normal non-italic normal-case leading-snug f1-text__body text-fs-17px max-laptop:mb-normal"]')
    if team_tag:
        data['Team'] = team_tag.text
    country_tag=soup.select_one('dd:nth-of-type(2)[class="f1-text font-titillium tracking-normal font-normal non-italic normal-case leading-snug f1-text__body text-fs-17px max-laptop:mb-normal"]')
    if country_tag:
        data['Country'] = country_tag.text
    age_tag=soup.select_one('dd:nth-of-type(9)[class="f1-text font-titillium tracking-normal font-normal non-italic normal-case leading-snug f1-text__body text-fs-17px max-laptop:mb-normal"]')
    if age_tag:
        data['Age'] = get_age(age_tag.text)

    '''sections = soup.select('dl[class="grid gap-x-normal gap-y-xs f1-grid grid-cols-1 tablet:grid-cols-2 items-baseline"]')
    for item in sections:
        key = item.select_one('.stat-key').text.strip()
        value = item.select_one('.stat-value').text.strip()
        data[key] = value
    
    # 特殊處理出生日期格式
    if 'Date of birth' in data:
        data['Date of birth'] = data['Date of birth'].replace('/', '-')
    
    # 獲取車手完整姓名
    name = soup.select_one('.driver-name').text.strip()
    data['Driver'] = name
    '''
    
    return data

# 主爬蟲流程
def f1_driver_scraper():
    base_url = 'https://www.formula1.com'
    driver.get(f"{base_url}/en/drivers")
    time.sleep(2)
    
    # 獲取所有車手個人頁面連結
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver_links = [base_url + a['href'] for a in soup.select('a[href^="/en/drivers/"]')]
    rank = []
    pts = []
    for rank_tag in soup.select('p[class*="f1-heading-black"]'):
        rank.append(rank_tag.text if rank_tag else 'N/A')
    for pts_tag in soup.select('p[class="f1-heading-wide font-formulaOneWide tracking-normal font-normal non-italic text-fs-18px leading-none normal-case"]'):
        pts.append(pts_tag.text if pts_tag else 'N/A')
    # 爬取每個車手頁面
    all_data = []

    for link in driver_links:
        try:
            print(f"Processing: {link}")
            driver_data = get_driver_details(link)
            all_data.append({'Rank': rank[driver_links.index(link)], **driver_data, 'Points': pts[driver_links.index(link)]})
        except Exception as e:
            print(f"Error processing {link}: {str(e)}")
    
    driver.quit()
    return all_data

# 執行爬蟲並保存結果
df = f1_driver_scraper()
data_frame = pd.DataFrame(df)
with open('f1_drivers_full_data.json', 'w', encoding='utf-8') as f:
    json.dump(df, f, ensure_ascii=False, indent=4)
print(data_frame)

