import undetected_chromedriver as uc  # type: ignore
import time

import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
type_fullname = {
                "MS": "MEN'S SINGLES",
                "MD": "MEN'S DOUBLES",
                "WS": "WOMEN'S SINGLES",
                "WD": "WOMEN'S DOUBLES",
                "XD": "MIXED DOUBLES"
            }


with open(r"Player_info\BWF\BWF_player_links.json", "r", encoding="utf-8") as f:
    player_links = json.load(f)

print(f"Total player links: {len(player_links)}")

options = uc.ChromeOptions()
# options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(options=options)

player_info = []
id = 0

for link in player_links:
    print(f"id : {id}")
    driver.get(link)

    wait = WebDriverWait(driver, 10)
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
    stat_panels = driver.find_elements(By.CSS_SELECTOR, ".col.stat-panel")
    age = ""
    hand = ""
    if len(stat_panels) >= 3:
        # 第一個是 AGE
        try:
            age_elem = stat_panels[0].find_element(By.CSS_SELECTOR, ".stat-value")
            age = age_elem.text.strip() if age_elem else ""
        except Exception:
            age = ""
        # 第三個是慣用手
        try:
            hand_elem = stat_panels[2].find_element(By.CSS_SELECTOR, ".stat-value")
            hand = hand_elem.text.strip() if hand_elem else ""
        except Exception:
            hand = ""
    else:
        age = ""
        hand = ""

    print(f"Age: {age}")
    print(f"Hand: {hand}")

    # 取得所有 playertop-rank 區塊
    rank_blocks = driver.find_elements(By.CSS_SELECTOR, ".playertop-rank")
    World_Rank = ""
    world_rank_title = ""
    World_Tour_Rank = ""
    tour_rank_title = ""

    # 處理 World Rank
    if len(rank_blocks) > 0:
        block = rank_blocks[0]
        try:
            # 新版格式
            rank_num_elem = block.find_element(By.CSS_SELECTOR, ".ranking-number")
            World_Rank = rank_num_elem.text.strip()
            try:
                world_rank_title_elem = block.find_element(By.CSS_SELECTOR, ".ranking-title")
                world_rank_title = world_rank_title_elem.text.strip()
            except Exception:
                world_rank_title = ""
        except Exception:
            # 舊版格式（多欄位，需對應下方類型）
            try:
                rows = block.find_elements(By.CSS_SELECTOR, "table tr")
                if len(rows) >= 2:
                    rank_tds = rows[0].find_elements(By.TAG_NAME, "td")
                    type_tds = rows[1].find_elements(By.TAG_NAME, "td")
                    min_rank = None
                    min_type_full = ""
                    min_type_short = ""
                    for i in range(min(len(rank_tds), len(type_tds))):
                        rank_val = rank_tds[i].text.strip()
                        type_val = type_tds[i].text.strip()
                        type_full = type_fullname.get(type_val, type_val)
                        if rank_val and type_val:
                            try:
                                rank_num = int(rank_val.replace(",", ""))
                                if (min_rank is None) or (rank_num < min_rank):
                                    min_rank = rank_num
                                    min_type_full = type_full
                                    min_type_short = type_val
                            except Exception:
                                pass
                    if min_rank is not None:
                        World_Rank = f"{min_rank}"
                        world_rank_title = min_type_full
                    else:
                        World_Rank = ""
                        world_rank_title = ""
                else:
                    World_Rank = ""
                    world_rank_title = ""
            except Exception:
                World_Rank = ""
                world_rank_title = ""

    print(f"World Rank: {World_Rank}")
    print(f"World Rank Title: {world_rank_title}")

    # 處理 World Tour Rank
    if len(rank_blocks) > 1:
        block = rank_blocks[1]
        try:
            # 新版格式
            rank_num_elem = block.find_element(By.CSS_SELECTOR, ".ranking-number")
            World_Tour_Rank = rank_num_elem.text.strip()
            try:
                tour_rank_title_elem = block.find_element(By.CSS_SELECTOR, ".ranking-title")
                tour_rank_title = tour_rank_title_elem.text.strip()
            except Exception:
                tour_rank_title = ""
        except Exception:
            # 舊版格式（多欄位）
            try:
                rows = block.find_elements(By.CSS_SELECTOR, "table tr")
                if len(rows) >= 2:
                    rank_tds = rows[0].find_elements(By.TAG_NAME, "td")
                    type_tds = rows[1].find_elements(By.TAG_NAME, "td")
                    min_rank = None
                    min_type_full = ""
                    min_type_short = ""
                    for i in range(min(len(rank_tds), len(type_tds))):
                        rank_val = rank_tds[i].text.strip()
                        type_val = type_tds[i].text.strip()
                        type_full = type_fullname.get(type_val, type_val)
                        if rank_val and type_val:
                            try:
                                rank_num = int(rank_val.replace(",", ""))
                                if (min_rank is None) or (rank_num < min_rank):
                                    min_rank = rank_num
                                    min_type_full = type_full
                                    min_type_short = type_val
                            except Exception:
                                pass
                    if min_rank is not None:
                        World_Tour_Rank = f"{min_rank}"
                        tour_rank_title = min_type_full
                    else:
                        World_Tour_Rank = ""
                        tour_rank_title = ""
                else:
                    World_Tour_Rank = ""
                    tour_rank_title = ""
            except Exception:
                World_Tour_Rank = ""
                tour_rank_title = ""

    print(f"World Tour Rank: {World_Tour_Rank}")
    print(f"World Tour Rank Title: {tour_rank_title}")

    # 抓取獎金 (Prize Money)
    try:
        prize_elem = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".prize-value"))
        )
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
    wait = WebDriverWait(driver, 20)
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
        point_elem = WebDriverWait(driver, 5).until(
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