//UID
let uid = "22222222222"; // ⚠️ 你可以從登入系統或 LINE 傳來

const calendarEl = document.getElementById("calendar");
const currentMonthEl = document.getElementById("current-month");
const matchListEl = document.getElementById("match-list");
const selectedDateEl = document.getElementById("selected-date");

let today = new Date();
let currentYear = today.getFullYear();
let currentMonth = today.getMonth();

let matchData = {};
let bookingData = {};

const weekdayNames = ["日", "一", "二", "三", "四", "五", "六"];

function formatDateKey(date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

async function loadBookings() {
  const res = await fetch(`/api/bookings/user/${uid}`);
  bookingData = await res.json();  // ⚠️ bookingData 就會是多筆的
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

function isBooked(dateStr, matchName) {
  if (!bookingData[dateStr]) return false;
  return bookingData[dateStr].some(m => m.name === matchName);
}

function displayBookedMatches() {
  const bookedEl = document.getElementById("booked-matches");
  if (!bookedEl) return;

  
  const count = Object.values(bookingData).reduce((sum, arr) => sum + arr.length, 0);
  document.getElementById("booking-count").textContent = `✅ 已預約 ${count} 場比賽`;

  bookedEl.innerHTML = "";

  for (let date in bookingData) {
    for (let match of bookingData[date]) {
      // const key = `${date}-${match.name}`;
      const card = document.createElement("div");
      card.className = "booking-card";
      
      const content = document.createElement("div");
      content.className = "card-content";

      const bookedTime = match.booked_at
      ? new Date(match.booked_at).toLocaleString()
      : "未知時間";

      content.innerHTML = `
        🏟️ ${match.name}<br>
        📅 <strong>${date}</strong> - 🕒 ${match.time}<br>
        📺 平台：${match.platform}<br>
        📆 預約時間：${bookedTime}<br>
      `;
      
      const cancelBtn = document.createElement("button");
      cancelBtn.textContent = "❌ 取消預約";
      cancelBtn.onclick = () => {
        bookingData[date] = bookingData[date].filter(m => m.name !== match.name);
        if (bookingData[date].length === 0) delete bookingData[date];
        displayBookedMatches();
        refreshSelectedDate();
      };
      
      card.appendChild(content);
      card.appendChild(cancelBtn);
      bookedEl.appendChild(card);
    }
  }

  if (!bookedEl.innerHTML) {
    bookedEl.innerHTML = "<p>目前沒有已預約的比賽</p>";
  }
}


function selectDate(dateStr, cell) {
  document.querySelectorAll(".calendar-grid .selected").forEach(el => el.classList.remove("selected"));
  cell.classList.add("selected");

  selectedDateEl.textContent = `📅 ${dateStr} 的比賽`;
  matchListEl.innerHTML = "";

  const matches = matchData[dateStr];
  if (matches) {
    matches.forEach((matchObj, index) => {
      const matchKey = `${dateStr}-match-${index}`;
      const matchDateTime = new Date(`${dateStr}T${matchObj.time}:00`);
      const now = new Date();
      const diffMinutes = (matchDateTime - now) / (1000 * 60);

      // if (isBooked(matchKey)) return;
      if (isBooked(dateStr, matchObj.name)) return;


      const btn = document.createElement("button");
      btn.className = "match-card";
      btn.textContent = `🏟️ ${matchObj.name} 🕒 ${matchObj.time}`;

      if (diffMinutes < 30) {
        btn.classList.add("disabled");
        btn.addEventListener("click", () => {
          alert(`
              （⛔ 此比賽已過或即將開始，無法預約）
              🏟️ ${matchObj.name}
              📅 ${dateStr}
              🕒 ${matchObj.time}
              📺 平台：${matchObj.platform}
              🎯 比分：${matchObj.point}`.trim());
        });
      } else {
        btn.addEventListener("click", async () => {
          if (!bookingData[dateStr]) {
            bookingData[dateStr] = [];
          }
          const now = new Date();
          const matchWithTime = {
            ...matchObj,
            booked_at: now.toISOString()  // ✅ 存下預約當下時間
          };

          bookingData[dateStr].push(matchWithTime);
          displayBookedMatches();     // 更新下方列表
          btn.remove();               // 拿掉上方按鈕
        });
      }

      matchListEl.appendChild(btn);
    });
  } else {
    matchListEl.innerHTML = "<li>沒有比賽資訊</li>";
  }
}

function refreshSelectedDate() {
  const selectedDayCell = document.querySelector(".calendar-grid .selected");
  if (selectedDayCell) {
    const selectedDate = selectedDayCell.textContent.padStart(2, "0");
    const selectedKey = `${currentYear}-${String(currentMonth + 1).padStart(2, "0")}-${selectedDate}`;
    selectDate(selectedKey, selectedDayCell);
  }
}

function addBookedCard(key) {
  const bookedEl = document.getElementById("booked-matches");
  const [date, index] = key.split("-match-");
  const matchObj = matchData[date]?.[index];
  if (!matchObj) return;

  const card = document.createElement("div");
  card.className = "booking-card";
  card.id = "booked-" + key;

  const title = document.createElement("div");
  title.innerHTML = `
    📅 <strong>${date}</strong> - 🕒 ${matchObj.time}<br>
    🏟️ ${matchObj.name}<br>
    📺 平台：${matchObj.platform}<br>
    🎯 比分：${matchObj.point}
  `;

  const cancelBtn = document.createElement("button");
  cancelBtn.textContent = "❌ 取消預約";
  cancelBtn.onclick = async () => {
    await fetch(`/api/bookings/${key}`, { method: 'DELETE' });
    delete bookingData[key];
    card.remove();
    refreshSelectedDate();
    displayBookedMatches();
  };

  card.appendChild(title);
  card.appendChild(cancelBtn);
  bookedEl.appendChild(card);
}

async function clearAllBookings() {
  if (confirm("確定要清除所有預約嗎？")) {
    await fetch(`/api/bookings/user/${uid}`, { method: 'DELETE' });
    bookingData = {};
    alert("所有預約已清除！");
    displayBookedMatches();
    refreshSelectedDate();
  }
}

async function saveBookings() {
  if (Object.keys(bookingData).length === 0) {
    alert("⚠️ 沒有預約資料可儲存！");
    return;
  }

  //原本是timestamp當獨立ID
  // const timestamp = Date.now().toString();


  const res = await fetch(`/api/bookings/user/${uid}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(bookingData)
  });

  if (res.ok) {
    const total = Object.values(bookingData).reduce((sum, arr) => sum + arr.length, 0);
    alert(`✅ 已儲存 ${total} 筆預約資料，ID：${uid}`);
  } else {
    alert("❌ 儲存失敗！");
  }
}

async function saveBookingsToUser() {
  const res = await fetch(`/api/bookings/user/${uid}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(bookingData)  // ✅ 傳整包
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

loadMatchData();  // ⬅️ 主入口
