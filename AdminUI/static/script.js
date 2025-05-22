const page = document.body.dataset.page;

//重製登入畫面，只保留帳號
function resetlogin() {
    document.getElementById('password').value = "";

    const confirmLabel = document.querySelector('label[for="confirm-password"]');
    const confirmInput = document.getElementById('confirm-password');
    if (confirmLabel) confirmLabel.remove();
    if (confirmInput) confirmInput.remove();

    document.getElementById('form-title').textContent = '管理者登入';
    document.querySelector('.sign_up').textContent = 'Sign Up';
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
              sessionStorage.setItem('username', data.username); 
              sessionStorage.setItem('admin_id', data.admin_id); 
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
    document.querySelector('.sign_up').addEventListener('click', () => {
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
        document.querySelector('.sign_up').textContent = 'Log In';

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
            confirmInput.classList.add('login-form');

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
        document.querySelector('.sign_up').textContent = 'Sign Up';

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

  // window.addEventListener('DOMContentLoaded', async () => {
  //   const allTeams = await fetchAllTeams();

  //   const sportSelect = document.querySelector('.sport-type');
  //   const teamASelect = document.querySelector('.team-a');
  //   const teamBSelect = document.querySelector('.team-b');

  //   function updateTeamOptions(sportType) {
  //     const filtered = allTeams.filter(t => t.sport_type == sportType);
  //     teamASelect.innerHTML = '<option value="">請選擇隊伍</option>';
  //     teamBSelect.innerHTML = '<option value="">請選擇隊伍</option>';
  //     filtered.forEach(team => {
  //       const optA = document.createElement('option');
  //       optA.value = team.team_id;
  //       optA.textContent = team.team_name;
  //       teamASelect.appendChild(optA);

  //       const optB = document.createElement('option');
  //       optB.value = team.team_id;
  //       optB.textContent = team.team_name;
  //       teamBSelect.appendChild(optB);
  //     });
  //   }

  //   // 綁定 change 事件
  //   sportSelect.addEventListener('change', () => {
  //     const selectedSport = sportSelect.value;
  //     if (selectedSport) {
  //       updateTeamOptions(selectedSport);
  //     } else {
  //       teamASelect.innerHTML = '<option value="">請先選類別</option>';
  //       teamBSelect.innerHTML = '<option value="">請先選類別</option>';
  //     }
  //   });
  // });

  window.addEventListener('DOMContentLoaded', () => {
    const tbody = document.querySelector('#addTable tbody');
    tbody.innerHTML = '';   // 清除原本 HTML 裡寫死的那一列
    addRow(false); // 第一列不要 X   
  });

  async function fetchAllTeams() {
    try {
      const res = await fetch('/api/teams');
      return await res.json();
    } catch (e) {
      console.error('❌ 無法載入隊伍資料：', e);
      return [];
      }
    }


  // 通用畫面重置 function（不影響資料）
  function resetAddSection() {
      const tbody = document.querySelector('#addTable tbody');
      tbody.innerHTML = `
          <tr>
            <td>
            <select class="sport-type">
              <option value="">請選擇</option>
              <option value="1">NBA</option>
              <option value="2">F1</option>
              <option value="3">MLB</option>
              <option value="4">CPBL</option>
              <option value="5">BWF</option>
            </select>
          </td>
          <td>
            <select class="team-a">
              <option value="">請先選類別</option>
            </select>
          </td>
          <td>
            <select class="team-b">
              <option value="">請先選類別</option>
            </select>
          </td>
          <td>
            <input type="date" class="date-input">
          </td>
          <td><input type="text" placeholder="HH:MM" class="time-input"></td>
          <td><input type="text" placeholder="比分" class="point-input"></td>
        </tr>`;
      document.getElementById('addStatus').innerText = '';
      document.getElementById('addStatus').className = '';

  }
  

  async function addRow(showRemove = true) {
    const tbody = document.querySelector('#addTable tbody');
    const tr = document.createElement('tr');

    tr.innerHTML = `
      <td>
        <select class="sport-type">
          <option value="">請選擇</option>
          <option value="1">NBA</option>
          <option value="2">F1</option>
          <option value="3">MLB</option>
          <option value="4">CPBL</option>
          <option value="5">BWF</option>
        </select>
      </td>
      <td><select class="team-a"><option value="">請先選類別</option></select></td>
      <td><select class="team-b"><option value="">請先選類別</option></select></td>
      <td><input class="date-input" type="date" /></td>
      <td><input class="time-input" type="text" placeholder="HH:MM" /></td>
      <td><input class="point-input" type="text" placeholder="比分" /></td>
      ${showRemove ? `<td><button class="remove-btn">X</button></td>` : '<td></td>'}
    `;

    tbody.appendChild(tr);

    // 載入隊伍資料
    const sportSelect = tr.querySelector('.sport-type');
    const teamASelect = tr.querySelector('.team-a');
    const teamBSelect = tr.querySelector('.team-b');
    const allTeams = await fetchAllTeams();

    function updateTeamOptions(sportType) {
      const filtered = allTeams.filter(t => t.sport_type == sportType);
      teamASelect.innerHTML = '<option value="">請選擇隊伍</option>';
      teamBSelect.innerHTML = '<option value="">請選擇隊伍</option>';
      filtered.forEach(team => {
        const opt = new Option(team.team_name, team.team_id);
        teamASelect.appendChild(opt.cloneNode(true));
        teamBSelect.appendChild(opt.cloneNode(true));
      });
    }

    // 選擇隊伍時，檢查是否重複
    teamASelect.addEventListener('change', () => {
      if (teamASelect.value && teamASelect.value === teamBSelect.value) {
        alert('❌ 兩隊不能相同！');
        teamASelect.value = '';
      }
    });

    teamBSelect.addEventListener('change', () => {
      if (teamBSelect.value && teamASelect.value === teamBSelect.value) {
        alert('❌ 兩隊不能相同！');
        teamBSelect.value = '';
      }
    });

    sportSelect.addEventListener('change', () => {
      const selected = sportSelect.value;
      if (selected) updateTeamOptions(selected);
    });

    // 如果允許刪除，綁定 X 按鈕
    if (showRemove) {
      const removeBtn = tr.querySelector('.remove-btn');
      removeBtn.addEventListener('click', () => tr.remove());
    }
}



  async function submitAllMatches() {
    const rows = document.querySelectorAll('#addTable tbody tr');
    const matches = [];

    rows.forEach((row, i) => {
      const sport = row.querySelector('.sport-type')?.value;
      const teamA = row.querySelector('.team-a')?.value;
      const teamB = row.querySelector('.team-b')?.value;
      const date = row.querySelector('.date-input')?.value;
      const time = row.querySelector('.time-input')?.value.trim();
      let point = row.querySelector('.point-input')?.value.trim();
      point = point === "" ? null : point;

      console.log(`🧪 第 ${i + 1} 列：`, { sport, teamA, teamB, date, time, point });

      if (teamA && teamB && date && time) {
        matches.push({ type: sport, team_a: teamA, team_b: teamB, date, time, point });
      }
    });
    console.log("📦 準備送出資料：", matches);
    const res = await fetch(`/api/add-many`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ matches })
    });

    const data = await res.json();
    const status = document.getElementById('addStatus');
    if (data.success) {
    
      status.innerText = `✅ 新增 ${data.count} 筆資料完成`;
      status.className = 'success';

      const tbody = document.querySelector('#addTable tbody');
      tbody.innerHTML = '';
      addRow(false);
      
    } else {
      status.innerText = `❌ ${data.message}`;
      status.className = 'error';
    }

    setTimeout(() => {
      status.innerText = '';
      status.className = '';
    }, 3000); // 3 秒後自動清除
    
}


  function toggleEditForm(id, match, date, time) {
    const container = document.getElementById(`editForm_${id}`);

    // 已經有東西 → 就清空（關閉）
    if (container.innerHTML.trim() !== '') {
      container.innerHTML = '';
      return;
    }

    // 否則顯示編輯區
    showEditForm(id, match, date, time);
  }

   async function searchMatch() {
    const keyword = document.getElementById('searchInput').value.trim().toLowerCase();
    const resultDiv = document.getElementById('searchResult');
    resultDiv.innerHTML = '';
    if (!keyword) return;

    try {
        const res = await fetch(`/api/search?keyword=${encodeURIComponent(keyword)}`);
        const data = await res.json();
        

        // 安全檢查：避免 matches 為 undefined
        if (!data.matches || data.matches.length === 0) {
            resultDiv.innerHTML = '<p style="color: red;">❌ 沒有找到符合的比賽資料。</p>';
            return;
        }

        data.matches.forEach(m => {
            const div = document.createElement('div');
            div.className = 'match-card';
            div.id = `card_${m.id}`;  

            // 上方資訊區塊
            const infoWrapper = document.createElement('div');
            infoWrapper.className = 'info-wrapper';

            const title = document.createElement('strong');
            title.className = 'match-title';
            title.textContent = m.match;

            const datetime = document.createElement('span');
            datetime.className = 'match-datetime';
            datetime.textContent = ` | ${m.date} ${m.time}`;

            const point = document.createElement('span');
            point.className = 'match-point';
            point.textContent = m.point ? ` | 比數：${m.point}` : `| 比數：尚未開始`;

            infoWrapper.appendChild(title);
            infoWrapper.appendChild(datetime);
            infoWrapper.appendChild(point);

            // 下方按鈕區塊
            const buttonWrapper = document.createElement('div');
            buttonWrapper.className = 'button-wrapper';

            const editBtn = document.createElement('button');
            editBtn.textContent = '修改';
            editBtn.addEventListener('click', () => {
                toggleEditForm(m.id, m.match, m.date, m.time);
            });

            const deleteBtn = document.createElement('button');
            deleteBtn.textContent = '刪除';
            deleteBtn.classList.add('delete-btn');
            deleteBtn.addEventListener('click', () => confirmDelete(m.id));

            buttonWrapper.appendChild(editBtn);
            buttonWrapper.appendChild(deleteBtn);

            // 加到主容器
            div.appendChild(infoWrapper);
            div.appendChild(buttonWrapper);

            const editDiv = document.createElement('div');
            editDiv.id = `editForm_${m.id}`;
            editDiv.className = 'edit-form';
            editDiv.style.marginTop = '0.5rem';
            editDiv.style.marginBottom = '5%';

            div.appendChild(editDiv);
            resultDiv.appendChild(div);
        });

    } catch (error) {
        resultDiv.innerHTML = `<p style="color: red;">❌ 發生錯誤：${error.message}</p>`;
        console.error("❌ 搜尋錯誤：", error);
    }
  }

  async function showEditForm(id, match, date, time) {
    const container = document.getElementById(`editForm_${id}`);
    container.innerHTML = '⏳ 載入中...';

    const res = await fetch(`/api/match/${id}`);
    const data = await res.json();

    if (!data.success) {
      container.innerHTML = '❌ 無法載入比賽資料';
      return;
    }

    const matchData = data.match;
    const teamRes = await fetch("/api/teams");
    const allTeams = await teamRes.json();

    const filteredTeams = allTeams.filter(t => Number(t.sport_type) === Number(matchData.sport_type));

    const selectTeamA = document.createElement("select");
    const selectTeamB = document.createElement("select");

    filteredTeams.forEach(t => {
      const optionA = document.createElement("option");
      optionA.value = t.team_id;
      optionA.textContent = t.team_name;
      if (t.team_id == matchData.team_a) optionA.selected = true;
      selectTeamA.appendChild(optionA);

      const optionB = document.createElement("option");
      optionB.value = t.team_id;
      optionB.textContent = t.team_name;
      if (t.team_id == matchData.team_b) optionB.selected = true;
      selectTeamB.appendChild(optionB);
    });

      const dateInput = document.createElement("input");
      dateInput.type = "text";
      dateInput.value = matchData.date;

      const timeInput = document.createElement("input");
      timeInput.type = "text";
      timeInput.value = matchData.time;

      const pointInput = document.createElement("input");
      pointInput.type = "text";
      pointInput.placeholder = "比分（可留空）";
      pointInput.value = matchData.point || '';

      const saveBtn = document.createElement("button");
      saveBtn.textContent = "儲存";
      saveBtn.addEventListener("click", async () => {
        const payload = {
          team_a: selectTeamA.value,
          team_b: selectTeamB.value,
          date: dateInput.value,
          time: timeInput.value,
          point: pointInput.value
        };

        const editRes = await fetch(`/api/edit/${id}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        const result = await editRes.json();
        if (result.success) {
          alert("✅ 修改成功！");

          const card = document.getElementById(`card_${id}`);
          if (card) {
            const newTitle = `${selectTeamA.selectedOptions[0].textContent} vs ${selectTeamB.selectedOptions[0].textContent}`;
            const titleEl = card.querySelector(".match-title");
            const datetimeEl = card.querySelector(".match-datetime");
            const pointEl = card.querySelector(".match-point");

            if (titleEl) titleEl.textContent = newTitle;
            if (datetimeEl) datetimeEl.textContent = ` | ${dateInput.value} ${timeInput.value}`;
            if (pointEl) {
              pointEl.textContent = ` | 比數：${pointInput.value ? pointInput.value : "尚未開始"}`;
            } else {
              const newPoint = document.createElement("span");
              newPoint.className = "match-point";
              newPoint.textContent = ` | 比數：${pointInput.value ? pointInput.value : "尚未開始"}`;
              card.querySelector(".info-wrapper").appendChild(newPoint);
            }
          }

          container.innerHTML = '';

          container.style.display = "none";
          setTimeout(() => { container.innerHTML = ''; container.style.display = ""; }, 300);

        } else {
          alert("❌ 修改失敗：" + result.message);
        }
      });

  container.innerHTML = '';
  container.appendChild(selectTeamA);
  container.appendChild(document.createTextNode(" vs "));
  container.appendChild(selectTeamB);
  container.appendChild(document.createElement("br"));
  container.appendChild(dateInput);
  container.appendChild(timeInput);
  container.appendChild(pointInput);
  container.appendChild(saveBtn);
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
      card.querySelector('.match-datetime').innerText = ` | ${date} ${time}`;
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
    

    function getCurrentSQLDatetime() {
      const now = new Date();
      // 台灣時間 = 加上 8 小時
      const taiwan = new Date(now.getTime() + 8 * 60 * 60 * 1000);

      const pad = n => n.toString().padStart(2, '0');
      const y = taiwan.getUTCFullYear();
      const m = pad(taiwan.getUTCMonth() + 1);
      const d = pad(taiwan.getUTCDate());
      const h = pad(taiwan.getUTCHours());
      const min = pad(taiwan.getUTCMinutes());
      const s = pad(taiwan.getUTCSeconds());

      return `${y}-${m}-${d} ${h}:${min}:${s}`;
  }

    function toSQLDatetime(datetimeStr) {
      const date = new Date(datetimeStr);
      if (isNaN(date.getTime())) {
        console.warn("⚠️ 無效時間格式：", datetimeStr);
        return "Invalid Date";
      }
      const iso = date.toISOString();
      return iso.slice(0, 19).replace('T', ' ');
    }



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
      // const author = document.getElementById("authorInput").value.trim();
      const datetime = document.getElementById("announceDate").innerText;
      
      const status = document.getElementById("announceStatus");
      

      //抓管理者帳號
      // const author = document.body.dataset.username;

      //抓管理者ID
      const admin_id = document.body.dataset.adminId;
      // const datetime = getCurrentSQLDatetime();
      

      if (!content) {
          status.innerText = "❌ 請輸入公告內容";
          status.style.color = "red";
          return;
      }

      const res = await fetch("/api/announce", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ content, admin_id, datetime})
      });

      console.log(datetime);

      const result = await res.json();
      if (result.success) {
          status.innerText = "✅ 公告發佈成功！";
          status.style.color = "green";
          document.getElementById("announcementInput").value = "";

          // 展開區塊 + 立即更新歷史紀錄
          document.getElementById("historyArea").style.display = "block";
          await loadHistory();
      } else {
          status.innerText = "❌ 發佈失敗";
          status.style.color = "red";
      }

      //3 秒後自動清除提示
      setTimeout(() => {
          status.innerText = "";
      }, 3000);
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

      const CURRENT_ADMIN_ID = document.body.dataset.adminId;

      data.sort((a, b) => new Date(b.a_datetime) - new Date(a.a_datetime)).forEach((ann) => {
        
        sqlDateTime = toSQLDatetime(ann.a_datetime);

        const div = document.createElement('div');
        div.className = 'announcement';
        div.dataset.adminId = ann.admin_id;  // ⬅️ 加這行
        
        //判斷是否為最高管理員
        const is_top = document.body.dataset.isTop === "True";


        //對應admin_id 或 最高管理員 可編修
        const canEdit = ((String(ann.admin_id) === String(CURRENT_ADMIN_ID)) || is_top);
        
        div.innerHTML = `
            <p class="content">📣 ${ann.content}</p>
            <input class="editInput" type="text" style="display:none; width: 90%;" value="${ann.content}">
            <hr>
            <div class="meta">
              🕒 ${sqlDateTime} ｜ 👤 ${ann.admin_name}
              ${canEdit ? `
                <button class="EditAnsBtn" data-datetime="${sqlDateTime}" style="margin: 0.3rem;">修改</button>
                <button class="SaveAnsBtn" data-datetime="${sqlDateTime}" style="display:none; margin: 0.3rem;">儲存</button>
                <button class="DeleteAnsBtn" data-datetime="${sqlDateTime}" style="margin: 0.3rem;">刪除</button>
              ` : ''}
            </div>
        `;
          area.appendChild(div);
      });
    }


    //刪除公告
    async function deleteAnnouncement(a_datetime, admin_id) {
      
      const isTop = document.body.dataset.isTop === "True";
      console.log(a_datetime);
      console.log(isTop);
      const res = await fetch(`/api/announce/${encodeURIComponent(a_datetime)}?admin_id=${admin_id}&is_top=${isTop}`, {
        method: 'DELETE'
      });

      const result = await res.json();
      if (result.success) {
        alert("✅ 已刪除公告");
        loadHistory();
      } else {
        alert("❌ 刪除失敗：" + result.message);
      }
    }

    

    //更新公告
    async function updateAnnouncement(a_datetime, original_admin_id, new_admin_id, newContent, btnEl) {
      const currentDatetime = getCurrentSQLDatetime();  // ⬅️ 補上這行

      const res = await fetch(`/api/announce/${a_datetime}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content: newContent,
          admin_id: new_admin_id,         // 要換成誰的 ID
          original_admin_id: original_admin_id, // 主鍵用
          new_datetime: currentDatetime
        })
      });

      const result = await res.json();
      if (result.success) {
        alert("✅ 公告已更新");

        const card = btnEl.closest('.announcement');
        const contentP = card.querySelector('.content');
        const input = card.querySelector('.editInput');
        const datetimeEl = card.querySelector('.meta');

        contentP.textContent = `📣 ${newContent}`;
        input.style.display = 'none';
        contentP.style.display = 'block';

        card.querySelector('.EditAnsBtn').dataset.datetime = currentDatetime;
        card.querySelector('.SaveAnsBtn').dataset.datetime = currentDatetime;
        card.querySelector('.DeleteAnsBtn').dataset.datetime = currentDatetime;

        const parts = datetimeEl.innerHTML.split("｜");
        datetimeEl.innerHTML = `🕒 ${currentDatetime} ｜ ${parts[1]}`;

        loadHistory();
      } else {
        alert("❌ 更新失敗：" + result.message);
      }
    }
 
      //按鈕事件綁定
      document.getElementById('PostBtn').addEventListener('click', submitAnnouncement);
      document.getElementById('ShowAndHideBtn').addEventListener('click', toggleHistory);
      //用事件代理監聽刪除按鈕點擊
      document.getElementById('historyArea').addEventListener('click', function(e) {

        if (e.target.classList.contains('DeleteAnsBtn')) {
          const a_datetime = e.target.dataset.datetime;
          const admin_id = document.body.dataset.adminId;
          deleteAnnouncement(a_datetime, admin_id);
        }

        if (e.target.classList.contains('EditAnsBtn')) {
          const card = e.target.closest('.announcement');
          const contentP = card.querySelector('.content');
          const input = card.querySelector('.editInput');
          const saveBtn = card.querySelector('.SaveAnsBtn');

          // 切換顯示模式
          contentP.style.display = 'none';
          input.style.display = 'inline-block';
          e.target.style.display = 'none';
          saveBtn.style.display = 'inline-block';
        }

        if (e.target.classList.contains('SaveAnsBtn')) {
          const card = e.target.closest('.announcement');
          const input = card.querySelector('.editInput');
          const newContent = input.value.trim();

          if (!newContent) {
            alert("❌ 公告不能為空");
            return;
          }

          const a_datetime = e.target.dataset.datetime;
          const original_admin_id = card.dataset.adminId;  // ⬅️ 加這行取原本公告作者 ID
          const current_admin_id = document.body.dataset.adminId;  // ⬅️ 自己的 ID（可能是最高管理員）

          updateAnnouncement(a_datetime, original_admin_id, current_admin_id, newContent, e.target);
        }
  });
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

}else if(page === 'feedback'){

  const is_top = document.body.dataset.isTop === "True";
  console.log(is_top);

  document.addEventListener('DOMContentLoaded', () => {
    // 修正你的四個 list 的 id
    const doneList = document.getElementById('done-list');
    const processingList = document.getElementById('processing-list');
    const unprocessedList = document.getElementById('unprocessed-list');
    const rejectedList = document.getElementById('rejected-list');

    // 先清空所有區塊
    doneList.innerHTML = '';
    processingList.innerHTML = '';
    unprocessedList.innerHTML = '';
    rejectedList.innerHTML = '';

    // 讀取 API 資料
    fetch('/api/feedback/all')
      .then(res => res.json())
      .then(data => {
        // 若回傳不是陣列，代表後端錯了
        if (!Array.isArray(data)) {
          console.error("⚠️ 回傳不是陣列：", data);
          alert("❌ 無法取得回饋資料，請查看後端錯誤訊息！");
          return;
        }

        data.forEach(fb => {
          const card = createFeedbackCard(fb.user_id, fb.send_date, fb);
          if (fb.f_status === '已處理') {
              doneList.appendChild(card);
          } else if (fb.f_status === '處理中') {
              processingList.appendChild(card);
          } else if (fb.f_status === '未處理') {
              unprocessedList.appendChild(card);
          } else if (fb.f_status === '不採納') {
              rejectedList.appendChild(card);
          }
        });
      });



    function createFeedbackCard(uid, date, fb) {
        const typemap = {1:"NBA", 2:"F1", 3:"MLB", 4:"CPBL", 5:"BWF"};

        const card = document.createElement('div');
        
        card.className = 'feedback-card';
        card.style.cursor = 'pointer';

        const title = document.createElement('div');
        title.className = 'feedback-title';
        title.innerHTML = `<strong>使用者 ${uid}</strong> | 💪 ${typemap[fb.f_type]} | 🗓️ ${date} ${fb.f_time}`;

        const detail = document.createElement('div');
        detail.className = 'feedback-detail';
        detail.style.display = 'none';

        const p = document.createElement('p');
        p.textContent = `✏️ ${fb.content}`;
        detail.appendChild(p);

        const status = document.createElement('div');
        status.innerHTML = `❓ 狀態：<span class="status-text">${fb.f_status}</span>`;
        detail.appendChild(status);

        if (fb.admin_id != "") {
            const admin = document.createElement('div');
            const adminname = fb.admin_name === null || fb.admin_name === "null" ? "/" : fb.admin_name;
            admin.innerHTML = `👤 管理者：<span>${adminname}</span>`;
            detail.appendChild(admin);
        }
        if (fb.reply_date || fb.reply_time) {
            const replyTime = document.createElement('div');
            replyTime.innerHTML = `📅 回覆時間：<span>${fb.reply_date} ${fb.reply_time}</span>`;
            detail.appendChild(replyTime);
        }

        // 顯示回覆內容（reply 或 reason）
        if ((fb.f_status === '已處理' || fb.f_status === '不採納')) {
            const reply = document.createElement('div');
            reply.innerHTML = `💬 回覆內容：<span>${fb.reply || fb.reason || '（無內容）'}</span>`;
            detail.appendChild(reply);
        }

        // 🔘 認領按鈕：僅在 admin 欄位為空且狀態為未處理時顯示
        if (!fb.admin_id && fb.f_status === '未處理') {
            const claimBtn = document.createElement('button');
            claimBtn.textContent = '認領';
            claimBtn.className = 'claim-btn';
            claimBtn.addEventListener('click', async () => {
                const res = await fetch(`/api/feedback/${uid}/${date}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        admin_id: document.body.dataset.adminId,
                        status: '處理中',
                        time: fb.f_time
                    })
                });
                const result = await res.json();
                if (result.success) {
                    alert("✅ 已成功認領並轉為處理中");
                    location.reload();
                } else {
                    alert("❌ 認領失敗：" + result.message);
                }
            });
            detail.appendChild(claimBtn);
        }
        
        console.log(is_top);
        // ✅ 最高管理員 或「處理中」且 admin 為當前使用者才顯示可編輯區塊（可提交為已處理/不採納）
        if ((fb.f_status === '處理中' && (is_top || String(fb.admin_id) === String(document.body.dataset.adminId)))) {
            
            const replyInput = document.createElement('textarea');
            replyInput.className = 'reply-textarea';
            replyInput.placeholder = '輸入回覆內容（可留空）';
            replyInput.value = fb.reason || "";
            detail.appendChild(replyInput);

            const doneBtn = document.createElement('button');
            doneBtn.textContent = '✅ 標記為已處理';
            doneBtn.className = 'reply-btn';
            doneBtn.addEventListener('click', async () => {
                await submitFinalStatus('已處理');
            });
            detail.appendChild(doneBtn);

            const rejectBtn = document.createElement('button');
            rejectBtn.textContent = '❌ 不採納';
            rejectBtn.className = 'reply-btn';
            rejectBtn.addEventListener('click', async () => {
                await submitFinalStatus('不採納');
            });
            detail.appendChild(rejectBtn);

            async function submitFinalStatus(finalStatus) {
                const updatedReason = replyInput.value.trim();
                const now = new Date();
                const dateStr = `${now.getFullYear()}-${(now.getMonth()+1).toString().padStart(2, '0')}-${now.getDate().toString().padStart(2, '0')}`;
                const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
                console.log(dateStr);
                console.log(timeStr);
                const payload = {
                    time: fb.f_time,
                    status: finalStatus,
                    admin_id: document.body.dataset.adminId,
                    reply_date: dateStr,
                    reply_time: timeStr,
                    reason: updatedReason
                };
              
            
                const res = await fetch(`/api/feedback/${uid}/${date}`, {
                    method: 'POST',
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                const result = await res.json();
                if (result.success) {
                    alert(`✅ 已標記為 ${finalStatus}`);
                    location.reload();
                } else {
                    alert("❌ 修改失敗：" + result.message);
                }
            }
        }

        title.addEventListener('click', () => {
          // 關閉其他展開的卡片
          document.querySelectorAll('.feedback-detail').forEach(otherDetail => {
              if (otherDetail !== detail) {
                  otherDetail.style.display = 'none';
              }
          });

          // 切換當前卡片
          if (detail.style.display === 'none') {
              detail.style.display = 'block';
          } else {
              detail.style.display = 'none';
          }
      });

        card.appendChild(title);
        card.appendChild(detail);
        return card;
    }


  });

  document.querySelectorAll('.section-title').forEach(title => {
      title.addEventListener('click', () => {
          const currentList = title.nextElementSibling;  // 找到對應的 list

          // 先收起其他所有 list
          document.querySelectorAll('.feedback-list').forEach(list => {
              if (list !== currentList) {
                  list.style.display = 'none';
              }
          });

          if (currentList.style.display === 'none') {
              currentList.style.display = 'block';
          } else {
              currentList.style.display = 'none';  
          }
      });
  });
}