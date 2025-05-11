const page = document.body.dataset.page;

if(page === "door"){
    
}else if(page === "search"){
    // 自動產生時間下拉選項（00:00～23:30）
    function populateTimeOptions(selectId) {
        const select = document.getElementById(selectId);
        for (let h = 0; h < 24; h++) {
        for (let m = 0; m < 60; m += 30) {
            const hh = String(h).padStart(2, '0');
            const mm = String(m).padStart(2, '0');
            const option = document.createElement("option");
            option.value = `${hh}:${mm}`;
            option.textContent = `${hh}:${mm}`;
            select.appendChild(option);
        }
        }
    }

    populateTimeOptions('start-time');
    populateTimeOptions('end-time');

    //查詢功能
    function searchMatches() {
        const sport = document.getElementById('sport');
        const player = document.getElementById('player').value.trim();
        const start = document.getElementById('start-time').value;
        const end = document.getElementById('end-time').value;

        if (start && end && start >= end) {
        alert("❌ 結束時間必須晚於開始時間！");
        return;
        }
        
        let result = `✅ 運動類型：${sport.options[sport.selectedIndex].text}\n`;

        if (player) result += `👤 選手名稱：${player}\n`;
        if (start && end) result += `🕒 時間區間：${start} ～ ${end}`;

        if (!player && !start && !end) {
        alert("請至少輸入選手名稱或選擇時間區間！");
        return;
        }

        alert(result);
    }

    //重設reset功能
    function resetForm() {
        document.getElementById('sport').selectedIndex = document.getElementById('sport')[0];
        document.getElementById('player').value = "";
        document.getElementById('date').value = "";
        document.getElementById('start-time').selectedIndex = 0;
        document.getElementById('end-time').selectedIndex = 0;
    }

    //按鈕事件綁定
    document.getElementById('SearchBtn').addEventListener('click', searchMatches);
    document.getElementById('ResetBtn').addEventListener('click', resetForm);

}else if(page === "mix_search"){
    function searchComposite() {
        const type = document.getElementById('query-type').value;
        const keyword = document.getElementById('keyword').value.trim();
        const typeText = document.getElementById('query-type').options[
        document.getElementById('query-type').selectedIndex
        ].text;
    
        if (!keyword) {
        alert("請輸入關鍵字！");
        return;
        }
    
        // 模擬導向查詢結果（你可以改成 location.href = "..."）
        alert(`🔎 查詢類型：${typeText}\n關鍵字：${keyword}\n即將導向對應資料頁面...`);
        
        const encodedKeyword = encodeURIComponent(keyword);
        location.href = `/result?type=${type}&keyword=${encodedKeyword}`;
    }

  
    function resetForm() {
        document.getElementById('query-type').selectedIndex = 0;
        document.getElementById('keyword').value = "";
    }

    //按鈕事件綁定
    document.getElementById('SearchBtn').addEventListener('click', () =>{
        searchComposite();
        resetForm();
    })
    document.getElementById('ResetBtn').addEventListener('click', resetForm);

}else if(page === "result"){
    // 讀取 URL 查詢參數
    const params = new URLSearchParams(window.location.search);
    const type = params.get("type");
    const keyword = params.get("keyword");

    // 類型轉換（可做本地對照資料庫）
    const typeMap = {
      player: "球員名稱",
      team: "球隊名稱",
      event: "賽事名稱",
      rule: "運動規則"
    };

    // 模擬查詢資料（可串 JSON、API）
    const resultArea = document.getElementById("result-area");
    if (type && keyword) {
      resultArea.innerHTML = `
        <h2>查詢類型：${typeMap[type] || type}</h2>
        <p>關鍵字：<strong>${decodeURIComponent(keyword)}</strong></p>
        <p>這裡會顯示與「${keyword}」相關的資訊。</p> 
      `;
    } else {
      resultArea.innerHTML = `<p>❗ 找不到查詢參數，請回首頁重新查詢。</p>`;
    }
    
}else if(page === "recent_match"){
    //UID
    let uid = "22222222222";

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

    const weekdayNames = ["日", "一", "二", "三", "四", "五", "六"];

    function formatDateKey(date) {
        return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
    }

    async function loadBookings() {
        const res = await fetch(`/api/bookings/user/${uid}`);
        existingBookings = await res.json(); 
        displayBookedMatches();
    }

    async function loadMatchData() {
        try {
            const res = await fetch('/api/matches');
            matchData = await res.json();
            renderCalendar(currentYear, currentMonth);
            await loadBookings();
        } catch (err) {
            console.error('❌ 無法載入比賽資料:', err);
        }
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
        const bookedTime = match.booked_at ? new Date(match.booked_at).toLocaleString() : "未知時間";

        content.innerHTML = `
            🏟️ ${match.name}<br>
            📅 <strong>${date}</strong> - 🕒 ${match.time}<br>
            📺 平台：${match.platform}<br>
            📆 預約時間：${bookedTime}<br>
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
            btn.textContent = `🏟️ ${matchObj.name} 🕒 ${matchObj.time}`;

            if (diffMinutes < 30) {
                btn.classList.add("disabled");
                btn.addEventListener("click", () => {
                alert(`⛔ 此比賽已過或即將開始，無法預約。\n🏟️ ${matchObj.name}\n📅 ${dateStr}\n🕒 ${matchObj.time}`);
            });
            } else {
            btn.addEventListener("click", async () => {
                console.log('selected');
                if (!pendingBookings[dateStr]) pendingBookings[dateStr] = [];
                const now = new Date();
                pendingBookings[dateStr].push({ ...matchObj, booked_at: now.toISOString() });
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