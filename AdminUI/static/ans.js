  function updateDateTime() {
    const now = new Date();
  
    // 台灣時區 UTC+8 補正：加上 8 小時的毫秒數
    const taiwanTime = new Date(now.getTime() + 8 * 60 * 60 * 1000);
  
    const pad = (n) => n.toString().padStart(2, '0');
    const dateStr = `${taiwanTime.getUTCFullYear()}-${pad(taiwanTime.getUTCMonth() + 1)}-${pad(taiwanTime.getUTCDate())}`;
    const timeStr = `${pad(taiwanTime.getUTCHours())}:${pad(taiwanTime.getUTCMinutes())}:${pad(taiwanTime.getUTCSeconds())}`;
  
    document.getElementById("announceDate").innerText = `${dateStr} ${timeStr}`;
  }
  
  document.addEventListener("DOMContentLoaded", () => {
    updateDateTime();                     // 頁面載入時立即執行
    setInterval(updateDateTime, 1000);    // 每秒更新一次
  });


  console.log("🔔 submitAnnouncement triggered!");
  async function submitAnnouncement() {
    const content = document.getElementById("announcementInput").value.trim();
    const author = document.getElementById("authorInput").value.trim();
    const datetime = document.getElementById("announceDate").innerText;
    const timestamp = Date.now();
    const status = document.getElementById("announceStatus");
  
    if (!content) {
        status.innerText = "❌ 請輸入公告內容";
        status.style.color = "red";
        return;
    } else if (!author){
        status.innerText = "❌ 請輸入發布者";
        status.style.color = "red";
        return;
    }
  
    const res = await fetch("/api/announce", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content, author, datetime, timestamp })
    });
  
    const result = await res.json();
    if (result.success) {
      status.innerText = "✅ 公告發佈成功！";
      status.style.color = "green";
      document.getElementById("announcementInput").value = "";
      document.getElementById("authorInput").value = "";
    } else {
      status.innerText = "❌ 發佈失敗";
      status.style.color = "red";
    }

    //3 秒後自動清除提示
    setTimeout(() => {
        status.innerText = "";
    }, 2000);

    // 展開區塊 + 立即更新歷史紀錄
    document.getElementById("historyArea").style.display = "block";
    loadHistory();
  }

  function toggleHistory() {
    const area = document.getElementById('historyArea');
    if (area.style.display === 'none') {
      area.style.display = 'block';
      loadHistory();
    } else {
      area.style.display = 'none';
    }
  }
  
  async function loadHistory() {
    const res = await fetch('/announcements.json'); // 假設你開放這個 JSON
    const data = await res.json();
  
    const area = document.getElementById('historyArea');
    area.innerHTML = '';
  
    if (data.length === 0) {
      area.innerHTML = '<p>🚫 尚無公告</p>';
      return;
    }
  
    [...data].reverse().forEach((ann) => {
      const div = document.createElement('div');
      div.className = 'announcement';
      div.innerHTML = `
        <p>📣 ${ann.content}</p>
        <hr>
        <div class="meta">
        🕒 ${ann.datetime} ｜ 👤 ${ann.author}
        <button onclick="deleteAnnouncement(${ann.timestamp})" style="margin-left: 1rem;">🗑️ 刪除</button>
        </div>
      `;
      area.appendChild(div);
    });
  }

  async function deleteAnnouncement(timestamp) {
    const res = await fetch(`/api/announce/${timestamp}`, { method: 'DELETE' });
    const result = await res.json();
    if (result.success) {
      alert("✅ 已刪除公告");
      loadHistory();  // 立即更新
    } else {
      alert("❌ 刪除失敗");
    }
  }
  
  
