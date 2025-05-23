from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import render_template
from selenium.webdriver.firefox.options import Options
from fake_useragent import UserAgent
import json

app = Flask(__name__)
NBA_SCORE_FILE = "nba_score.json"
BWF_SCORE_FILE = "bwf_score.json"

def read_nba_score():
    with open(NBA_SCORE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def write_nba_score(data):
    with open(NBA_SCORE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)

def read_bwf_score():
    try:
        with open(BWF_SCORE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # 檔案不存在或內容錯誤時回傳空陣列
        return []
    
def write_bwf_score(data):
    with open(BWF_SCORE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/app/NBAscore", methods=["GET"])
def get_NBAscore():

    # url = "https://www.nba.com/games"

    # url = "http://127.0.0.1:5000/NBA_official"

    url = "http://cgusqlpj.ddns.net:5000/NBA_official"

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
    wrapper = soup.find("div", class_="GameCardMatchup_wrapper__uUdW8")

    if wrapper:
        team_logo_divs = wrapper.find_all("div", class_="TeamLogo_block__rSWmO")
    else:
        print("找不到 GameCardMatchup_wrapper__uUdW8")
    img1 = team_logo_divs[0].find("img")
    img2 = team_logo_divs[1].find("img")

    team_name = soup.find_all("span", class_="MatchupCardTeamName_teamName__9YaBA")
    Team_name1 = team_name[0].text.strip()
    Team_name2 = team_name[1].text.strip()

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


@app.route("/get_score")
def get_score():
    score = read_nba_score()
    return jsonify(score)


@app.route("/update_score", methods=["POST"])
def update_score():
    data = request.json
    score = read_nba_score()
    # 只在有傳入時才更新
    if "score1" in data:
        score["score1"] = data["score1"]
    if "score2" in data:
        score["score2"] = data["score2"]
    if "logo1" in data:
        score["logo1"] = data["logo1"]
    if "logo2" in data:
        score["logo2"] = data["logo2"]
    write_nba_score(score)
    return jsonify(score)


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
    # The following lines are only valid for Chrome, not Firefox, so they are removed:
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Firefox(options=options)

    # 執行 JavaScript 移除 webdriver 痕跡,
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    # url = "https://bwfbadminton.com/"

    url = "http://cgusqlpj.ddns.net:5000/BWF_official"

    # options = uc.FirefoxOptions()
    # # options.add_argument("--disable-blink-features=AutomationControlled")

    # driver = uc.Firefox(options=options)

    driver.get(url)

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

@app.route("/get_bwf_simple", methods=["GET"])
def get_bwf_simple():
    try:
        data = read_bwf_score()
        if not isinstance(data, list):
            data = []
    except Exception as e:
        print("get_bwf_simple error:", e)
        data = []
    return jsonify(data)

@app.route("/update_bwf_simple", methods=["POST"])
def update_bwf_simple():
    try:
        data = request.get_json(force=True)
        if not isinstance(data, list):
            return jsonify({"error": "Invalid data format"}), 400
        # 直接覆蓋
        write_bwf_score(data)
        return jsonify({"status": "ok"})
    except Exception as e:
        import traceback
        print("update_bwf_simple error:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
