# app.py
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import pandas as pd
import random
from datetime import datetime
from getf1timig import get_timing
import datetime
from get_mlb_score import get_mlb_score
from get_cpbl_score import get_cpbl_score
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from fake_useragent import UserAgent

app = Flask(__name__)
CORS(app, origins=["https://cgusqlpj.ddns.net:5001"])


@app.route("/")
def index():
    return render_template("index.html")


def generate_live_data():
    teams = {
        'Red Bull': {'color': '#3671C6', 'tyre_color': {'Soft': '#DA292C', 'Medium': '#FFD700', 'Hard': '#FFFFFF'}},
        'Ferrari': {'color': '#E8000D', 'tyre_color': {'Soft': '#DA292C', 'Medium': '#FFD700', 'Hard': '#FFFFFF'}},
        'Mercedes': {'color': '#6CD3BF', 'tyre_color': {'Soft': '#DA292C', 'Medium': '#FFD700', 'Hard': '#FFFFFF'}},
        'McLaren': {'color': '#FF8700', 'tyre_color': {'Soft': '#DA292C', 'Medium': '#FFD700', 'Hard': '#FFFFFF'}}
    }
    
    data = []
    for team in teams:
        for i in range(2):
            lap_time = 92.5 + random.uniform(-1, 1)
            data.append({
                'position': len(data)+1,
                'driver': f"{team} Driver {i+1}",
                'team': team,
                'lap_time': f"{int(lap_time//60)}:{lap_time%60:06.3f}",
                'gap': f"+{random.uniform(0.1, 15.5):.3f}" if len(data) > 0 else "LEADER",
                'tyre': random.choice(['Soft', 'Medium', 'Hard']),
                'team_color': teams[team]['color'],
                'tyre_color': teams[team]['tyre_color'][random.choice(['Soft', 'Medium', 'Hard'])]
            })
    return pd.DataFrame(data)

@app.route('/F1Timing')
def f1_timing():
    return render_template('F1Timing.html')


times = 1
@app.route('/f1/get_live_data')
def get_live_data():
    global times
    print(times)
    df = get_timing(times)
    
    times += 1
    if times > 13:
        times = 1
    return jsonify({
        'last_updated': datetime.datetime.now().strftime("%H:%M:%S"),
        'data': df.to_dict(orient='records')
    })
n=1
@app.route('/MLB_living', methods=['GET', 'POST'])
def mlb_living():
    global n
    if request.method == 'POST':
        mlb_year = int(request.form['year'])
        mlb_month = int(request.form['month'])
        mlb_day = int(request.form['day'])
        mlb_date = datetime.date(mlb_year, mlb_month, mlb_day)
    else:
        mlb_date = datetime.date.today() - datetime.timedelta(days=0)
    
    mlb_date_str = mlb_date.strftime("%Y-%m-%d")
    #mlb_games = get_mlb_score(mlb_date_str)
    mlb_games = get_mlb_score(n)
    return render_template('MLB_living.html', games=mlb_games, date=mlb_date_str)

@app.route('/api/mlb_games')
def mlb_api_games():
    global n
    if n>10:
        n=1
    else:
        n += 1
    mlb_date_str = request.args.get('date', datetime.date.today().strftime("%Y-%m-%d"))
    #mlb_games = get_mlb_score(mlb_date_str)
    mlb_games = get_mlb_score(n)
    return jsonify(games=mlb_games)  # 直接返回序列化後的數據

@app.route('/CPBL_living', methods=['GET', 'POST'])
def cpbl_living():
    if request.method == 'POST':
        cpbl_year = int(request.form['year'])
        cpbl_month = int(request.form['month'])
        cpbl_day = int(request.form['day'])
        cpbl_date = datetime.date(cpbl_year, cpbl_month, cpbl_day)
    else:
        cpbl_date = datetime.date.today() - datetime.timedelta(days=0)
    
    cpbl_date_str = cpbl_date.strftime("%Y-%m-%d")
    games = get_cpbl_score(cpbl_date_str)
    return render_template('CPBL_living.html', games=games, date=cpbl_date_str)

# 新增 API 路由
@app.route('/api/cpbl_games')
def cpbl_api_games():
    cpbl_date_str = request.args.get('date', datetime.date.today().strftime("%Y-%m-%d"))
    cpbl_games = get_cpbl_score(cpbl_date_str)
    return jsonify(games=cpbl_games)  # 直接返回序列化後的數據

