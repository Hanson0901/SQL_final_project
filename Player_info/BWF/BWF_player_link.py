from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json

url = "https://bwfbadminton.com/players/"
options = webdriver.ChromeOptions()
# options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

driver.get(url)
WebDriverWait(driver, 2).until(
    EC.presence_of_element_located((By.CLASS_NAME, "popular-player-pair-wrap"))
)
try:
    allow_btn = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable(
            (By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
        )
    )
    allow_btn.click()
except Exception as e:
    print("Cookie consent button not found or already accepted.")

soup = BeautifulSoup(driver.page_source, "html.parser")
player_list = []
for div in soup.find_all("div", class_="popular-player-pair-wrap"):
    for a in div.find_all("a", href=True):
        player_list.append(a["href"])

        with open("player_links.json", "w", encoding="utf-8") as f:
            json.dump(player_list, f, ensure_ascii=False, indent=2)
