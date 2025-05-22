const page = document.body.dataset.page;

if(page === "door"){
    
}else if (page === "search"){
    // ✅ 一載入就設定今天日期
    const today = new Date().toISOString().slice(0, 10);
    document.getElementById("date").value = today;

    const querySelect = document.getElementById("query-type");
    const sportTypeSelect = document.getElementById("sport-type");
    const keywordSelect = document.getElementById("keyword");
    const dateInput = document.getElementById("date");
    const resultDiv = document.getElementById("searchResult");

    // ✅ 頁面一載入就預設更新關鍵字選項
    window.addEventListener("DOMContentLoaded", () => {
        updateKeywordOptions();
    });

    querySelect.addEventListener("change", updateKeywordOptions);
    sportTypeSelect.addEventListener("change", updateKeywordOptions);

    // ✅ 載入關鍵字下拉選單
    async function updateKeywordOptions() {
        const type = querySelect.value;
        const sport_type = sportTypeSelect.value;

        if (!type || !sport_type) {
            keywordSelect.innerHTML = `<option value="">請先選擇運動與查詢方式</option>`;
            return;
        }
        console.log(sport_type);
        console.log(type);
        try {
            const res = await fetch(`/api/get_options?sport_type=${sport_type}&query_type=${type}`);
            const data = await res.json();

            console.log("👉 關鍵字選項：", data);

            keywordSelect.innerHTML = `<option value="">請選擇</option>`;
            data.forEach(item => {
                const opt = document.createElement("option");
                opt.value = item.id;
                opt.textContent = item.name;
                keywordSelect.appendChild(opt);
            });
        } catch (err) {
            console.error("❌ 載入選項失敗：", err);
            keywordSelect.innerHTML = `<option value="">❌ 載入失敗</option>`;
        }
    }

    // ✅ 查詢比賽
    document.getElementById("SearchBtn").addEventListener("click", async () => {
        const type = querySelect.value;
        const sport = sportTypeSelect.value;
        const keyword = keywordSelect.value;
        const date = dateInput?.value;

        let keywordText = keywordSelect.options[keywordSelect.selectedIndex]?.textContent || keyword;
        let teamText = "";

        // ✅ 查隊伍名稱
        if (type === "team") {
            try {
                const res = await fetch(`/api/get_team_name?team_id=${keyword}`);
                const data = await res.json();
                if (data.team_name) keywordText = data.team_name;
            } catch (err) {
                console.warn("⚠️ 查詢隊伍名稱失敗", err);
            }
        }

        // ✅ 查球員所屬隊伍
        else if (type === "player") {
            try {
                const res = await fetch(`/api/get_team_name_by_player?sport=${sport}&player_id=${keyword}`);
                const data = await res.json();
                if (data.team_name) {
                    teamText = data.team_name + " ";
                }
            } catch (err) {
                console.warn("⚠️ 撈球員隊伍名失敗：", err);
            }
        }

        const typemap = {
            "team": "隊伍",
            "player": "隊員"
        };

        const sportmap = {
            1: "NBA",
            2: "F1",
            3: "MLB",
            4: "CPBL",
            5: "BWF"
        };

        if (!type || !sport || !keyword || !keywordText) {
            alert("❗ 請選擇運動種類、查詢方式與關鍵字");
            return;
        }

        const params = new URLSearchParams({
            sport,
            query_type: type,
            keyword,
            date
        });

        try {
            const res = await fetch(`/api/search_matches?${params}`);
            const data = await res.json();

            resultDiv.innerHTML = "";

            if (!data || !data.matches || data.matches.length === 0) {
                resultDiv.innerHTML = "<p>❌ 查無比賽資料</p>";
                return;
            }

            console.log("🏷️ 隊伍名：", teamText);

            if(type === "team"){
                resultDiv.innerHTML = `
                    <p>🔎以「<strong>${sportmap[sport]}</strong> - <strong>${keywordText}</strong>」<br>查詢 ${date} 起的比賽</p>
                    <p>✅找到 ${data.matches.length} 筆比賽：</p>
                `;
            }else if(type === "palyer"){
                resultDiv.innerHTML = `
                    <p>🔎以「<strong>${sportmap[sport]}</strong> - <strong>${teamText}</strong>的${typemap[type]} <strong>${keywordText}</strong>」<br>查詢 ${date} 起的比賽</p>
                    <p>✅找到 ${data.matches.length} 筆比賽：</p>
                `;
            }

            data.matches.forEach(m => {
                const formattedDate = new Date(m.date).toISOString().slice(0, 10);
                resultDiv.innerHTML += `
                    <div>
                        <strong>${m.team_a_name} vs ${m.team_b_name}</strong><br>
                        📅 ${formattedDate} 🕒 ${m.time}<br>
                        🎯 比分：${m.point ?? "尚未公布"}<br><br>
                    </div>
                `;
            });
        } catch (err) {
            console.error("查詢錯誤：", err);
            resultDiv.innerHTML = "<p>⚠️ 發生錯誤，請稍後再試</p>";
        }
    });

}else if (page === "mix_search") {

    window.addEventListener('DOMContentLoaded', () => {
  const page = document.body.dataset.page;

  if (page === "mix_search") {
    const queryTypeInput = document.getElementById("query-type");
    const sportTypeInput = document.getElementById("sport-type");
    const keywordSelect = document.getElementById("keyword");
    const searchBtn = document.getElementById("SearchBtn");
    const resetBtn = document.getElementById("ResetBtn");
    const resultArea = document.getElementById("mix-result-area");

    // 初始狀態
    sportTypeInput.disabled = true;
    keywordSelect.disabled = true;
    keywordSelect.innerHTML = `<option value="">請先選擇上方選項</option>`;

    // 類型改變
    queryTypeInput.addEventListener("change", () => {
        const type = queryTypeInput.value;

        // 🔄 重建運動種類選單（清空後重建）
        sportTypeInput.innerHTML = `<option value="">請選擇</option>`;  // 預設值
        const sportOptions = [
            { value: "1", label: "NBA" },
            { value: "2", label: "F1" },
            { value: "3", label: "MLB" },
            { value: "4", label: "CPBL" },
            { value: "5", label: "BWF" }
        ];

        sportOptions.forEach(opt => {
            // ❌ 如果是查隊伍 且是 BWF，就不顯示
            if (type === "team" && opt.value === "5") return;

            const option = document.createElement("option");
            option.value = opt.value;
            option.textContent = opt.label;
            sportTypeInput.appendChild(option);
        });

        // ✅ 若選擇球員、隊伍、賽事，都可以選運動種類
        sportTypeInput.disabled = (type === "");

        // 🔄 清空 keyword 選單
        keywordSelect.innerHTML = `<option value="">請先選擇上方選項</option>`;
        keywordSelect.disabled = true;

        fetchKeywordList(); // 🔁 重新載入關鍵字
    });


    // 運動種類改變時
    sportTypeInput.addEventListener("change", fetchKeywordList);

    function fetchKeywordList() {
      const type = queryTypeInput.value;
      const sportType = sportTypeInput.value;

      if (!type || !sportType) {
        keywordSelect.disabled = true;
        keywordSelect.innerHTML = `<option value="">請先選擇上方選項</option>`;
        return;
      }

      fetch(`/api/get_keywords?type=${type}&sport_type=${sportType}`)
        .then(res => res.json())
        .then(data => {
          if (!Array.isArray(data)) {
            alert("⚠️ 後端回傳錯誤：" + (data.error || "未知錯誤"));
            return;
          }

          keywordSelect.innerHTML = `<option value="">請選擇</option>`;
          keywordSelect.disabled = false;

          data.forEach(item => {
            const option = document.createElement("option");
            option.value = item.id;
            option.textContent = item.name;
            keywordSelect.appendChild(option);
          });
        });
    }

    // 查詢
    searchBtn.addEventListener("click", () => {
      const type = queryTypeInput.value;
      const sportType = sportTypeInput.value;
      const keyword = keywordSelect.value;
    
      if (!type || !keyword || ((type === "player" || type === "team") && !sportType)) {
        alert("請完整選擇查詢類型與條件");
        return;
      }

      fetch(`/api/mix_search?type=${type}&keyword=${keyword}&sport_type=${sportType}`)
        .then(res => res.json())
        .then(data => {
          if (!Array.isArray(data)) {
            console.error("查詢失敗：", data);
            alert("❌ 查詢失敗：" + (data.error || "請檢查參數"));
            return;
          }

          resultArea.innerHTML = '';

          const sportTypeNum = parseInt(sportType);

          if (type === "player") {
            data.forEach(player => {
              const div = document.createElement('div');
              div.className = "result-card";

              let html = `<strong>${player.name}</strong><br>`;
              html += `年齡：${player.age || '無'}<br>`;
              html += `國籍：${player.country || '未知'}<br>`;

              switch (sportTypeNum) {
                case 1:
                  html += `隊伍：${player.team_name}<br>
                           背號：${player.jersey_number}<br>
                           命中率：FG ${player.fg_pct}% / FT ${player.ft_pct}% / 3PT ${player.three_pt_pct}%<br>
                           得分：${player.points}｜籃板：${player.rebounds}｜助攻：${player.assists}`;
                  break;
                case 2:
                  html += `車隊：${player.team_name}<br>
                           車號：${player.number}<br>
                           排名：${player.ranking}｜積分：${player.pts}`;
                  break;
                case 3:
                case 4:
                  html += `隊伍：${player.team_name}<br>
                           背號：${player.jersey_number}<br>
                           守備位置：${player.position}<br>
                           打擊習慣：${player.batting_hand}<br>
                           打擊率：${player.batting_avg}`;
                  break;
                case 5:
                  html += `慣用手：${player.hand}<br>
                           世界排名：${player.world_rank}<br>
                           巡迴排名：${player.world_tour_rank}<br>
                           冠軍數：${player.world_rank_title}/${player.world_tour_rank_title}<br>
                           積分頭銜：${player.point_title}｜積分：${player.point}`;
                  break;
                default:
                  html += `（不支援顯示）`;
              }

              div.innerHTML = html;
              resultArea.appendChild(div);
            });
          }else if (type === "team") {
            data.forEach(team => {
              const div = document.createElement("div");
              div.className = "result-card";

              let html = `<strong>${team.team_name}</strong><br>`;

              
              switch (sportTypeNum) {
                case 1:
                  html += `縮寫：${team.abbr}<br>
                           城市：${team.city1 || ''} ${team.city2 || ''}<br>
                           主場：${team.arena}`;
                  break;
                case 2:
                    html += `完整名稱：${team.full_name}<br>
                            引擎供應商：${team.engine_supplier}<br>
                            車型：${team.car_type}<br>
                            隊長：${team.team_chief}<br>
                            排名：${team.ranking}｜積分：${team.team_point}<br>
                            成立年份：${team.entry_year}`;
                    break;
                case 3:
                case 4:
                  html += `城市：${team.location}<br>
                           聯盟：${team.league}<br>
                           主場：${team.stadium}<br>
                           成立年份：${team.founded_year}<br>
                           教練：${team.head_coach}`;
                  break;
                // case 5:
                //   html += `🏸 國籍名稱（隊名）：${team.team_name}`;
                //   break;
                default:
                  html += "（不支援的運動種類）";
              }

              div.innerHTML = html;
              resultArea.appendChild(div);
            });
          }else if (type === "event") {
                data.forEach(match => {
                    const div = document.createElement("div");
                    div.className = "result-card";

                    let html = `<strong>【${match.team_a_name} vs ${match.team_b_name}】</strong><br>`;
                    html += `時間：${match.date} ${match.time}<br>`;
                    html += `比數：${match.point === null ? "尚未開始" : match.point}`;

                    div.innerHTML = html;
                    resultArea.appendChild(div);
                });
            }

        });
    });

    // 重設按鈕
    resetBtn.addEventListener("click", () => {
        queryTypeInput.value = "";
        sportTypeInput.value = "";
        sportTypeInput.disabled = true;
        keywordSelect.innerHTML = `<option value="">請先選擇上方選項</option>`;
        keywordSelect.disabled = true;
        resultArea.innerHTML = "";
        });
      }
    });

}else if(page === "recent_match"){
    //UID
    let uid = "10107670810";

    const calendarEl = document.getElementById("calendar");
    const currentMonthEl = document.getElementById("current-month");
    const matchListEl = document.getElementById("match-list");
    const selectedDateEl = document.getElementById("selected-date");

    let today = new Date();
    let currentYear = today.getFullYear();
    let currentMonth = today.getMonth();

    let matchData = {};
    let existingBookings = {};
    let deletedBookings = [];
    let pendingBookings = {};
    const typeMap = {
        1: "NBA",
        2: "F1",
        3: "MLB",
        4: "CPBL",
        5: "BWF"
    };

    const weekdayNames = ["日", "一", "二", "三", "四", "五", "六"];

    function formatDateKey(date) {
        return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
    }

    async function loadBookings() {
        const res = await fetch(`/api/bookings/user/${uid}`);
        existingBookings = await res.json(); 
        displayBookedMatches();
        
        await loadTopPlatform(uid);
    }

    async function loadTopPlatform(uid) {
        const res = await fetch(`/api/platform/rank/${uid}`);
        const platforms = await res.json();

        const box = document.getElementById("recommend-platform");
        if (!box) return;

        box.innerHTML = ""; // 清空舊內容

        if (platforms.length === 0) {
            box.innerHTML = `<div class="platform-card">📺 您尚未預約任何比賽</div>`;
            return;
        }

        const maxUsage = platforms[0].usage_count;
        const topPlatforms = platforms.filter(p => p.usage_count === maxUsage);

        // 建立卡片
        const card = document.createElement("div");
        card.className = "platform-card";

        const title = document.createElement("h3");
        title.textContent = "為您推薦平台";
        title.style.marginBottom = "0.5rem";

        const list = document.createElement("ul");
        list.style.listStyle = "none";
        list.style.paddingLeft = "0";

        for (const p of topPlatforms) {
            const li = document.createElement("li");
            li.innerHTML = `🎖️ <strong>${p.platform_name}</strong>（預約次數 ${p.usage_count}）`;
            list.appendChild(li);
        }

        card.appendChild(title);
        card.appendChild(list);
        box.appendChild(card);
    }


    async function loadMatchData() {
        
        try {
            const res = await fetch('/api/matches');
            const rawList = await res.json();
            matchData = {}; // 清空原本資料

            for (let date in rawList) {
                matchData[date] = rawList[date].map(match => ({
                    name: match.name,
                    time: match.time,
                    platform: match.platform,
                    type: match.type
                }));
            }

            renderCalendar(currentYear, currentMonth);
            await loadBookings();
        } catch (err) {
            console.error('❌ 無法載入比賽資料:', err);
        }
        console.log("📦 matchData", matchData);
    }
    function isBooked(dateStr, matchName) {
        const data = existingBookings[dateStr] || [];
        return data.some(m => m.name === matchName);
    }

    function displayBookedMatches() {
        const bookedEl = document.getElementById("booked-matches");
        if (!bookedEl) return;
        bookedEl.innerHTML = "";

        bookedEl.innerHTML += `<h3>🆕 剛新增</h3>`;
        for (let date in pendingBookings) {
            for (let match of pendingBookings[date]) {
                bookedEl.appendChild(createBookingCard(date, match, true));
            }
        }

        bookedEl.innerHTML += `<h3>✅ 已預約</h3>`;
        for (let date in existingBookings) {
            for (let match of existingBookings[date]) {
                bookedEl.appendChild(createBookingCard(date, match, false));
            }
        }

        const total =
            Object.values(existingBookings).reduce((sum, arr) => sum + arr.length, 0) +
            Object.values(pendingBookings).reduce((sum, arr) => sum + arr.length, 0);
        document.getElementById("booking-count").textContent = `已預約 + 新增 ${total} 場比賽`;
    }

    function createBookingCard(date, match, isNew) {
        const card = document.createElement("div");
        card.className = "booking-card";

        const content = document.createElement("div");
        content.className = "card-content";
        console.log(typeMap[match.type]);
        content.innerHTML = `
            【${typeMap[match.type]}】  ${match.name}<br>
            📅 <strong>${date}</strong> - 🕒 ${match.time}<br>
            📺 平台：${match.platform}<br>
        `;

        const cancelBtn = document.createElement("button");
        cancelBtn.textContent = "X";
        cancelBtn.dataset.date = date;
        cancelBtn.dataset.name = match.name;
        cancelBtn.dataset.time = match.time;
        cancelBtn.dataset.isNew = isNew;

        card.appendChild(content);
        card.appendChild(cancelBtn);
        return card;
    }

    document.getElementById("booked-matches").addEventListener("click", function (e) {
        if (e.target.tagName === "BUTTON" && e.target.textContent === "X") {
            const { date, name, time, isNew } = e.target.dataset;
            const target = isNew === "true" ? pendingBookings : existingBookings;

            if (!target[date]) return;

            const idx = target[date].findIndex(m => m.name === name && m.time === time);
            if (idx !== -1) {
                const removed = target[date].splice(idx, 1)[0];
                if (target[date].length === 0) delete target[date];
                deletedBookings.push({ date, match: removed, isNew: isNew === "true" });
            }

            displayBookedMatches();
            refreshSelectedDate(date);
        }
    });

    function isAlreadySelected(dateStr, matchObj) {
        const check = list => (list[dateStr] || []).some(m => m.name === matchObj.name && m.time === matchObj.time);
        return check(existingBookings) || check(pendingBookings);
    }

    function selectDate(dateStr, cell) {
        document.querySelectorAll(".calendar-grid .selected").forEach(el => el.classList.remove("selected"));
        cell.classList.add("selected");

        selectedDateEl.textContent = `📅 ${dateStr} 的比賽`;
        matchListEl.innerHTML = "";

        const matches = matchData[dateStr];
        if (matches) {
        let hasVisible = false;

        matches.forEach((matchObj) => {
            const matchDateTime = new Date(`${dateStr}T${matchObj.time}:00`);
            const now = new Date();
            const diffMinutes = (matchDateTime - now) / (1000 * 60);

            if (isAlreadySelected(dateStr, matchObj)) return;  // 已選擇就跳過

            hasVisible = true; // 有比賽可以顯示

            const btn = document.createElement("button");
            btn.className = "match-card";
            btn.textContent = `【${typeMap[matchObj.type]}】 ${matchObj.name} 🕒 ${matchObj.time}`;

            if (diffMinutes < 30) {
                btn.classList.add("disabled");
                btn.addEventListener("click", () => {
                alert(`⛔ 此比賽已過或即將開始，無法預約。\n ${matchObj.name}\n📅 ${dateStr}\n🕒 ${matchObj.time}`);
            });
            } else {
            btn.addEventListener("click", async () => {
                console.log('selected');
                if (!pendingBookings[dateStr]) pendingBookings[dateStr] = [];
                const now = new Date();
                pendingBookings[dateStr].push({ ...matchObj });
                displayBookedMatches();
                btn.remove();

                // ✅ 檢查是否所有比賽都被選完
                const remaining = matchData[dateStr].filter(m => !isAlreadySelected(dateStr, m));
                if (remaining.length === 0) {
                    matchListEl.innerHTML = "<li>✅ 今天的比賽都已預約或選擇完畢！</li>";
                }
            });
            }

            matchListEl.appendChild(btn);
        });

        // 若全部比賽都已選擇，顯示提示
        if(!hasVisible) {
            matchListEl.innerHTML = "<li>✅ 今天的比賽都已預約或選擇完畢！</li>";
            displayBookedMatches();
        }

        }else{
            matchListEl.innerHTML = "<li>❌ 沒有比賽資訊</li>";
        }

    }

    function refreshSelectedDate(dateOverride) {
        const selectedDayCell = document.querySelector(".calendar-grid .selected");

        if (dateOverride) {
            // 傳入的是完整的 date 字串：2025-05-12
            const [y, m, d] = dateOverride.split("-");
            const selectedKey = `${y}-${String(m).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
            const allCells = document.querySelectorAll(".calendar-grid div");

            // 嘗試找對應的 cell 並選起來
            for (let cell of allCells) {
            if (cell.textContent.padStart(2, "0") === d) {
                selectDate(selectedKey, cell);
                break;
            }
            }
        } else if (selectedDayCell) {
            const selectedDate = selectedDayCell.textContent.padStart(2, "0");
            const today = new Date();
            const selectedKey = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${selectedDate}`;
            selectDate(selectedKey, selectedDayCell);
        }
    }

    function renderCalendar(year, month) {
        calendarEl.innerHTML = "";

        for (let i = 0; i < 7; i++) {
            const header = document.createElement("div");
            header.textContent = "週" + weekdayNames[i];
            header.classList.add("weekday-header");
            calendarEl.appendChild(header);
        }

        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const startWeekday = firstDay.getDay();
        const daysInMonth = lastDay.getDate();

        currentMonthEl.textContent = `${year} 年 ${month + 1} 月`;

        for (let i = 0; i < startWeekday; i++) {
            const emptyCell = document.createElement("div");
            calendarEl.appendChild(emptyCell);
        }

        for (let day = 1; day <= daysInMonth; day++) {
            const cell = document.createElement("div");
            const cellDate = new Date(year, month, day);
            const key = formatDateKey(cellDate);

            cell.textContent = day;
            cell.addEventListener("click", () => selectDate(key, cell));

            if (key === formatDateKey(new Date())) {
                cell.classList.add("today");
            }

            if (cellDate < new Date(today.getFullYear(), today.getMonth(), today.getDate())) {
                cell.classList.add("past");
            }

            calendarEl.appendChild(cell);

            if (year === today.getFullYear() && month === today.getMonth()) {
                const allCells = calendarEl.querySelectorAll("div");
                for (let cell of allCells) {
                    if (cell.textContent === String(today.getDate())) {
                    const key = formatDateKey(today);
                    selectDate(key, cell);
                    break;
                    }
                }
            }
        }
    }

    function addPendingBooking(dateStr, matchObj) {
        if (!pendingBookings[dateStr]) pendingBookings[dateStr] = [];
        const now = new Date();
        pendingBookings[dateStr].push({
            ...matchObj,
            booked_at: now.toISOString()
        });
        displayBookedMatches();
    }

    async function clearAllBookings() {
        if (Object.keys(pendingBookings).length + Object.keys(existingBookings).length === 0) {
            alert("⚠️ 沒有新增預約可刪除！");
            return;
        }
        if (confirm("確定要清除所有預約嗎？")) {
            await fetch(`/api/bookings/user/${uid}`, { method: 'DELETE' });
            bookingData = {};
            alert("所有預約已清除！");
        }
        displayBookedMatches();
        loadMatchData();
    }

    async function saveBookings() {
        if (Object.keys(pendingBookings).length === 0 && deletedBookings.length === 0) {
            alert("⚠️ 沒有新增或刪除的預約可儲存！");
            return;
        }

        const merged = structuredClone(existingBookings);

        for (let date in pendingBookings) {
            if (!merged[date]) merged[date] = [];
            merged[date] = merged[date].concat(pendingBookings[date]);
        }

        for (let { date, match } of deletedBookings) {
            if (!merged[date]) continue;
            merged[date] = merged[date].filter(m => !(m.name === match.name && m.time === match.time));
            if (merged[date].length === 0) delete merged[date];
        }

        const res = await fetch(`/api/bookings/user/${uid}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(merged)
        });

        if (res.ok) {
            const total = Object.values(merged).reduce((sum, arr) => sum + arr.length, 0);
            alert(`✅ 已儲存 ${total} 筆預約資料！`);
            pendingBookings = {};
            deletedBookings = [];
            existingBookings = merged;
            displayBookedMatches();
            await loadTopPlatform(uid);
        } else {
            alert("❌ 儲存失敗！");
        }
    }

    async function saveBookingsToUser() {
        const res = await fetch(`/api/bookings/user/${uid}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(bookingData)
        });

        if (res.ok) {
            alert("✅ 儲存成功！");
        }
    }

    function prevMonth() {
        currentMonth--;
        if (currentMonth < 0) {
            currentMonth = 11;
            currentYear--;
        }
        renderCalendar(currentYear, currentMonth);
    }

    function nextMonth() {
        currentMonth++;
        if (currentMonth > 11) {
            currentMonth = 0;
            currentYear++;
        }
        renderCalendar(currentYear, currentMonth);
    }

    function updateClock() {
        const now = new Date();
        const yyyy = now.getFullYear();
        const mm = String(now.getMonth() + 1).padStart(2, '0');
        const dd = String(now.getDate()).padStart(2, '0');
        const hh = String(now.getHours()).padStart(2, '0');
        const min = String(now.getMinutes()).padStart(2, '0');
        const sec = String(now.getSeconds()).padStart(2, '0');
        const formatted = `${yyyy}-${mm}-${dd} ${hh}:${min}:${sec}`;
        document.getElementById("now-time").textContent = formatted;
    }

    updateClock();
    setInterval(updateClock, 1000);

    loadMatchData();

    document.getElementById('PrevMonthBtn').addEventListener('click', prevMonth);
    document.getElementById('NextMonthBtn').addEventListener('click', nextMonth);
    document.getElementById('save').addEventListener('click', saveBookings);
    document.getElementById('cancel').addEventListener('click', clearAllBookings);
}