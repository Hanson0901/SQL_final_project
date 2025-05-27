from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json

url = "https://bwfbadminton.com/players/"
options = webdriver.ChromeOptions()
# options.add_argument("--headless")
options.add_argument("--incognito")
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
with open(r"Player_info\BWF\player_info.json", "r") as f:

    data = json.load(f)

    # 合併 name1 和 name2 為 full_name
    for player in data[0:3]:
        next_page = True
        not_find = True
        find_name1 = player["name1"]
        find_name2 = player["name2"]
        country = player["country"]
        print(f"Searching for player: {find_name1}")
        search_box = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "input-3"))
        )
        search_box.click()
        search_box.send_keys("\ue009" + "a")  # Ctrl+A
        search_box.send_keys("\ue003")  # Delete
        search_box.send_keys(find_name1)
        time.sleep(3)  # wait for results to load

        while next_page and not_find:
            # 取得所有 class="popular-player-pair-wrap" 的元素
            soup = BeautifulSoup(driver.page_source, "html.parser")
            player_divs = soup.find_all("div", class_="popular-player-pair-wrap")
            print(
                f"Found {len(player_divs)} players with class 'popular-player-pair-wrap'"
            )
            # ...existing code...
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
                    print(f"Flag alt: {flag_alt}, Country: {country}")
                    name1_text = name1_span.text.strip() if name1_span else ""
                    name2_text = name2_span.text.strip() if name2_span else ""
                    if name1_text == find_name1 and name2_text == find_name2:
                        a_tag = div.find("a", href=True)
                        if a_tag:
                            link = a_tag["href"]
                            print(
                                f"找到對應的 player: {find_name1} {find_name2}\nlink: {link}"
                            )
                            all_link.append(link)
                            not_find = False
                        break

            # 取得目前頁碼
            page_nav = driver.find_element(
                By.CSS_SELECTOR, "div.table-pagination nav.pagination"
            )
            page_stats = page_nav.find_element(By.CLASS_NAME, "page-stats")
            page_text = page_stats.text.strip()  # 例如 "Page 10 of 10"
            current_page, total_page = map(
                int, page_text.replace("Page", "").replace("of", "").split()
            )
            print(f"目前頁碼：{current_page} / {total_page}")

            # 如果已經到最後一頁就 break
            if current_page == total_page:
                print("已到最後一頁，結束搜尋。")
                next_page = False

            # 點擊右箭頭按鈕
            next_btn = page_nav.find_elements(By.CLASS_NAME, "button")[
                2
            ]  # 第三個是右箭頭
            next_btn.click()
            time.sleep(2)  # 等待頁面載入

print("所有找到的 player links:")
for link in all_link:
    print(link)
