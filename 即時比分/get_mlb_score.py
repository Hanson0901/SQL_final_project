from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from markupsafe import Markup
import json
import datetime
import os
# pip install selenium
# pip install beautifulsoup4
def get_mlb_score(date):

    

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # 推薦用這個
    driver = webdriver.Chrome(options=chrome_options)
    #輸入年月日
    
    #url="C:/Users/cbes1/Desktop/MLB%20Scores_%20Scoreboard,%20Results%20and%20Highlights.mhtml"
    #date_obj = datetime.datetime.strptime(date, "%Y-%m-%d") - datetime.timedelta(days=1)
    #date = date_obj.strftime("%Y-%m-%d")
    url=f"file:///home/cbes100070/Desktop/website_all/SQL_final_project/MLB{date}.html"
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
            bag=[]
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
            bag_info = game.select("[class*='inningStatestyle__StyledInningWrapper-sc']")if game.select("[class*='inningStatestyle__StyledInningWrapper-sc']") else ""
            bag_html = ''.join(str(b) for b in bag_info)
            bag_html = Markup(bag_html)

            bag.append(bag_info)
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
                'rhe': rhe_data,
                'bag':bag_html
                })
        print(games)
        return games

            
            
    except Exception as e:
        print(f"發生錯誤: {e}") 
        return []
    finally:
        driver.quit()
'''def get_mlb_score(date):

    

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # 推薦用這個
    driver = webdriver.Chrome(options=chrome_options)
    #輸入年月日
    
    #url="C:/Users/cbes1/Desktop/MLB%20Scores_%20Scoreboard,%20Results%20and%20Highlights.mhtml"
    date_obj = datetime.datetime.strptime(date, "%Y-%m-%d") - datetime.timedelta(days=1)
    date = date_obj.strftime("%Y-%m-%d")
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
            bag=[]
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
            bag_info = game.select("[class*='inningStatestyle__StyledInningWrapper-sc']")if game.select("[class*='inningStatestyle__StyledInningWrapper-sc']") else ""
            bag_html = ''.join(str(b) for b in bag_info)
            bag_html = Markup(bag_html)

            bag.append(bag_info)
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
                'rhe': rhe_data,
                'bag':bag_html
                })
        print(games)
        return games

            
            
    except Exception as e:
        print(f"發生錯誤: {e}") 
        return []
    finally:
        driver.quit()'''