<!-- Improved compatibility of 回到最上面 link: See: https://github.com/Hanson0901/SQL_final_project/pull/73 -->
<a id="readme-top"></a>
<!--
*** Thanks for checking out the SQL_final_project. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![Unlicense License][license-shield]][license-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/Hanson0901/SQL_final_project">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">CGU_SQL_team1_final_project</h3>

  <p align="center">
    屌到爆炸的資料庫專題!
    <br />
    <a href="https://github.com/Hanson0901/SQL_final_project"><strong>查看所有檔案»</strong></a>
    <br />
    <br />
    <a href="https://github.com/Hanson0901/SQL_final_project/blob/main/messageImage_1746199525381.jpg">檢視分工</a>
    &middot;
    <a href="https://github.com/Hanson0901/SQL_final_project/issues/new?labels=bug&template=bug-report---.md">回報 Bug</a>
    &middot;
    <a href="https://github.com/Hanson0901/SQL_final_project/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>目錄</summary>
  <ol>
    <li>
      <a href="#about-the-project">關於專案</a>
      <ul>
        <li><a href="#built-with">使用工具</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">開始使用</a>
      <ul>
        <li><a href="#prerequisites">需要的插件</a></li>
        <li><a href="#installation">下載專案</a></li>
      </ul>
    </li>
    <li><a href="#usage">用法</a></li>
    <li><a href="#roadmap">專案目標</a></li>
    <li><a href="#contributing">貢獻</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">資料來源</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://cgusqlpj.ddns.net)

個專案是一套以 Line Bot 為主要互動介面的即時資料查詢與回覆系統，結合 Python、Flask、MySQL 資料庫與爬蟲技術，讓使用者可以透過 Line 直接查詢最新資料，並獲得自動化回應。專案架構與功能如下：

1. 使用者互動層（前端）

使用者透過 Line Bot 發送訊息，作為主要的互動介面。

部分功能可透過 HTML 頁面呈現資訊，提升資訊可讀性。

2. 中介層（後端伺服器）

以 Flask（Python Web 框架）作為伺服器主體，負責處理來自 Line Bot 或 HTML 頁面的請求。

內建爬蟲模組，能自動抓取網路上的最新資料，並即時更新資料庫。

使用 pymysql 或 Flask-MySQLdb 套件，實現與 MySQL 資料庫的連線與資料操作。

可選用 PHP 處理部分網頁或 API 功能。

透過 ngrok 將本地端 Flask 伺服器公開至網際網路，讓 Line Bot 能順利與伺服器溝通。

3. 資料儲存層（資料庫）

採用 XAMPP 架設 MySQL 資料庫，負責儲存所有查詢資料、用戶紀錄與爬蟲更新內容。

可利用 phpMyAdmin 進行資料庫與資料表的管理與維護。

4. 技術流程簡述

使用者在 Line 上輸入查詢指令。

Line Bot 將訊息傳送給 Flask 伺服器。

Flask 後端根據需求，調用爬蟲取得最新資料，或直接查詢 MySQL 資料庫。

查詢結果經由 Flask 處理後回傳至 Line Bot，再回覆給使用者。

所有資料皆儲存在 XAMPP 架設的 MySQL 資料庫中，確保資料一致性與可追溯性。

5. 特色與應用場景

結合即時通訊（Line）、自動化爬蟲與資料庫，適合用於即時資料查詢、資訊推播、個人化服務等應用。

架構彈性高，便於本地開發測試與後續雲端部署。

<p align="right">(<a href="#readme-top">回到最上面</a>)</p>



### Built With

使用以下工具完成此專案

* [![Flask][Flask]][Flask-url]
* [![beautifulsoup][beautifulsoup4]][beautifulsoup4-url]
* [![Linebot][Linebot]][Linebot-url]
* [![html5][html5]][html5-url]
* [![Xampp][Xampp]][xampp-url]
* [![pymysql][pymysql]][pymysql-url]
* [![GCP][GCP]][GCP-url]
* [![JQuery][JQuery.com]][JQuery-url]

<p align="right">(<a href="#readme-top">回到最上面</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

您需要下載或安裝的文件

### Prerequisites

需要安裝的python套件，請用以下指令在含有python變數的command-Line
* python
  ```sh
  pip install beautifulsoup4
  pip install Flask
  pip install pymysql
  pip isntall line-bot-sdk
  pip install selenium
  pip install 
  ```

### Installation

_Below is an example of how you can instruct your audience on installing and setting up your app. This template doesn't rely on any external dependencies or services._

1. Get a free domain  at [https://www.noip.com/]if you want your own(https://www.noip.com/)
2. Clone the repo
   ```sh
   git clone https://github.com/Hanson0901/SQL_final_project.git
   ```

3. Change git remote url to avoid accidental pushes to base project
   ```sh
   git remote set-url origin github_username/repo_name
   git remote -v # confirm the changes
   ```
4. install xampp at [https://www.apachefriends.org/zh_tw/download.html](https://www.apachefriends.org/zh_tw/download.html)
<p align="right">(<a href="#readme-top">回到最上面</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

完成前置步驟後，即可連入我們的GCP

<p align="right">(<a href="#readme-top">回到最上面</a>)</p>



<!-- ROADMAP -->
## Roadmap
- [ ] 第一階段
  - [x] 從網頁上爬蟲賽事資料
  - [x] 將資料轉為JSON
  - [ ] 建立更新日誌
  - [ ] 完成web UI設計與回傳後端
  - [ ] 額外功能
      - [ ] 查詢比分
      - [ ] 意見回饋
- [ ] 第二階段
  - [ ] Linebot設計與使用
  - [ ] 實現所有功能

請參閱未解決的問題以取得提議的功能[現有問題](https://github.com/Hanson0901/SQL_final_project/issues)的完整清單。

<p align="right">(<a href="#readme-top">回到最上面</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

此項專案由以下開發者完成。若您在名單內，您所做的任何貢獻都將受到**極大的感謝**。

如果您有任何建議可以讓這個專案變得更好，請 fork 此 repo 並建立一個 pull request。您也可以直接開啟一個帶有 "enhancement" 標籤的 issue。
別忘了給這個專案點個星星！再次感謝您的支持！

1. Fork 此專案
2. 建立您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m '新增一些 AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟一個 Pull Request

### Top contributors:

<a href="https://github.com/Hanson0901/SQL_final_project/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Hanson0901/SQL_final_project" alt="contrib.rocks image" />
</a>

<p align="right">(<a href="#readme-top">回到最上面</a>)</p>



<!-- LICENSE -->
## License
根據 Unlicense 授權條款分發。詳細資訊請參閱 `LICENSE.txt` 文件。

<p align="right">(<a href="#readme-top">回到最上面</a>)</p>



<!-- CONTACT -->
## Contact

長庚大學第一癡情-呂號稱 [@hao_chen_cgu_csie_2005.05.05](https://www.instagram.com/hao_chen_cgu_csie_2005.05.05?utm_source=ig_web_button_share_sheet&igsh=ZDNlZDc0MzIxNw==) - B1229012@cgu.edu.tw

Project Link: [https://github.com/Hanson0901/SQL_final_project](https://github.com/Hanson0901/SQL_final_projec)

<p align="right">(<a href="#readme-top">回到最上面</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

Use this space to list resources you find helpful and would like to give credit to. I've included a few of my favorites to kick things off!

* [Choose an Open Source License](https://choosealicense.com)
* [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
* [Malven's Flexbox Cheatsheet](https://flexbox.malven.co/)
* [Malven's Grid Cheatsheet](https://grid.malven.co/)
* [Img Shields](https://shields.io)
* [GitHub Pages](https://pages.github.com)
* [Font Awesome](https://fontawesome.com)
* [React Icons](https://react-icons.github.io/react-icons/search)

<p align="right">(<a href="#readme-top">回到最上面</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/Hanson0901/SQL_final_project?style=for-the-badge
[contributors-url]: https://img.shields.io/github/contributors/Hanson0901/SQL_final_project/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Hanson0901/SQL_final_project?style=for-the-badge
[forks-url]: https://github.com/Hanson0901/SQL_final_project/network/members
[stars-shield]: https://img.shields.io/github/stars/Hanson0901/SQL_final_project?style=for-the-badge
[stars-url]: https://github.com/Hanson0901/SQL_final_project/stargazers
[issues-shield]: https://img.shields.io/github/issues/Hanson0901/SQL_final_project?style=for-the-badge
[issues-url]: https://github.com/Hanson0901/SQL_final_project/issues
[license-shield]: https://img.shields.io/github/license/Hanson0901/SQL_final_project?style=for-the-badge
[license-url]: https://github.com/Hanson0901/SQL_final_project/blob/main/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/Hanson0901
[product-screenshot]: images/screenshot.png
[Flask]: https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=Flask&logoColor=FFFFFF
[Flask-url]: https://flask.palletsprojects.com/en/stable/
[beautifulsoup4]: https://img.shields.io/badge/BeautifulSoup-green?style=for-the-badge&logo=python
[beautifulsoup4-url]: https://pypi.org/project/beautifulsoup4/
[Linebot]: https://img.shields.io/badge/LineBot-FFFFFF?style=for-the-badge&logo=LINE&logoColor=00C300
[Linebot-url]: https://developers.line.biz/zh-hant/services/bot-designer/
[html5]: https://img.shields.io/badge/HTML-FFFFFF?style=for-the-badge&logo=html5&logoColor=E34F26
[html5-url]: https://www.w3.org/TR/2011/WD-html5-20110525/
[Xampp]: https://img.shields.io/badge/Xampp-FB7A24?style=for-the-badge&logo=xampp&logoColor=FFFFFF
[xampp-url]: https://www.apachefriends.org/zh_tw/index.html
[pymysql]: https://img.shields.io/badge/pymysql-4479A1?style=for-the-badge&logo=mysql&logoColor=FFFFFF
[pymysql-url]: https://github.com/PyMySQL/PyMySQL
[GCP]: https://img.shields.io/badge/Google%20Cloud%20Platform-4285F4?style=for-the-badge&logo=googlecloud&logoColor=FFFFFF
[GCP-url]: https://console.cloud.google.com/?hl=zh-tw
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 
