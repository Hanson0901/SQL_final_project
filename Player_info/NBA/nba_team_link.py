from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json

url = "https://tw.sports.yahoo.com/nba/players"
options = webdriver.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("--ignore-certificate-errors")
options.add_experimental_option(
    "excludeSwitches", ["enable-automation", "enable-logging"]
)
driver = webdriver.Chrome(options=options)

driver.get(url)

# 取得網頁原始碼並建立 BeautifulSoup 物件
soup = BeautifulSoup(driver.page_source, "html.parser")

# 找到主要容器
container = soup.find_all("div", class_="D(ib) W(48%) Bxz(bb) Va(t)")
# print(f"container: {len(container)}")

# 找到所有E的球隊名稱
all_py6px = container[0].select("div.Py\\(6px\\)")

E_teams = []
E_team_links = []
for div in all_py6px:
    team_name = div.text.strip()
    a_tag = div.find("a")
    if a_tag and a_tag.has_attr("href"):
        team_link = "https://tw.sports.yahoo.com" + a_tag["href"].replace(
            "/roster", "/stats"
        )
    else:
        team_link = None
    E_teams.append((team_name, team_link))

for team_name, team_link in E_teams:
    print(f"{team_name}, {team_link}")
print(f"E_teams: {len(E_teams)}")

# 找到所有W的球隊名稱
all_py6px = container[1].select("div.Py\\(6px\\)")

W_teams = []
W_team_links = []
for div in all_py6px:
    team_name = div.text.strip()
    a_tag = div.find("a")
    if a_tag and a_tag.has_attr("href"):
        team_link = "https://tw.sports.yahoo.com" + a_tag["href"].replace(
            "/roster", "/stats"
        )
    else:
        team_link = None
    W_teams.append((team_name, team_link))

for team_name, team_link in W_teams:
    print(f"{team_name}, {team_link}")
print(f"W_teams: {len(W_teams)}")

# 寫進json檔

with open("Player_info/NBA/nba_team_links.json", "w", encoding="utf-8") as f:
    json.dump(E_teams + W_teams, f, ensure_ascii=False, indent=4)
print("Data saved to nba_team_links.json")


driver.quit()
