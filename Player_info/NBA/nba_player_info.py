from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json

options = webdriver.ChromeOptions()
# options.add_argument("--headless")
driver = webdriver.Chrome(options=options)


with open("Player_info/NBA/nba_team_links.json", "r", encoding="utf-8") as f:
    team_links = json.load(f)


for team_name, team_url in team_links:
    data = []
    print(f"Team: {team_name}, URL: {team_url}")
    driver.get(team_url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.find("table", class_="stats-table")
    player_info_list = []
    if table:
        rows = table.find_all("tr", class_="Bgc(table-hover):h")

        for row in rows:

            player_data = []

            for cell in row.find_all(["th", "td"]):
                player_data.append(cell.get_text(strip=True))
            if player_data:
                player_info_list.append(player_data)
                # print(len(player_data))  # 21
                # print(player_data[0])  # Player Name

                player_dict = {
                    "player": player_data[0],
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
                data.append(player_dict)

                output_filename = f"Player_info/NBA/json/{team_name}_player_info.json"
                with open(output_filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                    # print(f"Data saved to {output_filename}")
