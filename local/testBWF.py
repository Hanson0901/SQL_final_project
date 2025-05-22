from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc  # type: ignore
from bs4 import BeautifulSoup
import time


url = "https://bwfbadminton.com/"

options = uc.ChromeOptions()
# options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(options=options)

driver.get(url)

# 取得所有下一場賽事的連結（div.menu-next-tmt-outer 裡的 href）
next_tmt_links = []
try:
    next_tmt_divs = driver.find_elements(By.CSS_SELECTOR, "div.menu-next-tmt-outer a")
    for a in next_tmt_divs:
        href = a.get_attribute("href")
        if href:
            next_tmt_links.append(href)
except Exception as e:
    print("Error finding next tournament links:", e)

driver.get(href)


# 取得 div.tmt-live-link 裡的所有 a 標籤的 href
tmt_live_links = []
try:
    tmt_live_divs = driver.find_elements(By.CSS_SELECTOR, "div.tmt-live-link a")
    for a in tmt_live_divs:
        href = a.get_attribute("href")
        if href:
            tmt_live_links.append(href)
except Exception as e:
    print("Error finding tmt-live-link anchors:", e)

driver.get(href)

# 等待關閉按鈕出現並點擊
try:
    close_button = driver.find_element(By.CLASS_NAME, "close-button")
    close_button.click()
except Exception as e:
    print("Close button not found or not clickable:", e)

# 用 CSS_SELECTOR 並延長等待時間
match_cards_ul = WebDriverWait(driver, 1).until(
    EC.presence_of_element_located((By.CLASS_NAME, "result-match-cards"))
)

# Find all `li` elements within the `ul`
match_cards_li = match_cards_ul.find_elements(By.TAG_NAME, "li")

# Store the `li` elements in an array, including court information if available
match_cards_array = []
for li in match_cards_li:
    court_info = (
        li.find_element(By.CLASS_NAME, "round-court").text
        if li.find_elements(By.CLASS_NAME, "round-court")
        else "No court info"
    )
    flag_elements = li.find_elements(By.CSS_SELECTOR, ".flag img")
    flag = (
        [element.get_attribute("src") for element in flag_elements]
        if flag_elements
        else "No flag info"
    )
    flag_1 = flag[0] if flag else "No flag info"
    flag_2 = flag[1] if len(flag) > 1 else "No flag info"

    player_name_1 = (
        li.find_element(By.CSS_SELECTOR, ".player1").text.strip()
        if li.find_elements(By.CSS_SELECTOR, ".player1")
        else "player1 not found"
    )
    player_name_2 = (
        li.find_element(By.CSS_SELECTOR, ".player2").text.strip()
        if li.find_elements(By.CSS_SELECTOR, ".player2")
        else ""
    )
    player_name_3 = (
        li.find_element(By.CSS_SELECTOR, ".player3").text.strip()
        if li.find_elements(By.CSS_SELECTOR, ".player3")
        else "player3 not found"
    )
    player_name_4 = (
        li.find_element(By.CSS_SELECTOR, ".player4").text.strip()
        if li.find_elements(By.CSS_SELECTOR, ".player4")
        else ""
    )

    team_details = li.find_elements(By.CSS_SELECTOR, ".team-details-wrap-card")
    score1 = []
    score2 = []

    if len(team_details) > 0:
        scores_team1 = team_details[0].find_elements(By.CSS_SELECTOR, ".score span")
        score1 = [
            score.text for score in scores_team1[:3]
        ]  # Get up to 3 scores for team 1

    if len(team_details) > 1:
        scores_team2 = team_details[1].find_elements(By.CSS_SELECTOR, ".score span")
        score2 = [
            score.text for score in scores_team2[:3]
        ]  # Get up to 3 scores for team 2

    round_oop = li.find_elements(By.CSS_SELECTOR, ".round-oop")
    round_oop_text = round_oop[0].text if round_oop else "No round info"

    round_status = li.find_elements(By.CSS_SELECTOR, ".round-status")
    round_status_text = round_status[0].text if round_status else "No status info"
    game_time = (
        li.find_element(By.CSS_SELECTOR, ".time").text.strip()
        if li.find_elements(By.CSS_SELECTOR, ".time")
        else "No game time info"
    )
    animated_gif = li.find_elements(By.CSS_SELECTOR, ".animated-line img")
    animated_gif_src = (
        animated_gif[0].get_attribute("src") if animated_gif else "No animated gif"
    )

    match_cards_array.append(
        {
            "court": court_info,
            "flag1": flag_1,
            "flag2": flag_2,
            "player1": player_name_1,
            "player2": player_name_2,
            "player3": player_name_3,
            "player4": player_name_4,
            "score1": score1,
            "score2": score2,
            "round_oop": round_oop_text,
            "round_status": round_status_text,
            "game_time": game_time,
            "animated_gif": animated_gif_src,
        }
    )

for match in match_cards_array:
    print("Court:", match["court"])
    print("Flag1:", match["flag1"])
    print("Flag2:", match["flag2"])
    print("Player 1:", match["player1"])
    print("Player 2:", match["player2"])
    print("Player 3:", match["player3"])
    print("Player 4:", match["player4"])
    print("Score 1:", match["score1"])
    print("Score 2:", match["score2"])
    print("Round OOP:", match["round_oop"])
    print("Round Status:", match["round_status"])
    print("Game Time:", match["game_time"])
    print("Animated GIF:", match["animated_gif"][:10])
    print("-" * 20)
