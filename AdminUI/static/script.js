const page = document.body.dataset.page;

//重製登入畫面，只保留帳號
function resetlogin() {
    document.getElementById('password').value = "";

    const confirmLabel = document.querySelector('label[for="confirm-password"]');
    const confirmInput = document.getElementById('confirm-password');
    if (confirmLabel) confirmLabel.remove();
    if (confirmInput) confirmInput.remove();

    document.getElementById('form-title').textContent = '管理者登入';
    document.querySelector('.sign_in').textContent = 'Sign In';
    const submitButton = document.getElementById('submit-button');
    submitButton.value = '登入';

    mode = 'login';
}

//整合所有頁面到js
if(page === 'login'){
    let mode = 'login';  // 預設是登入模式

    // 登入/註冊 提交邏輯
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();

        if (mode === 'login') {
            // === 登入 ===
            const res = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const data = await res.json();
            if (data.success) {
                window.location.href = '/control_panel';
            } else {
                alert('帳號或密碼錯誤');
            }
        } else if (mode === 'register') {
            // === 註冊 ===
            const confirmPassword = document.getElementById('confirm-password').value.trim();

            if (!username || !password || !confirmPassword) {
                alert('請填寫所有欄位');
                return;
            }

            if (password !== confirmPassword) {
                alert('密碼和確認密碼不一致');
                return;
            }

            const res = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const data = await res.json();
            if (data.success) {
                alert('註冊成功！現在可以登入');
                switchToLogin();
            } else {
                alert(data.message || '註冊失敗');
            }
        }
    });

    // 點擊 Sign In 切換到註冊模式
    document.querySelector('.sign_in').addEventListener('click', () => {
        if (mode === 'login') {
            switchToRegister();
        } else {
            switchToLogin();
        }
    });

    // 切換到註冊模式
    function switchToRegister() {
        mode = 'register';
        document.getElementById('form-title').textContent = '管理者註冊';
        document.querySelector('.sign_in').textContent = 'Log In';

        
        
        const submitButton = document.getElementById('submit-button');
        submitButton.value = '註冊';

        // 檢查是否已經有確認密碼欄位，如果沒有就新增
        if (!document.getElementById('confirm-password')) {
            const confirmLabel = document.createElement('label');
            confirmLabel.setAttribute('for', 'confirm-password');
            confirmLabel.textContent = '確認密碼：';

            const confirmInput = document.createElement('input');
            confirmInput.type = 'password';
            confirmInput.id = 'confirm-password';
            confirmInput.name = 'confirm-password';
            confirmInput.required = true;

            const form = document.querySelector('.login-form');
            form.insertBefore(confirmLabel, submitButton);
            form.insertBefore(confirmInput, submitButton);
        }
            document.getElementById('password').value = "";
            document.getElementById('confirm-password').value = "";
    }

    // 切換回登入模式
    function switchToLogin() {
        mode = 'login';
        document.getElementById('form-title').textContent = '管理者登入';
        document.querySelector('.sign_in').textContent = 'Sign In';

        
        document.getElementById('password').value = "";
        const submitButton = document.getElementById('submit-button');
        submitButton.value = '登入';

        // 移除確認密碼欄位（如果有的話）
        const confirmLabel = document.querySelector('label[for="confirm-password"]');
        const confirmInput = document.getElementById('confirm-password');
        if (confirmLabel) confirmLabel.remove();
        if (confirmInput) confirmInput.remove();
    }


    //每次進到登入畫面，都reset畫面到只有帳號
    window.addEventListener('pageshow', function(event) {
    if (event.persisted || (window.performance && performance.navigation.type === 2)) {
        resetlogin();
    }
});

}else if (page === 'sql'){

    // 通用畫面重置 function（不影響資料）
    function resetAddSection() {
        const tbody = document.querySelector('#addTable tbody');
        tbody.innerHTML = `<tr>
        <td><input type="text" placeholder="ID"></td>
        <td><input type="text" placeholder="對戰組合"></td>
        <td><input type="text" placeholder="YYYY-MM-DD"></td>
        <td><input type="text" placeholder="HH:MM"></td>
        </tr>`;
        document.getElementById('addStatus').innerText = '';
        document.getElementById('addStatus').className = '';
    }
  
    //   function confirmRowDelete(btn) {
    //     if (confirm('確定要刪除此列資料嗎？')) {
    //       btn.closest('tr').remove();
    //     }
    //   }
  
  function addRow() {
    const tbody = document.querySelector('#addTable tbody');
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><input type="text" placeholder="ID"></td>
      <td><input type="text" placeholder="對戰組合"></td>
      <td><input type="text" placeholder="YYYY-MM-DD"></td>
      <td><input type="text" placeholder="HH:MM"></td>
      <td><button onclick="this.closest('tr').remove();">X</button></td>
    `;
    tbody.appendChild(tr);
  }
  
  async function searchMatch() {
    const keyword = document.getElementById('searchInput').value.trim().toLowerCase();
    const resultDiv = document.getElementById('searchResult');
    resultDiv.innerHTML = '';
    if (!keyword) return;
  
    const res = await fetch(`/api/search?keyword=${encodeURIComponent(keyword)}`);
    const data = await res.json();
    if (data.matches.length === 0) {
      resultDiv.innerHTML = '<p style="color: red;">❌ 沒有找到符合的比賽資料。</p>';
      return;
    }
  
    data.matches.forEach(m => {
      const div = document.createElement('div');
      div.className = 'match-card';
      div.id = `card_${m.id}`;
      div.innerHTML = `
        <strong class="match-title">${m.match}</strong>｜<span class="match-datetime">${m.date} ${m.time}</span>
        <button onclick="showEditForm(${m.id}, '${m.match}', '${m.date}', '${m.time}')">修改</button>
        <button onclick="confirmDelete(${m.id})">刪除</button>
        <div id="editForm_${m.id}" class="edit-form" style="margin-top:0.5rem;"></div>
      `;
      resultDiv.appendChild(div);
    });
  }
  async function submitAllMatches() {
    const rows = document.querySelectorAll('#addTable tbody tr');
    const matches = [];
    rows.forEach(row => {
      const inputs = row.querySelectorAll('input');
      const [id, match, date, time] = [...inputs].map(i => i.value.trim());
      if (id && match && date && time) {
        matches.push({ id: parseInt(id), match, date, time });
      }
    });
  
    const res = await fetch('/api/add-many', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ matches })
    });
  
    const data = await res.json();
    const status = document.getElementById('addStatus');
    if (data.success) {
        status.innerText = `✅ 新增 ${data.count} 筆資料完成`;
        status.className = 'success';
        searchMatch();
      
    } else {
      status.innerText = `❌ ${data.message}`;
      status.className = 'error';
    }

    setTimeout(() => {
        resetAddSection();
      }, 2500)
  }

  function showEditForm(id, match, date, time) {
    const container = document.getElementById(`editForm_${id}`);
    container.innerHTML = `
      <input type="text" id="match_${id}" value="${match}">
      <input type="text" id="date_${id}" value="${date}">
      <input type="text" id="time_${id}" value="${time}">
      <button onclick="saveEdit(${id})">儲存</button>
    `;
  }
  
  async function saveEdit(id) {
    const match = document.getElementById(`match_${id}`).value.trim();
    const date = document.getElementById(`date_${id}`).value.trim();
    const time = document.getElementById(`time_${id}`).value.trim();
  
    const res = await fetch(`/api/edit/${id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ match, date, time })
    });
    const result = await res.json();
    if (result.success) {
      alert('✅ 修改完成');
      const card = document.getElementById(`card_${id}`);
      card.querySelector('.match-title').innerText = match;
      card.querySelector('.match-datetime').innerText = `${date} ${time}`;
      card.querySelector('.edit-form').innerHTML = '';
    } else {
      alert(`❌ 修改失敗：${result.message}`);
    }
  }
  
  async function confirmDelete(id) {
    const yes = confirm('確定要刪除此比賽嗎？');
    if (!yes) return;
    const res = await fetch(`/api/delete/${id}`, { method: 'DELETE' });
    const result = await res.json();
    if (result.success) {
      alert('✅ 刪除完成');
      const card = document.getElementById(`card_${id}`);
      if (card) card.remove();
    } else {
      alert(`❌ 刪除失敗：${result.message}`);
    }
  }

  //按鈕事件綁定
  document.getElementById('SearchBtn').addEventListener('click', searchMatch);
  document.getElementById('AddBtn').addEventListener('click', addRow);
  document.getElementById('SendAddBtn').addEventListener('click', submitAllMatches);
}else if (page === 'announcement'){

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
          <button class="DeleteAnsBtn" data-timestamp="${ann.timestamp}" style="margin-left: 1rem;">🗑️ 刪除</button>
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

    //按鈕事件綁定
    document.getElementById('PostBtn').addEventListener('click', submitAnnouncement);
    document.getElementById('ShowAndHideBtn').addEventListener('click', toggleHistory);
    //用事件代理監聽刪除按鈕點擊
    document.getElementById('historyArea').addEventListener('click', function(e) {
    if (e.target.classList.contains('DeleteAnsBtn')) {
        const timestamp = e.target.dataset.timestamp;
        deleteAnnouncement(timestamp);
    }
});

}else if(page === 'update-summary'){
  
}else if(page === 'UI'){
    
  async function goToSQL() {
    const res = await fetch('/sql');
    if (res.ok) {
      window.location.href = '/sql';
    } else {
      alert('無法前往 SQL 操作區');
    }
  }

  async function goToAnnouncements() {
    const res = await fetch('/announcements');
    if (res.ok) {
      window.location.href = '/announcements';
    } else {
      alert('無法載入公告管理');
    }
  }

  async function goToFeedback() {
    const res = await fetch('/feedback');
    if (res.ok) {
      window.location.href = '/feedback';
    } else {
      alert('載入意見回饋失敗');
    }
  }

  async function goToUpdateSummary() {
    const res = await fetch('/update-summary');
    if (res.ok) {
      window.location.href = '/update-summary';
    } else {
      alert('無法取得更新摘要');
    }
  }

  //按鈕事件綁定
  document.getElementById('sqlBtn').addEventListener('click', goToSQL);
  document.getElementById('announcementsBtn').addEventListener('click', goToAnnouncements);
  document.getElementById('feedbackBtn').addEventListener('click', goToFeedback);
  document.getElementById('updateSummaryBtn').addEventListener('click', goToUpdateSummary);

}else if(page === 'feedback'){

}