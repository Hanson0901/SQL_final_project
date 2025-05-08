from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import json
import datetime
import os
# pip install selenium
# pip install beautifulsoup4
def get_mlb_score(date):

    



    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    #輸入年月日
    

    url=f"https://www.mlb.com/scores/{date}"
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[class^='ScoresCollectionGridstyle__GridElementWrapper-sc']"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        all =soup.select("div[class^='ScoresCollectionGridstyle__GridElementWrapper-sc']")
        

        games = []

        for game in all:
            teams=[]
            img=[]
            R=[]
            H=[]
            E=[]
            game_info = game.select("div[class^='TeamMatchupLayerstyle__InlineWrapper-sc'] div[data-test-id='teamRecordWrapper']")
            rhe_info = game.select("div[class^='GameInfoLayoutstyle__GameInfoWrapper-sc'] tbody tr")
            time_info_element = game.select_one("div[class*='StatusLayerstyle__StatusLayerValue']")
            if(time_info_element.find("span")): #回傳不為空字串
                time_info = time_info_element.find("span").text
            else:
                time_info = time_info_element.text
            rhe_data = {
                'away': {'R': "", 'H': "", 'E': ""},
                'home': {'R': "", 'H': "", 'E': ""}
                }
            for team in game_info:
                a_tag=team.find('a', attrs={'data-team-name': True})
                team_name = a_tag['data-team-name']  # 直接取屬性值
                teams.append(team_name)
                img_src = f"https://www.mlbstatic.com/team-logos/team-cap-on-light/{a_tag['data-team-id']}.svg"
                img.append(img_src)

            for rhe in rhe_info:
                # 改用條件判斷抓取每個欄位
                R.append(rhe.select_one('td:nth-of-type(1) div').text if rhe.select_one('td:nth-of-type(1) div') else "")
                H.append(rhe.select_one('td:nth-of-type(2) div').text if rhe.select_one('td:nth-of-type(2) div') else "")
                E.append(rhe.select_one('td:nth-of-type(3) div').text if rhe.select_one('td:nth-of-type(3) div') else "")



            if len(teams) >= 2 and len(R) >= 2 and len(H) >= 2 and len(E) >= 2:
                    rhe_data = {
                        'away': {'R': R[0], 'H': H[0], 'E': E[0]},
                        'home': {'R': R[1], 'H': H[1], 'E': E[1]}
                    }
            games.append({
                'time': time_info,
                'img': img,
                'teams': teams,
                'rhe': rhe_data
                })
        print(games)
        return games

            
            
    except Exception as e:
        print(f"發生錯誤: {e}") 
        return []
    finally:
        driver.quit()