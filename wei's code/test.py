from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://www.nba.com/games"
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
driver.get(url)

response = requests.get(url)
response.encoding = "utf-8"
soup = BeautifulSoup(response.text, "html.parser")

wrapper = soup.find("div", class_="GameCardMatchup_wrapper__uUdW8")

if wrapper:
    team_logo_divs = wrapper.find_all("div", class_="TeamLogo_block__rSWmO")
    # for div in team_logo_divs:

    #     print(div)
else:
    print("找不到 GameCardMatchup_wrapper__uUdW8")
img1 = team_logo_divs[0].find("img")
img2 = team_logo_divs[1].find("img")
# print(img1)


team_name = soup.find_all("span", class_="MatchupCardTeamName_teamName__9YaBA")
# print(team_name)
Team_name1 = team_name[0].text.strip()
Team_name2 = team_name[1].text.strip()
# print(Team_name1, Team_name2)

score1_elem = WebDriverWait(driver, 2).until(
    EC.presence_of_all_elements_located(
        (
            By.CSS_SELECTOR,
            "p.MatchupCardScore_p__dfNvc.GameCardMatchup_matchupScoreCard__owb6w",
        )
    )
)[0]
score2_elem = WebDriverWait(driver, 2).until(
    EC.presence_of_all_elements_located(
        (
            By.CSS_SELECTOR,
            "p.MatchupCardScore_p__dfNvc.GameCardMatchup_matchupScoreCard__owb6w",
        )
    )
)[1]

series_elem = WebDriverWait(driver, 2).until(
    EC.presence_of_element_located(
        (By.CSS_SELECTOR, "p.GameCardMatchup_gameSeriesText__zqvUF")
    )
)

series_text = (
    series_elem.find_element(By.TAG_NAME, "span").text.strip()
    if series_elem.find_elements(By.TAG_NAME, "span")
    else "No series information"
)


team_rank1_elem = WebDriverWait(driver, 2).until(
    EC.presence_of_element_located(
        (By.CSS_SELECTOR, "span.MatchupCardTeamName_seed__Bb84k")
    )
)
team_rank2_elem = WebDriverWait(driver, 2).until(
    EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "span.MatchupCardTeamName_seed__Bb84k")
    )
)[1]

Team_rank1 = team_rank1_elem.text.strip()
Team_rank2 = team_rank2_elem.text.strip()

playoff_round_elem = soup.find(
    "p", class_="GameCardMatchup_gamePlayoffRoundText__Sy2Tn"
)
if playoff_round_elem:
    playoff_round_text = playoff_round_elem.find("span").text.strip()
    game_number_elem = playoff_round_elem.find(
        "span", class_="GameCardPlayoffRoundText_seriesGameNumberWithDot__aRVj_"
    )
    game_number_text = (
        game_number_elem.text.strip() if game_number_elem else "No game number"
    )
else:
    playoff_round_text = "No playoff round information"
    game_number_text = "No game number"

data = {
    "home_team": Team_name1,
    "away_team": Team_name2,
    "home_score": score1_elem.text.strip(),
    "away_score": score2_elem.text.strip(),
    "home_flag": img1["src"] if img1 else "",
    "away_flag": img2["src"] if img2 else "",
    "series": series_text,
    "home_team_rank": Team_rank1,
    "away_team_rank": Team_rank2,
    "playoff_round": playoff_round_text,
    "game_number": game_number_text,
}
print(data)

driver.quit()
