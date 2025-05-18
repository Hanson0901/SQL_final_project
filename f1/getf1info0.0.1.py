from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
driver.get('https://www.formula1.com/en/drivers')

time.sleep(5)  # 等待動態內容載入
soup = BeautifulSoup(driver.page_source, 'html.parser')

# 根據實際網頁結構調整選擇器
drivers = []
for card in soup.select('div[class*="border-t-double border-r-double rounded-tr-s"]'):
    rank = card.select_one('p[class*="f1-heading-black"]').text if card.select_one('p[class*="f1-heading-black"]') else 'N/A'
    #number = card.select_one('p[class*="f1-heading-black"]').text if card.select_one('p[class*="f1-heading-black"]') else 'N/A'
    for name_tag in card.select('div[class*="flex gap-xxs flex-col"]'):
        name = name_tag.select_one('p:nth-of-type(1)').text+' '+name_tag.select_one('p:nth-of-type(2)').text
    team = card.select_one('p[class="f1-heading tracking-normal text-fs-12px leading-tight normal-case font-normal non-italic f1-heading__body font-formulaOne text-greyDark"]').text if card.select_one('p[class*="f1-heading tracking-normal text-fs-12px leading-tight normal-case font-normal non-italic f1-heading__body font-formulaOne text-greyDark"]') else 'N/A'
    drivers.append({'姓名': name, '車隊': team, '名次': rank})

print(drivers)
driver.quit()
