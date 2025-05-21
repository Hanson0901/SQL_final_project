from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json

options = webdriver.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("--ignore-certificate-errors")
driver = webdriver.Chrome(options=options)


with open("Player_info/NBA/nba_team_links.json", "r", encoding="utf-8") as f:
    team_links = json.load(f)

i = 1
for team_name, team_url in team_links:

    player_info1 = []
    player_info2 = []
    print(f"Team: {team_name}, URL: {team_url}")
    driver.get(team_url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.find("table", class_="stats-table")

    if table:
        rows = table.find_all("tr", class_="Bgc(table-hover):h")

        for row in rows:

            player_data = []

            for cell in row.find_all(["th", "td"]):
                player_data.append(cell.get_text(strip=True))
            if player_data:
                # print(len(player_data))  # 21
                # print(player_data[0])  # Player Name

                player_dict = {
                    "name": player_data[0],
                    "games": player_data[1],
                    "minutes": player_data[2],
                    "fg_pct": player_data[5],
                    "ft_pct": player_data[8],
                    "three_pt_pct": player_data[11],
                    "points": player_data[12],
                    "off_reb": player_data[13],
                    "rebounds": player_data[15],
                    "assists": player_data[16],
                }
                player_info1.append(player_dict)

    team_stats_url = team_url.replace("stats", "roster")
    driver.get(team_stats_url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.find("table", class_="W(100%)")
    if table:
        tbody = table.find("tbody")
        rows = tbody.find_all("tr") if tbody else []

        for row in rows:

            player_data = []

            for cell in row.find_all(["th", "td"]):
                player_data.append(cell.get_text(strip=True))
            if player_data:
                # print(len(player_data))  # 21
                # print(player_data[0])  # Player Name

                player_dict = {
                    "no": player_data[0],
                    "name": player_data[1],
                    "position": player_data[2],
                    "height": player_data[3],
                    "weight_lbs": player_data[4],
                    "age": player_data[5],
                    "experience": player_data[6],
                    "nationality": player_data[7],
                    "college": player_data[8],
                }
                player_info2.append(player_dict)

    data = []
    # print(player_info2)
    # Combine player_info1 and player_info2
    for player1 in player_info1:
        for player2 in player_info2:
            # print(player1["player"], player2["player"])
            if player1["name"] == player2["name"]:
                combined_player_info = {**player1, **player2}
                data.append(combined_player_info)

    output_filename = f"Player_info/NBA/json/{i}_{team_name}_player_info.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        # print(f"Data saved to {output_filename}")

    i += 1
