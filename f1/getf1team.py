from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
import json

base_url = "https://www.formula1.com"
teams_url = f"{base_url}/en/teams"

# 第一步：取得所有車隊的網址
options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)
driver.get(teams_url)

soup = BeautifulSoup(driver.page_source, 'html.parser')
team_links = []
for a in soup.select('a.group.focus-visible\\:outline-0'):
    href = a.get('href')
    if href and '/en/teams/' in href:
        full_url = base_url + href
        team_links.append(full_url)
        print(full_url)

# 第二步：爬取每個車隊的資料
def fetch_team_info(url):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    info = {}
    # Full Team Name
    full_team_name_tag = soup.find('dd', class_='f1-text font-titillium tracking-normal font-normal non-italic normal-case leading-snug f1-text__body text-fs-17px max-laptop:mb-normal')
    team_cheif_tags = soup.find_all('dd', class_='f1-text font-titillium tracking-normal font-normal non-italic normal-case leading-snug f1-text__body text-fs-17px max-laptop:mb-normal')
    info['Full Team Name'] = full_team_name_tag.text.strip() if full_team_name_tag else 'N/A'
    info['Team Chief'] = team_cheif_tags[2].text.strip() if len(team_cheif_tags) > 2 else None

    # Chassis
    chassis_label = soup.find('dt', string='Chassis')
    if chassis_label:
        chassis_value = chassis_label.find_next_sibling('dd').text.strip()
        info['Chassis'] = chassis_value
    else:
        info['Chassis'] = 'N/A'
    # Power Unit
    power_unit_label = soup.find('dt', string='Power Unit')
    if power_unit_label:
        power_unit_value = power_unit_label.find_next_sibling('dd').text.strip()
        info['Power Unit'] = power_unit_value
    else:
        info['Power Unit'] = 'N/A'
    entry = soup.find('dt', string='First Team Entry')
    if entry:
        info['First Team Entry'] = entry.find_next_sibling('dd').text.strip()
    else:
        info['First Team Entry'] = 'N/A'
    return info

# 執行爬取
all_teams_info = []
pts= soup.select('.f1-inner-wrapper.flex.flex-col.gap-xs')
p={}
for pt in pts:
    p[pts.index(pt)] = pt.find('p', class_='f1-heading-wide font-formulaOneWide tracking-normal font-normal non-italic text-fs-18px leading-none normal-case')
nk=soup.select('.f1-inner-wrapper.flex.flex-col.gap-xs')
for nickname in nk:
    p[nk.index(nickname)] = nickname.find('span', class_='f1-heading tracking-normal text-fs-20px tablet:text-fs-25px leading-tight normal-case font-bold non-italic f1-heading__body font-formulaOne')
for url in team_links:
    team_info = {}
    team_info['Rank'] = team_links.index(url) + 1
    team_info['Nickname'] = p[team_links.index(url)].text.strip()
    team_info.update(fetch_team_info(url))
    team_info['Team Points'] = p[team_links.index(url)].text.strip()
    #team_info['URL'] = url
    all_teams_info.append(team_info)

# 輸出結果
with open('f1_teams_info.json', 'w', encoding='utf-8') as f:
    json.dump(all_teams_info, f, ensure_ascii=False, indent=4)
print(pd.DataFrame(all_teams_info))
