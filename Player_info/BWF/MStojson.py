from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
def get_search_name(full_name):
    words = full_name.split()
    if len(words) == 3:
        # 三個詞，取前兩個詞
        return " ".join(words[:2])
    elif len(words) == 2:
        # 兩個詞，取第一個詞
        return words[0]
    else:
        # 其他情況，直接回傳
        return full_name
    
def Next_Page(driver):
    page_nav = driver.find_element(
        By.CSS_SELECTOR, "div.table-pagination nav.pagination"
    )
    page_stats = page_nav.find_element(By.CLASS_NAME, "page-stats")
    page_text = page_stats.text.strip()  # 例如 "Page 10 of 10"
    current_page, total_page = map(
        int, page_text.replace("Page", "").replace("of", "").split()
    )
    print(f"目前頁碼：{current_page+1} / {total_page}")

    # 如果已經到最後一頁就 break
    if current_page == total_page:
        print("已到最後一頁，結束搜尋。")
        next_page = False
        return next_page

    # 點擊右箭頭按鈕
    next_btn = page_nav.find_elements(By.CLASS_NAME, "button")[
        2
    ]  # 第三個是右箭頭
    next_btn.click()
    time.sleep(2)  # 等待頁面載入

    return True

def if_not_find(driver, index, team, player,org_name):
    not_find = True
    next_page = True
    full_name=player[f"player_{index}"]

    name = get_search_name(org_name)

    if name:
        country= player[f"team_{team}"]
        print(f"Searching for player: {name}")
        driver.execute_script("window.scrollTo(0, 0);")
        search_box = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "input-3"))
        )
        search_box.click()
        search_box.send_keys("\ue009" + "a")  # Ctrl+A
        search_box.send_keys("\ue003")  # Delete
        search_box.send_keys(name)
        time.sleep(3)  # wait for results to load

        
        

        while not_find and next_page:
            # 取得所有 class="popular-player-pair-wrap" 的元素
            soup = BeautifulSoup(driver.page_source, "html.parser")
            player_divs = soup.find_all("div", class_="popular-player-pair-wrap")
            # print(
            #     f"Found {len(player_divs)} players with class 'popular-player-pair-wrap'"
            # )
            for div in player_divs:
                name1_span = div.find("span", class_="name-1")
                name2_span = div.find("span", class_="name-2")
                # 檢查國旗 alt 屬性是否與 country 相同
                flag_div = div.find("div", class_="popular-player-flag")
                flag_img = flag_div.find("img") if flag_div else None
                flag_alt = (
                    flag_img["alt"].strip()
                    if flag_img and flag_img.has_attr("alt")
                    else ""
                )

                if flag_alt == country:

                    # print(f"Flag alt: {flag_alt}, Country: {country}")
                    name1_text = name1_span.text.strip() if name1_span else ""
                    name2_text = name2_span.text.strip() if name2_span else ""
                    find_full_name1 = f"{name2_text} {name1_text}".strip()
                    find_full_name2 = f"{name1_text} {name2_text}".strip()
                    
                    if  find_full_name1 == full_name or find_full_name2 == full_name:
                        a_tag = div.find("a", href=True)
                        if a_tag:
                            link = a_tag["href"]
                            # print(
                            #     f"找到對應的 player: {full_name}\nlink: {link}\n"
                            # )
                            all_link.append(link)
                            not_find = False
                            return not_find
                        break
            if next_page:
                next_page = Next_Page(driver)
    return not_find

url = "https://bwfbadminton.com/players/"
options = webdriver.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("--incognito")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)
driver.get(url)
try:
    # 嘗試等待並點擊 Cookie 彈窗的接受/關閉按鈕
    cookie_btn = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable(
            (By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
        )
    )
    cookie_btn.click()
    print("Cookie 彈窗已關閉")
except Exception as e:
    print("沒有找到 Cookie 彈窗或已自動關閉")



all_link = []
found_players = set()  # 新增這行
with open(r"Player_info\BWF\BWF_schedule.json", "r", encoding="utf-8") as f:

    data = json.load(f)

    #  teama
    for player in data:

        
        for index in range(1, 4):
            if index == 1 or index == 2:
                team = "a"
            else:
                team = "b"
            not_find = True
            name = player[f"player_{index}"]
            if name:
                if name in found_players:
                    print(f"⚠️ 已經找到過這名選手: {name}，跳過")
                    continue
                country= player[f"team_{team}"]
                print(f"Searching for player: {name}")
                driver.execute_script("window.scrollTo(0, 0);")
                search_box = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.ID, "input-3"))
                )
                search_box.click()
                search_box.send_keys("\ue009" + "a")  # Ctrl+A
                search_box.send_keys("\ue003")  # Delete
                search_box.send_keys(name)
                time.sleep(3)  # wait for results to load

                
                # 取得所有 class="popular-player-pair-wrap" 的元素
                soup = BeautifulSoup(driver.page_source, "html.parser")
                player_divs = soup.find_all("div", class_="popular-player-pair-wrap")
                # print(
                #     f"Found {len(player_divs)} players with class 'popular-player-pair-wrap'"
                # )
        
                for div in player_divs:
                    name1_span = div.find("span", class_="name-1")
                    name2_span = div.find("span", class_="name-2")
                    # 檢查國旗 alt 屬性是否與 country 相同
                    flag_div = div.find("div", class_="popular-player-flag")
                    flag_img = flag_div.find("img") if flag_div else None
                    flag_alt = (
                        flag_img["alt"].strip()
                        if flag_img and flag_img.has_attr("alt")
                        else ""
                    )
                    print(f"Flag alt: {flag_alt}, Country: {country}")
                    if flag_alt == country:

                        a_tag = div.find("a", href=True)
                        link = a_tag["href"]
                        print(f"✅找到對應的 player: {name}\n")
                        all_link.append(link)
                        not_find = False
                        break
                        
                        
                    
                if not_find:

                    not_find = if_not_find(driver, index, team, player, name)
                    if not_find:
                        name = get_search_name(name)
                        not_find = if_not_find(driver, index, team, player, name)
                        if not_find:
                            print(f"❌找不到對應的 player: {name}\n")
                            continue
                        else:
                            print(f"✅找到對應的 player: {name}\n")
                            found_players.add(name)
                    else:
                        print(f"✅找到對應的 player: {name}\n")
                        found_players.add(name)  # 新增這行
                else:
                    found_players.add(name)  # 新增這行



# print("所有找到的 player links:")
# for link in all_link:
#     print(link)

# 將所有連結寫入 JSON 檔案
with open(
    r"Player_info\BWF\BWF_player_links.json", "w", encoding="utf-8"
) as f:
    json.dump(all_link, f, ensure_ascii=False, indent=4)