@app.route("/app/NBAscore", methods=["GET"])
def get_NBAscore():

    # url = "https://www.nba.com/games"

    # url = "http://127.0.0.1:5000/NBA_official"

    url = "https://cgusqlpj.ddns.net:5001/NBA_official"

    # url = "http://localhost:5001/NBA_official"

    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get(url)

    response = requests.get(url)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    # 預先等待所有需要的元素
    wait = WebDriverWait(driver, 2)
    score_elements = wait.until(
        EC.presence_of_all_elements_located(
            (
                By.CSS_SELECTOR,
                "p.MatchupCardScore_p__dfNvc.GameCardMatchup_matchupScoreCard__owb6w",
            )
        )
    )
    series_element = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "p.GameCardMatchup_gameSeriesText__zqvUF")
        )
    )
    team_rank_elements = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "span.MatchupCardTeamName_seed__Bb84k")
        )
    )

    # BeautifulSoup 部分
    # 使用 WebDriverWait 來等待隊伍 logo 區塊
    wrapper_elem = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.GameCardMatchup_wrapper__uUdW8")
        )
    )
    team_logo_divs = wrapper_elem.find_elements(By.CLASS_NAME, "TeamLogo_block__rSWmO")
    img1 = team_logo_divs[0].find_element(By.TAG_NAME, "img")
    img2 = team_logo_divs[1].find_element(By.TAG_NAME, "img")
    img1 = {"src": img1.get_attribute("src")}
    img2 = {"src": img2.get_attribute("src")}

    # 使用 WebDriverWait 來等待並獲取隊名元素
    team_name_elements = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "span.MatchupCardTeamName_teamName__9YaBA")
        )
    )
    Team_name1 = team_name_elements[0].text.strip()
    Team_name2 = team_name_elements[1].text.strip()

    # 使用預先等待的元素
    score1_elem = score_elements[0]
    score2_elem = score_elements[1]

    series_text = (
        series_element.find_element(By.TAG_NAME, "span").text.strip()
        if series_element.find_elements(By.TAG_NAME, "span")
        else "No series information"
    )

    game_status_elem = soup.find("p", class_="GameCardMatchupStatusText_gcsText__PcQUX")
    if game_status_elem:
        game_status_text = game_status_elem.text.strip()
    else:
        game_status_text = "No status"

    team_rank1_elem = team_rank_elements[0]
    team_rank2_elem = team_rank_elements[1]

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
        "game_status": game_status_text,
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
    return jsonify(data)


@app.route("/app/BWFscore", methods=["GET"])
def get_bwf_score():

    options = Options()

    # 設置完整 User-Agent
    user_agent = UserAgent().random
    options.add_argument(f"user-agent={user_agent}")
    # 設置隱藏瀏覽器的選項
    options.add_argument("--headless")

    # 其他反檢測設定
    options.add_argument("--disable-blink-features=AutomationControlled")
    # The following lines are only valid for Chrome, not Chrome, so they are removed:
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Firefox(options=options)

    # 執行 JavaScript 移除 webdriver 痕跡,
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    # url = "https://bwfbadminton.com/"

    url = "https://cgusqlpj.ddns.net:5001/BWF_official"

    # url = "http://localhost:5001/BWF_official"

    # options = uc.ChromeOptions()
    # # options.add_argument("--disable-blink-features=AutomationControlled")

    # driver = uc.Chrome(options=options)

    driver.get(url)
    if url != "https://cgusqlpj.ddns.net:5001/BWF_official":

        # 取得所有下一場賽事的連結（div.menu-next-tmt-outer 裡的 href）
        next_tmt_links = []
        try:
            next_tmt_divs = driver.find_elements(
                By.CSS_SELECTOR, "div.menu-next-tmt-outer a"
            )
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

    driver.quit()
    return jsonify(match_cards_array)


@app.route("/NBAscore")
def nba_score():
    return render_template("NBA_score.html")


@app.route("/BWFscore")
def bwf_score():
    return render_template("BWF_score.html")


@app.route("/BWF_official")
def bwf_official():
    return render_template("BWF_official.html")


@app.route("/NBA_official")
def nba_official():
    return render_template("NBA_official.html")


if __name__ == '__main__':
    context = (
        "/opt/lampp/etc/pem/fullchain.pem",
        "/opt/lampp/etc/pem/privkey.pem"
    )
    app.run(debug=True, port="5000", host='0.0.0.0', ssl_context=context)
