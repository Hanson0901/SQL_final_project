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
import time
import re
# pip install selenium
# pip install beautifulsoup4
def get_cpbl_score(date):

    

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # 推薦用這個
    driver = webdriver.Chrome(options=chrome_options)
    #輸入年月日
    
    #url="C:/Users/cbes1/Desktop/MLB%20Scores_%20Scoreboard,%20Results%20and%20Highlights.mhtml"
    url="https://www.cpbl.com.tw/box"
    driver.get(url)
    time.sleep(1)  # 確保動態內容載入
    try:
        WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[id='Content']"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        all =soup.select("div[class='game_list'] ul")

        games = []

        for game in all:
            
            bag=''
            times=[]
            #game_info = game.select("div[class^='TeamMatchupLayerstyle__InlineWrapper-sc'] div[data-test-id='teamRecordWrapper']")
            #rhe_info = game.select("div[class^='GameInfoLayoutstyle__GameInfoWrapper-sc'] tbody tr")
            time_info_element = game.select("li[class^='item']")
            Date=soup.select_one("div[class='date']").text
            if Date!= datetime.now().strftime("%Y/%m/%d"):
                return []  # 如果日期不符合，返回空列表
            for times in time_info_element:
                img=[]
                teams=[]
                img_tag = times.select_one("div[class='team_name'] span")
                img_style = img_tag["style"] if img_tag and img_tag.has_attr("style") else ""
                img_url = ""
                if img_style:
                    # 解析 style 屬性中的 background-image url
                    match = re.search(r'url\(["\']?(.*?)["\']?\)', img_style)
                    if match:
                        img_url = match.group(1)
                img.append(f"https://www.cpbl.com.tw{img_url}")
                img_tag = times.select_one("div[class='team home'] div[class='team_name'] span")
                img_style = img_tag["style"] if img_tag and img_tag.has_attr("style") else ""
                img_url = ""
                if img_style:
                    # 解析 style 屬性中的 background-image url
                    match = re.search(r'url\(["\']?(.*?)["\']?\)', img_style)
                    if match:
                        img_url = match.group(1)
                img.append(f"https://www.cpbl.com.tw{img_url}")
                print(img_url)
                teams.append( times.select_one("div[class='team away'] div[class='team_name'] span").text)
                teams.append( times.select_one("div[class='team home'] div[class='team_name'] span").text)
                game_status_div = times.find('div', class_='tag game_status')
                if game_status_div and game_status_div.get_text(strip=True):  # 檢查存在且內容不為空
                    time_info = times.select_one("div[class='tag game_status'] span").text
                    rhe_url = times.find("a").get("href")
                    rhe_data = get_rhe_info(rhe_url)
                    games.append({
                    'Date': Date,
                    'time': time_info,
                    'img': img,
                    'teams': teams,
                    'rhe': rhe_data,
                    'bag':bag
                    })
                else:
                    time_info = times.select_one('div[class="time"]').text
                    time_info = times.select_one('div[class="time"]').text + times.select_one("div[class='tag game_note'] span").text if times.select_one("div[class='tag game_note'] span") else time_info
                    rhe_data = {
                       'away': {'R': "", 'H': "", 'E': ""},
                       'home': {'R': "", 'H': "", 'E': ""}
                    }
                    games.append({
                    'Date': Date,
                    'time': time_info,
                    'img': img,
                    'teams': teams,
                    'rhe': rhe_data,
                    'bag':bag
                    })
            
            
        print(games)
        return games

    except Exception as e:
        print(f"發生錯誤: {e}")
        return []
    finally:
        driver.quit()

        
def get_rhe_info(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # 推薦用這個
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(f"https://www.cpbl.com.tw{url}")
    try:
        WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='item ScoreBoard']")))
        soup2 = BeautifulSoup(driver.page_source, "html.parser")
        rhe_info = soup2.select("div[class='item ScoreBoard']")
        rhe_data = {}
        for item in rhe_info:
            data = {
                'away':{
                    'R': item.select_one("div[class='linescore fixed'] tr[class='away'] td:nth-of-type(1)").text,
                    'H': item.select_one("div[class='linescore fixed'] tr[class='away'] td:nth-of-type(2)").text,
                    'E': item.select_one("div[class='linescore fixed'] tr[class='away'] td:nth-of-type(3)").text
                    },
                'home': {
                    'R': item.select_one("div[class='linescore fixed'] tr[class='home'] td:nth-of-type(1)").text,
                    'H': item.select_one("div[class='linescore fixed'] tr[class='home'] td:nth-of-type(2)").text,
                    'E': item.select_one("div[class='linescore fixed'] tr[class='home'] td:nth-of-type(3)").text
                    }
                }
            rhe_data=data
            print(rhe_data)
    except Exception as e:
        print(f"發生錯誤1: {e}") 
        return []
    finally:
        driver.quit()
        return rhe_data