import undetected_chromedriver as uc  # type: ignore
import time

import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

with open("Player_info\BWF\player_links.json", "r", encoding="utf-8") as f:
    player_links = json.load(f)

options = uc.ChromeOptions()
# options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(options=options)

player_info = []
id = 0

for link in player_links:

    driver.get(link)

    wait = WebDriverWait(driver, 5)
    # 抓取姓名2 (英文姓)
    try:
        name2_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".name-2"))
        )
        name2 = name2_elem.text.strip() if name2_elem else ""
    except Exception:
        name2 = ""
    print(f"Name2: {name2}")

    # 抓取姓名1 (英文名)
    try:
        name1_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".name-1"))
        )
        name1 = name1_elem.text.strip() if name1_elem else ""
    except Exception:
        name1 = ""
    print(f"Name1: {name1}")

    # 抓取國家名稱
    try:
        country_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".playertop-country span"))
        )
        country = country_elem.text.strip() if country_elem else ""
    except Exception:
        country = ""
    print(f"Country: {country}")
    # 抓取 AGE 和慣用手
    try:
        stat_panels = driver.find_elements(By.CSS_SELECTOR, ".col.stat-panel")
        age = ""
        hand = ""
        if len(stat_panels) >= 3:
            # 第一個是 AGE
            age_elem = stat_panels[0].find_element(By.CSS_SELECTOR, ".stat-value")
            age = age_elem.text.strip() if age_elem else ""
            # 第三個是慣用手
            hand_elem = stat_panels[2].find_element(By.CSS_SELECTOR, ".stat-value")
            hand = hand_elem.text.strip() if hand_elem else ""
    except Exception:
        age = ""
        hand = ""

    print(f"Age: {age}")
    print(f"Hand: {hand}")

    # 抓取世界排名
    try:
        rank_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ranking-number"))
        )
        World_Rank = rank_elem.text.strip() if rank_elem else ""
    except Exception:
        World_Rank = ""
    print(f"World Rank: {World_Rank}")

    # 抓取排名類型
    try:
        world_rank_title_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ranking-title"))
        )
        world_rank_title = (
            world_rank_title_elem.text.strip() if world_rank_title_elem else ""
        )
    except Exception:
        world_rank_title = ""
    print(f"World Rank Title: {world_rank_title}")
    # 抓取 World Tour Rank
    try:
        world_tour_rank_elem = driver.find_elements(By.CSS_SELECTOR, ".ranking-number")
        World_Tour_Rank = (
            world_tour_rank_elem[1].text.strip()
            if len(world_tour_rank_elem) > 1
            else ""
        )
    except Exception:
        World_Tour_Rank = ""
    print(f"World Tour Rank: {World_Tour_Rank}")
    # 抓取 World Tour Rank Title
    try:
        tour_rank_title_elem = driver.find_elements(By.CSS_SELECTOR, ".ranking-title")
        tour_rank_title = (
            tour_rank_title_elem[1].text.strip()
            if len(tour_rank_title_elem) > 1
            else ""
        )
    except Exception:
        tour_rank_title = ""
    print(f"World Tour Rank Title: {tour_rank_title}")

    # 抓取獎金 (Prize Money)
    try:
        prize_elem = driver.find_element(By.CSS_SELECTOR, ".prize-value")
        Prize_money = prize_elem.text.strip() if prize_elem else ""
    except Exception:
        Prize_money = ""
    print(f"Prize Money: {Prize_money}")

    # 切換到 RANKING 分頁
    try:
        ranking_tab = driver.find_element(By.LINK_TEXT, "RANKING")
        driver.execute_script("arguments[0].click();", ranking_tab)
        time.sleep(3)  # 等待分頁切換
    except Exception:
        pass

    # 切換到 RANKING 分頁後，需重新建立 wait 以確保等待新分頁內容載入
    wait = WebDriverWait(driver, 10)
    # 取得目前 RANKING 分頁的類別名稱
    try:
        point_title_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ranking-tab-category"))
        )
        point_title = point_title_elem.text.strip() if point_title_elem else ""
    except Exception:
        point_title = ""
    print(f"Point Title: {point_title}")

    # 抓取積分 (point)
    try:
        point_elem = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".details-value"))
        )
        point = point_elem.text.strip() if point_elem else ""
    except Exception:
        point = ""
    print(f"Point: {point}")

    player_info.append(
        {
            "id": id,
            # "name": name,
            "name1": name1,
            "name2": name2,
            "country": country,
            "age": age,
            "hand": hand,
            "world_rank": World_Rank,
            "world_tour_rank": World_Tour_Rank,
            "world_rank_title": world_rank_title,
            "world_tour_rank_title": tour_rank_title,
            "prize_money": Prize_money,
            "point_title": point_title,
            "point": point,
            # "link": link,
        }
    )
    id += 1

# 儲存資料到 JSON 檔案（若檔案已存在則覆寫）
with open("Player_info/player_info.json", "w", encoding="utf-8") as f:
    json.dump(player_info, f, ensure_ascii=False, indent=4)
# 關閉瀏覽器
driver.quit()
