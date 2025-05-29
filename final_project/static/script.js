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
if(page === 'foradmin'){
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
  
  let allTeams = [];  // 全域隊伍資料
  
  window.addEventListener('DOMContentLoaded', async () => {
    const tbody = document.querySelector('#addTable tbody');
    tbody.innerHTML = '';

    await fetchAllTeams();


    await populateSportOptions();
    bindSearchEvents();
    addRow(false); // 第一筆不要 X
  });

  async function fetchAllTeams(sportType = "") {
    try {
      const url = sportType === "2" ? `/api/teams?sport=2` : `/api/teams`;
      const res = await fetch(url);
      allTeams = await res.json(); // 存入全域
      return allTeams;
    } catch (e) {
      console.error('❌ 無法載入隊伍資料：', e);
      allTeams = [];
      return [];
    }
  }


  async function populateSportOptions() {
    const sportSelect = document.getElementById("search-sport");
    sportSelect.innerHTML = `
      <option value="">請選擇</option>
      <option value="1">NBA</option>
      <option value="2">F1</option>
      <option value="3">MLB</option>
      <option value="4">CPBL</option>
      <option value="5">BWF</option>
    `;

    sportSelect.addEventListener("change", async () => {
      const sportType = sportSelect.value;
      const teamASelect = document.getElementById("search-team-a");
      const teamBSelect = document.getElementById("search-team-b");

      document.getElementById("searchResult").innerHTML = "";
      
      if (!sportType) {
        teamASelect.innerHTML = '<option value="">請先選擇運動種類</option>';
        teamBSelect.innerHTML = '<option value="">請先選擇運動種類</option>';
        teamASelect.disabled = true;
        teamBSelect.disabled = true;
        teamBSelect.style.display = ""; // 顯示回來
        return;
      }

      const allTeams = await fetchAllTeams(sportType);
      const filtered = allTeams.filter(t => t.sport_type == sportType);

      teamASelect.innerHTML = '<option value="">(可選)</option>';
      filtered.forEach(t => {
        const opt = new Option(t.team_name, t.team_id);
        teamASelect.appendChild(opt);
      });

      teamASelect.disabled = false;

      // ✅ F1 → 隱藏 teamB
      if (sportType === "2") {
        teamBSelect.innerHTML = "";
        teamBSelect.disabled = true;
        teamBSelect.style.display = "none";
      } else {
        teamBSelect.innerHTML = '<option value="">(可選)</option>';
        filtered.forEach(t => {
          const opt = new Option(t.team_name, t.team_id);
          teamBSelect.appendChild(opt);
        });
        teamBSelect.disabled = false;
        teamBSelect.style.display = "";
      }
    });

  }

  function generateTimeOptions() {
    let options = '<option value="">請選擇時間</option>';
    for (let hour = 0; hour < 24; hour++) {
      for (let min = 0; min < 60; min += 5) {
        const timeStr = `${String(hour).padStart(2, '0')}:${String(min).padStart(2, '0')}`;
        options += `<option value="${timeStr}">${timeStr}</option>`;
      }
    }
    return options;
  }

  function bindSearchEvents() {
    const btn = document.getElementById("SearchBtn");

    const sport_name = {
      1 : "NBA",
      2 : "F1",
      3 : "MLB",
      4 : "CPBL",
      5 : "BWF"
    }
    btn.addEventListener("click", async () => {
      const sport = document.getElementById("search-sport").value;
      const date = document.getElementById("search-date").value;
      const teamA = document.getElementById("search-team-a").value;
      const teamB = document.getElementById("search-team-b").value;

      if ((teamA || teamB) && !sport) {
        alert("❌ 若要選擇比賽隊伍，請先選擇運動類別");
        return;
      }

      const params = new URLSearchParams();
      if (sport) params.append("sport", sport);
      if (date) params.append("date", date);
      if (sport === "2") {
        if (teamA) params.append("game_no", teamA);  // 改成 game_no
      } else {
        if (teamA) params.append("team_a", teamA);
        if (teamB) params.append("team_b", teamB);
      }

      const result = document.getElementById("searchResult");

      const res = await fetch(`/api/search_match_advanced?${params}`);

      if (!res.ok) {
        const errorData = await res.json();
        alert(`❌ 查詢錯誤：${errorData.error || "未知錯誤"}`);
        return;
      }

      const data = await res.json(); // ✅ 放在確認 ok 後再取出

      result.innerHTML = "";
      if (!data.matches || data.matches.length === 0) {
        result.innerHTML = '<p>查無比賽資料</p>';
        return;
      }

      result.innerHTML = `<p>共找到 ${data.matches.length} 筆比賽：</p>`;
      const isF1 = sport === "2";

      data.matches.forEach(m => {
        const formattedDate = new Date(m.date).toISOString().slice(0, 10);
        const matchTitle = isF1
          ? m.match_name
          : m.match || `${m.team_a_name} vs ${m.team_b_name}`;

        const platforms = m.platforms && m.platforms.length > 0
          ? m.platforms.join('、')
          : '無';
        
        if(m.type === 2){
          result.innerHTML += `
            <div class="match-card" id="card_${m.game_no}" style="margin-bottom: 1rem;">
              <strong>【${sport_name[m.type]}】 ${matchTitle}</strong><br>
              比賽類型 : ${m.match_type}<br>
              日期時間 : ${formattedDate} ${m.time}<br>
              播放平台：${platforms}<br>
              <div class="button-wrapper" style="margin-top: 0.5rem;">
                <button onclick="toggleEditForm(${m.game_no}, \`${matchTitle}\`, \`${formattedDate}\`, \`${m.time}\`)">修改</button>
                <button class="delete-btn" data-id="${m.game_no}">刪除</button>
              </div>
              <div id="editForm_${m.game_no}" class="edit-form"></div>
            </div>
          `;
        }else{
          result.innerHTML += `
          <div class="match-card" id="card_${m.game_no}" style="margin-bottom: 1rem;">
            <strong>【${sport_name[m.type]}】 ${matchTitle}</strong><br>
            日期時間 : ${formattedDate} ${m.time}<br>
            比分：${m.point || '尚未公布'}<br>
            播放平台：${platforms}<br>
            <div class="button-wrapper" style="margin-top: 0.5rem;">
              <button onclick="toggleEditForm(${m.game_no}, \`${matchTitle}\`, \`${formattedDate}\`, \`${m.time}\`)">修改</button>
              <button class="delete-btn" data-id="${m.game_no}">刪除</button>
            </div>
            <div id="editForm_${m.game_no}" class="edit-form"></div>
          </div>
        `;
        }
        
      });


      setTimeout(() => {
        document.querySelectorAll(".edit-btn").forEach(btn => {
          btn.addEventListener("click", () => {
            const id = btn.dataset.id;
            const title = btn.dataset.title;
            const date = btn.dataset.date;
            const time = btn.dataset.time;
            toggleEditForm(id, title, date, time);
          });
        });

        document.querySelectorAll(".delete-btn").forEach(btn => {
          btn.addEventListener("click", () => {
            const id = btn.dataset.id;
            confirmDelete(id);
          });
        });
      }, 0);

    });
  }


  function checkDuplicatePlayers(tr) {
    const selects = tr.querySelectorAll('.bwf-players select.player-id');
    const selectedValues = [];

    selects.forEach(sel => {
      const val = sel.value;
      if (val && selectedValues.includes(val)) {
        alert("❌ 不能選擇重複的選手！");
        sel.value = "";  // 清空該欄位
      } else if (val) {
        selectedValues.push(val);
      }
    });
  }


  async function addRow(showRemove = true) {
    const tbody = document.querySelector('#addTable tbody');
    const tr = document.createElement('tr');

    tr.innerHTML = `
      <td data-label="運動類別">
        <select class="sport-type">
          <option value="">請選擇</option>
          <option value="1">NBA</option>
          <option value="2">F1</option>
          <option value="3">MLB</option>
          <option value="4">CPBL</option>
          <option value="5">BWF</option>
        </select>
      </td>
      <td colspan="2" data-label="隊伍／名稱選擇／比賽類型">
        <div class="team-selects">
          <select class="team-a"><option value="">請先選類別</option></select>
          <select class="team-b"><option value="">請先選類別</option></select>
        </div>
        <input type="text" class="match-name" placeholder="請輸入比賽名稱" style="display: none; width: 100%;" />
        <input type="text" class="match-type" placeholder="請輸入比賽類型（如 Race）" style="display: none; width: 100%; margin-top: 0.5em;" />
        <div class="bwf-players" style="display: none; margin-top: 0.5em;">
          <div style="margin-bottom: 0.5em;">
            <label>隊伍 A：</label><br/>
            <select class="player-id team-a-player-select"><option value="">選手1</option></select><br/>
            <select class="player-id team-a-player-select"><option value="">選手3 (可選)</option></select>
          </div>
          <div>
            <label>隊伍 B：</label><br/>
            <select class="player-id team-b-player-select"><option value="">選手2</option></select><br/>
            <select class="player-id team-b-player-select"><option value="">選手4 (可選)</option></select>
          </div>
        </div>
      </td>
      <td data-label="日期"><input type="date" class="date-input" /></td>
      <td data-label="時間">
        <select class="time-input">
          ${generateTimeOptions()}
        </select>
      </td>
      <td data-label="比分"><input type="text" class="point-input" placeholder="比分" /></td>
      <td data-label="播放平台">
        <div class="platform-checkboxes" style="display: flex; flex-direction: column; gap: 0.25em;">載入中...</div>
      </td>
      ${showRemove ? `<td><button class="remove-btn">X</button></td>` : `<td></td>`}
    `;

    tbody.appendChild(tr);

    const platformContainer = tr.querySelector('.platform-checkboxes');

// ✅ 容器樣式（手機優化、保證靠左）
Object.assign(platformContainer.style, {
  display: "block",
  width: "100%",
  maxHeight: "130px",
  overflowY: "auto",
  border: "1px solid #ccc",
  borderRadius: "6px",
  padding: "8px",
  backgroundColor: "#fff",
  boxSizing: "border-box",
  WebkitOverflowScrolling: "touch",
  fontSize: "16px",
  lineHeight: "1.8",
  textAlign: "left"         // ✅ 容器內部整體靠左
});

try {
  const res = await fetch('/api/platforms');
  const platforms = await res.json();
  platformContainer.innerHTML = '';

  platforms.forEach(p => {
    const wrapper = document.createElement("label");
    wrapper.style.display = "flex";
    wrapper.style.alignItems = "center";
    wrapper.style.justifyContent = "flex-start"; // ✅ 內容靠左對齊
    wrapper.style.gap = "0.6em";
    wrapper.style.marginBottom = "4px";
    wrapper.style.width = "100%";
    wrapper.style.cursor = "pointer";
    wrapper.style.textAlign = "left";           // ✅ 每一行都靠左
    wrapper.style.boxSizing = "border-box";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = p.platform_id;
    checkbox.classList.add("platform-checkbox");
    checkbox.style.width = "18px";
    checkbox.style.height = "18px";
    checkbox.style.margin = "0";

    const span = document.createElement("span");
    span.textContent = p.name;
    span.style.flex = "1";
    span.style.wordBreak = "keep-all";
    span.style.fontSize = "1em";
    span.style.lineHeight = "1.6";
    span.style.textAlign = "left";              // ✅ 文本內容靠左

    wrapper.appendChild(checkbox);
    wrapper.appendChild(span);
    platformContainer.appendChild(wrapper);
  });
} catch (err) {
  console.error("❌ 無法載入平台資料", err);
  platformContainer.innerText = "❌ 載入失敗";
}

    const sportSelect = tr.querySelector('.sport-type');
    const teamASelect = tr.querySelector('.team-a');
    const teamBSelect = tr.querySelector('.team-b');
    const matchNameInput = tr.querySelector('.match-name');
    const teamSelects = tr.querySelector('.team-selects');
    const bwfPlayers = tr.querySelector('.bwf-players');

    async function updateTeamOptions(sportType) {
      const allTeams = await fetchAllTeams(sportType);
      const filtered = allTeams.filter(t => t.sport_type == sportType);

      teamASelect.innerHTML = '<option value="">請選擇隊伍</option>';
      teamBSelect.innerHTML = '<option value="">請選擇隊伍</option>';

      filtered.forEach(team => {
        const opt = new Option(team.team_name, team.team_id);
        teamASelect.appendChild(opt.cloneNode(true));
        teamBSelect.appendChild(opt.cloneNode(true));
      });
    }

    sportSelect.addEventListener('change', () => {
      const selected = sportSelect.value;
      const matchTypeInput = tr.querySelector('.match-type');
      const pointInput = tr.querySelector('.point-input');

      if (selected === "2") {
        teamSelects.style.display = "none";
        matchNameInput.style.display = "block";
        matchTypeInput.style.display = "block";     // 顯示比賽類型
        pointInput.parentElement.style.display = "none";  // 隱藏比分
        bwfPlayers.style.display = "none";
      } else if (selected === "5") {
        teamSelects.style.display = "flex";
        matchNameInput.style.display = "none";
        matchTypeInput.style.display = "none";
        pointInput.parentElement.style.display = "";      // 顯示比分
        bwfPlayers.style.display = "block";
        updateTeamOptions(selected);
      } else {
        teamSelects.style.display = "flex";
        matchNameInput.style.display = "none";
        matchTypeInput.style.display = "none";
        pointInput.parentElement.style.display = "";      // 顯示比分
        bwfPlayers.style.display = "none";
        updateTeamOptions(selected);
      }
    });

    teamASelect.addEventListener('change', () => {
      if (sportSelect.value !== "5" && teamASelect.value === teamBSelect.value) {
        alert('❌ 兩隊不能相同！');
        teamASelect.value = '';
        return;
      }
      if (sportSelect.value === "5") {
        getBWF_Players(teamASelect.value, tr, 'A');
      }
    });

    teamBSelect.addEventListener('change', () => {
      if (teamBSelect.value === teamASelect.value) {
        alert('❌ 兩隊不能相同！');
        teamBSelect.value = '';
        return;
      }
      if (sportSelect.value === "5") {
        getBWF_Players(teamBSelect.value, tr, 'B');
      }
    });

    if (showRemove) {
      const removeBtn = tr.querySelector('.remove-btn');
      removeBtn.addEventListener('click', () => tr.remove());
    }
  }



  async function getBWF_Players(teamId, tr, teamLabel) {
    if (!teamId) return;

    try {
      const res = await fetch(`/api/get_bwf_players?team_id=${teamId}`);
      const players = await res.json();

      // 只抓對應那一隊的選手選單
      const selector = teamLabel === 'A'
        ? '.bwf-players select.team-a-player-select'
        : '.bwf-players select.team-b-player-select';

      const playerSelects = tr.querySelectorAll(selector);

      playerSelects.forEach(select => {
        select.innerHTML = `<option value="">請選擇選手</option>`;
        players.forEach(p => {
          const opt = new Option(p.name, p.player_id);
          select.appendChild(opt);
        });

        // ✅ 加入重複選手檢查
        select.addEventListener('change', () => {
          const allSelects = tr.querySelectorAll('.bwf-players select.player-id');
          const selected = [];

          allSelects.forEach(sel => {
            const val = sel.value;
            if (val) {
              if (selected.includes(val)) {
                alert('❌ 不能選擇重複的選手');
                sel.value = '';
              } else {
                selected.push(val);
              }
            }
          });
        });
      });
    } catch (err) {
      console.error('❌ 無法載入選手名單', err);
    }
  }
  

  async function submitAllMatches() {
    const rows = document.querySelectorAll('#addTable tbody tr');
    const matches = [];

    rows.forEach((row) => {
      const sport = row.querySelector('.sport-type')?.value;
      const teamA = row.querySelector('.team-a')?.value;
      const teamB = row.querySelector('.team-b')?.value;
      const date = row.querySelector('.date-input')?.value;
      const time = row.querySelector('.time-input')?.value.trim();
      let point = row.querySelector('.point-input')?.value.trim();
      const matchType = row.querySelector('.match-type')?.value.trim();

      point = point === "" ? null : point;
      const matchName = row.querySelector('.match-name')?.value.trim();
      const selectedPlatforms = Array.from(row.querySelectorAll('.platform-checkbox:checked')).map(cb => Number(cb.value));

      if (sport === "2") {
        if (matchName && date && time && matchType) {
          matches.push({ type: sport, match_name: matchName, date, time, point: null, platforms: selectedPlatforms, match_type : matchType});
        }
      } else if (sport === "5") {
        const teamAPlayers = Array.from(row.querySelectorAll('.team-a-player-select'))
          .map(sel => sel.value.trim()).filter(pid => pid !== "");
        const teamBPlayers = Array.from(row.querySelectorAll('.team-b-player-select'))
          .map(sel => sel.value.trim()).filter(pid => pid !== "");

        const selectedPlayers = [...teamAPlayers, ...teamBPlayers];
        if (teamA && teamB && date && time && selectedPlayers.length >= 2 && selectedPlayers.length <= 4) {
          if (teamAPlayers.length !== teamBPlayers.length) {
            alert(`❌ 隊伍 A 與 B 選手數量需一致（目前是 ${teamAPlayers.length} vs ${teamBPlayers.length}）`);
            return;
          }
          const match = {
            type: sport,
            team_a: teamA,
            team_b: teamB,
            date,
            time,
            point,
            platforms: selectedPlatforms
          };
          selectedPlayers.forEach((pid, idx) => {
            match[`player_${idx + 1}`] = pid;
          });
          matches.push(match);
        }
      } else {
        if (teamA && teamB && date && time) {
          matches.push({ type: sport, team_a: teamA, team_b: teamB, date, time, point, platforms: selectedPlatforms });
        }
      }
    });

    const res = await fetch(`/api/add-many`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ matches })
    });

    const data = await res.json();
    const status = document.getElementById('addStatus');
    if (data.success) {
      alert(`新增 ${data.count} 筆資料成功！`);
      status.innerText = `✅ 新增 ${data.count} 筆資料完成`;
      status.className = 'success';
      const tbody = document.querySelector('#addTable tbody');
      tbody.innerHTML = '';
      addRow(false);
    } else {
      alert(`❌ ${data.message}`);
      status.innerText = `❌ ${data.message}`;
      status.className = 'error';
    }

    setTimeout(() => {
      status.innerText = '';
      status.className = '';
    }, 3000);
  }


  async function searchMatch() {
    const sport = document.getElementById("search-sport").value;
    const date = document.getElementById("search-date").value;
    const teamA = document.getElementById("search-team-a").value;
    const teamB = document.getElementById("search-team-b").value;
    const resultDiv = document.getElementById("searchResult");
    resultDiv.innerHTML = '';

    const params = new URLSearchParams();
    if (sport) params.append("sport", sport);
    if (date) params.append("date", date);
    if (teamA) params.append("team_a", teamA);
    if (teamB) params.append("team_b", teamB);

    try {
      const res = await fetch(`/api/search_match_advanced?${params.toString()}`);
      const data = await res.json();

      if (!data.matches || data.matches.length === 0) {
        resultDiv.innerHTML = '<p style="color: red;">❌ 沒有找到符合的比賽資料。</p>';
        return;
      }

      resultDiv.innerHTML = `<p>共找到 ${data.matches.length} 筆比賽：</p>`;

      const isF1 = sport === "2";

      data.matches.forEach(m => {
        const matchTitle = m.match || `${m.team_a_name} vs ${m.team_b_name}`;
        const formattedDate = new Date(m.date).toISOString().slice(0, 10);

        const div = document.createElement('div');
        div.className = 'match-card';
        div.id = `card_${m.game_no}`;

        const infoWrapper = document.createElement('div');
        infoWrapper.className = 'info-wrapper';

        const title = document.createElement('strong');
        title.className = 'match-title';
        title.textContent = matchTitle;

        const datetime = document.createElement('span');
        datetime.className = 'match-datetime';
        datetime.textContent = ` | ${formattedDate} ${m.time}`;

        const point = document.createElement('span');
        point.className = 'match-point';
        point.textContent = m.point ? ` | 比數：${m.point}` : ` | 比數：尚未公布`;

        infoWrapper.appendChild(title);
        infoWrapper.appendChild(datetime);
        infoWrapper.appendChild(point);

        const platforms = m.platforms && m.platforms.length > 0
          ? ` | 播放平台：${m.platforms.join("、")}`
          : ` | 播放平台：無`;

        const platformSpan = document.createElement('span');
        platformSpan.className = 'match-platforms';
        platformSpan.textContent = platforms;
        infoWrapper.appendChild(platformSpan);

        const buttonWrapper = document.createElement('div');
        buttonWrapper.className = 'button-wrapper';
        buttonWrapper.style.marginTop = '0.5rem';

        const editBtn = document.createElement('button');
        editBtn.textContent = '修改';
        editBtn.addEventListener('click', () => toggleEditForm(m.game_no, matchTitle, formattedDate, m.time));

        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = '刪除';
        deleteBtn.classList.add('delete-btn');
        deleteBtn.addEventListener('click', () => confirmDelete(m.game_no));

        buttonWrapper.appendChild(editBtn);
        buttonWrapper.appendChild(deleteBtn);

        div.appendChild(infoWrapper);
        div.appendChild(buttonWrapper);

        const editDiv = document.createElement('div');
        editDiv.id = `editForm_${m.game_no}`;
        editDiv.className = 'edit-form';

        div.appendChild(editDiv);
        resultDiv.appendChild(div);
      });
    } catch (error) {
      resultDiv.innerHTML = `<p style="color: red;">❌ 發生錯誤：${error.message}</p>`;
      console.error("❌ 搜尋錯誤：", error);
    }
  }


  function toggleEditForm(id, match, date, time) {
    const container = document.getElementById(`editForm_${id}`);
    if (container.innerHTML.trim() !== '') {
      container.innerHTML = '';
      return;
    }
    showEditForm(id, match, date, time);
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

  const m = data.match;
  const teamRes = await fetch("/api/teams?sport=" + m.type);
  allTeams = await teamRes.json();
  const teams = allTeams.filter(t => t.sport_type == m.type);

  const res2 = await fetch('/api/platforms');
  const allPlatforms = await res2.json();
  const selectedRes = await fetch(`/api/match/${id}/platforms`);
  const selected = await selectedRes.json();

  const platformContainer = document.createElement("div");
  platformContainer.className = "platform-checkboxes";
  Object.assign(platformContainer.style, {
    display: "block",
    width: "100%",
    maxHeight: "130px",
    overflowY: "auto",
    border: "1px solid #ccc",
    borderRadius: "6px",
    padding: "8px",
    backgroundColor: "#fff",
    boxSizing: "border-box",
    WebkitOverflowScrolling: "touch",
    fontSize: "16px",
    lineHeight: "1.8",
    textAlign: "left"
  });

  allPlatforms.forEach(p => {
    const wrapper = document.createElement("label");
    Object.assign(wrapper.style, {
      display: "flex",
      alignItems: "center",
      justifyContent: "flex-start",
      gap: "0.6em",
      marginBottom: "4px",
      width: "100%",
      cursor: "pointer",
      boxSizing: "border-box"
    });

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = p.platform_id;
    checkbox.classList.add("platform-checkbox");
    checkbox.checked = selected.includes(p.platform_id);

    const span = document.createElement("span");
    span.textContent = p.name;
    span.style.flex = "1";

    wrapper.appendChild(checkbox);
    wrapper.appendChild(span);
    platformContainer.appendChild(wrapper);
  });

  const saveBtn = document.createElement("button");
  saveBtn.textContent = "儲存";

  const dateInput = document.createElement("input");
  dateInput.type = "date";
  dateInput.value = m.date || '';

  const timeSelect = document.createElement("select");
  for (let hour = 0; hour < 24; hour++) {
    for (let min = 0; min < 60; min += 30) {
      const timeStr = `${String(hour).padStart(2, "0")}:${String(min).padStart(2, "0")}`;
      const opt = new Option(timeStr, timeStr);
      if (m.time === timeStr) opt.selected = true;
      timeSelect.appendChild(opt);
    }
  }

  const pointInput = document.createElement("input");
  pointInput.type = "text";
  pointInput.value = m.point || '';

  // F1
  if (m.type == 2) {
    const nameInput = document.createElement("input");
    nameInput.type = "text";
    nameInput.placeholder = "比賽名稱";
    nameInput.value = m.team_a_name || '';
    

    // 🆕 比賽類型輸入欄位
    const matchTypeInput = document.createElement("input");
    matchTypeInput.type = "text";
    matchTypeInput.placeholder = "比賽類型";
    matchTypeInput.value = m.match_type || '';
    matchTypeInput.style.marginBottom = "8px";


    container.innerHTML = '';
    container.appendChild(document.createTextNode("比賽名稱："));
    container.appendChild(nameInput);
    container.appendChild(document.createTextNode("比賽類型："));
    container.appendChild(matchTypeInput);
    container.appendChild(document.createTextNode("日期："));
    container.appendChild(dateInput);
    container.appendChild(document.createTextNode("時間："));
    container.appendChild(timeSelect);
    container.appendChild(document.createTextNode("播放平台（可複選）："));
    container.appendChild(platformContainer);
    container.appendChild(saveBtn);

    saveBtn.addEventListener("click", async () => {
      const selectedPlatforms = Array.from(platformContainer.querySelectorAll('.platform-checkbox:checked'))
        .map(cb => Number(cb.value));
      const payload = {
        date: dateInput.value,
        time: timeSelect.value,
        point: null,
        match_name: nameInput.value,
        platforms: selectedPlatforms,
        match_type: matchTypeInput.value
      };

      const res = await fetch(`/api/edit/${id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const result = await res.json();
      if (result.success) {
        alert("✅ 修改成功");
        container.innerHTML = '';
        document.getElementById("SearchBtn").click();
      } else {
        alert("❌ 修改失敗：" + result.message);
      }
    });

  // BWF
  } else if (m.type == 5) {
    const selectA = document.createElement("select");
    const selectB = document.createElement("select");
    const playerA1 = document.createElement("select");
    const playerA2 = document.createElement("select");
    const playerB1 = document.createElement("select");
    const playerB2 = document.createElement("select");

    teams.forEach(t => {
      const optA = new Option(t.team_name, t.team_id);
      const optB = new Option(t.team_name, t.team_id);
      if (t.team_id == m.team_a) optA.selected = true;
      if (t.team_id == m.team_b) optB.selected = true;
      selectA.appendChild(optA);
      selectB.appendChild(optB);
    });

    async function loadPlayers(teamId, selects, preselected = []) {
      const res = await fetch(`/api/get_bwf_players?team_id=${teamId}`);
      const players = await res.json();
      selects.forEach((select, idx) => {
        select.innerHTML = `<option value="">請選擇選手</option>`;
        players.forEach(p => {
          const opt = new Option(p.name, p.player_id);
          if (preselected[idx] == p.player_id) opt.selected = true;
          select.appendChild(opt);
        });
      });
    }

    await loadPlayers(m.team_a, [playerA1, playerA2], [m.player_1, m.player_2]);
    await loadPlayers(m.team_b, [playerB1, playerB2], [m.player_3, m.player_4]);

    container.innerHTML = '';
    container.appendChild(document.createTextNode("隊伍 A："));
    container.appendChild(selectA);
    container.appendChild(document.createTextNode("選手（隊伍 A）："));
    container.appendChild(playerA1);
    container.appendChild(playerA2);
    container.appendChild(document.createTextNode("隊伍 B："));
    container.appendChild(selectB);
    container.appendChild(document.createTextNode("選手（隊伍 B）："));
    container.appendChild(playerB1);
    container.appendChild(playerB2);
    container.appendChild(document.createTextNode("日期："));
    container.appendChild(dateInput);
    container.appendChild(document.createTextNode("時間："));
    container.appendChild(timeSelect);
    container.appendChild(document.createTextNode("比分："));
    container.appendChild(pointInput);
    container.appendChild(document.createTextNode("播放平台（可複選）："));
    container.appendChild(platformContainer);
    container.appendChild(saveBtn);

    selectA.addEventListener("change", () => loadPlayers(selectA.value, [playerA1, playerA2]));
    selectB.addEventListener("change", () => loadPlayers(selectB.value, [playerB1, playerB2]));

    saveBtn.addEventListener("click", async () => {
      const selectedPlatforms = Array.from(platformContainer.querySelectorAll('.platform-checkbox:checked'))
        .map(cb => Number(cb.value));

      const aPlayers = [playerA1.value, playerA2.value].filter(v => v);
      const bPlayers = [playerB1.value, playerB2.value].filter(v => v);

      // 數量檢查
      if (aPlayers.length !== bPlayers.length) {
        alert(`❌ 隊伍 A 與 B 的選手數量需一致（目前是 ${aPlayers.length} vs ${bPlayers.length}）`);
        return;
      }

      const allSelected = [...aPlayers, ...bPlayers];
      const uniqueSet = new Set(allSelected);

      // 重複檢查
      if (uniqueSet.size !== allSelected.length) {
        alert("❌ 不可選擇相同的選手！");
        return;
      }

      const payload = {
        team_a: selectA.value,
        team_b: selectB.value,
        date: dateInput.value,
        time: timeSelect.value,
        point: pointInput.value,
        platforms: selectedPlatforms,
        player_1: aPlayers[0] || null,
        player_2: aPlayers[1] || null,
        player_3: bPlayers[0] || null,
        player_4: bPlayers[1] || null
      };

      const res = await fetch(`/api/edit/${id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const result = await res.json();
      if (result.success) {
        alert("✅ 修改成功");
        container.innerHTML = '';
        document.getElementById("SearchBtn").click();
      } else {
        alert("❌ 修改失敗：" + result.message);
      }
    });



  // 其他運動
  } else {
    const selectA = document.createElement("select");
    const selectB = document.createElement("select");
    teams.forEach(t => {
      const optA = new Option(t.team_name, t.team_id);
      const optB = new Option(t.team_name, t.team_id);
      if (t.team_id == m.team_a) optA.selected = true;
      if (t.team_id == m.team_b) optB.selected = true;
      selectA.appendChild(optA);
      selectB.appendChild(optB);
    });

    container.innerHTML = '';
    container.appendChild(document.createTextNode("隊伍 A："));
    container.appendChild(selectA);
    container.appendChild(document.createTextNode("隊伍 B："));
    container.appendChild(selectB);
    container.appendChild(document.createTextNode("日期："));
    container.appendChild(dateInput);
    container.appendChild(document.createTextNode("時間："));
    container.appendChild(timeSelect);
    container.appendChild(document.createTextNode("比分："));
    container.appendChild(pointInput);
    container.appendChild(document.createTextNode("播放平台（可複選）："));
    container.appendChild(platformContainer);
    container.appendChild(saveBtn);

    saveBtn.addEventListener("click", async () => {
      const selectedPlatforms = Array.from(platformContainer.querySelectorAll('.platform-checkbox:checked'))
        .map(cb => Number(cb.value));
      const payload = {
        team_a: selectA.value,
        team_b: selectB.value,
        date: dateInput.value,
        time: timeSelect.value,
        point: pointInput.value,
        platforms: selectedPlatforms
      };

      const res = await fetch(`/api/edit/${id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const result = await res.json();
      if (result.success) {
        alert("✅ 修改成功");
        container.innerHTML = '';
        document.getElementById("SearchBtn").click();
      } else {
        alert("❌ 修改失敗：" + result.message);
      }
    });
  }
}


  async function confirmDelete(game_no) {
  const yes = confirm("確定要刪除這筆比賽嗎？");
  if (!yes) return;

  try {
    const res = await fetch(`/api/delete/${game_no}`, {
      method: "DELETE"
    });
    const result = await res.json();

    if (result.success) {
      alert("✅ 刪除成功");

      // ✅ 立即從畫面上移除該比賽卡片
      const card = document.getElementById(`card_${game_no}`);
      if (card) card.remove();

      // ✅ 如果有查詢按鈕，就觸發重新查詢（確保同步）
      const searchBtn = document.getElementById("SearchBtn");
      if (searchBtn) searchBtn.click();
    } else {
      alert("❌ 刪除失敗：" + result.message);
    }
  } catch (err) {
    alert("❌ 刪除時發生錯誤：" + err.message);
  }
}




  document.getElementById('AddBtn').addEventListener('click', () => addRow(true));
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
        const userDisplayName = fb.user_name || uid;

        title.className = 'feedback-title';
        title.innerHTML = `<strong>使用者 ${fb.user_name}</strong> | 賽事類型 : ${typemap[fb.f_type]} | 日期時間 : ${date} ${fb.f_time}`;

        const detail = document.createElement('div');
        detail.className = 'feedback-detail';
        detail.style.display = 'none';

        const p = document.createElement('p');
        p.textContent = `📃內容 : ${fb.content}`;
        detail.appendChild(p);

        const status = document.createElement('div');
        status.innerHTML = `狀態：<span class="status-text"><strong>${fb.f_status}</strong></span>`;
        detail.appendChild(status);

        if (fb.admin_id != "") {
            const admin = document.createElement('div');
            const adminname = fb.admin_name === null || fb.admin_name === "null" ? "尚無管理員認領" : fb.admin_name;
            admin.innerHTML = `管理者：<span>${adminname}</span>`;
            detail.appendChild(admin);
        }
        if (fb.reply_date || fb.reply_time) {
            const replyTime = document.createElement('div');
            replyTime.innerHTML = `回覆時間：<span>${fb.reply_date} ${fb.reply_time}</span>`;
            detail.appendChild(replyTime);
        }

        // 顯示回覆內容（reply 或 reason）
        if ((fb.f_status === '已處理' || fb.f_status === '不採納')) {
            const reply = document.createElement('div');
            reply.innerHTML = `回覆內容：<span>${fb.reply || fb.reason || '（無內容）'}</span>`;
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
        // 最高管理員 或「處理中」且 admin 為當前使用者才顯示可編輯區塊（可提交為已處理/不採納）
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
}else if (page === "search"){
  
    const today = new Date().toISOString().slice(0, 10);
    document.getElementById("date").value = today;

    const sportTypeSelect = document.getElementById("sport-type");
    const querySelect = document.getElementById("query-type");
    const keywordSelect = document.getElementById("keyword");
    const searchBtn = document.getElementById("SearchBtn");
    const dateInput = document.getElementById("date");
    const resultDiv = document.getElementById("searchResult");
    const extraFields = document.getElementById("extra-fields");

    // ✅ 頁面載入時初始化狀態
    window.addEventListener("DOMContentLoaded", () => {
      sportTypeSelect.value = "";
      querySelect.value = "";
      keywordSelect.value = "";
      querySelect.disabled = true;
      keywordSelect.disabled = true;
      searchBtn.disabled = true;
      keywordSelect.innerHTML = `<option value="">請先選擇查詢方式</option>`;
      resultDiv.innerHTML = "";
      extraFields.style.display = "none";
    });

    // ✅ 當選擇運動種類時
    sportTypeSelect.addEventListener("change", () => {
      const sport = sportTypeSelect.value;
      resultDiv.innerHTML = "";

      // 重設所有下拉與狀態
      querySelect.value = "";
      keywordSelect.value = "";
      querySelect.disabled = true;
      keywordSelect.disabled = true;
      searchBtn.disabled = true;
      keywordSelect.innerHTML = `<option value="">請先選擇查詢方式</option>`;

      if (sport === "2") {
        // ✅ F1
        querySelect.style.display = "none";
        keywordSelect.style.display = "none";
        extraFields.style.display = "none";
        searchBtn.disabled = false;
      } else if (sport) {
        // ✅ 其他運動
        querySelect.style.display = "";
        keywordSelect.style.display = "";
        extraFields.style.display = "";
        querySelect.disabled = false;
        // keyword 仍是 disabled，直到查詢方式選擇後觸發載入
      } else {
        // ❌ 清空狀態
        querySelect.style.display = "";
        keywordSelect.style.display = "";
        extraFields.style.display = "none";
      }
    });
    
    querySelect.addEventListener("change", () => {
      keywordSelect.innerHTML = `<option value="">請先選擇</option>`;
      keywordSelect.disabled = true;
      resultDiv.innerHTML = "";
      updateKeywordOptions();
    });

    keywordSelect.addEventListener("change", () => {
      const keyword = keywordSelect.value;
      resultDiv.innerHTML = "";
      searchBtn.disabled = !keyword;
    });

    dateInput.addEventListener("change", () =>{
      resultDiv.innerHTML = "";
    });


    //載入關鍵字下拉選單
    async function updateKeywordOptions() {
        const type = querySelect.value;
        const sport_type = sportTypeSelect.value;
        const extraFields = document.getElementById("extra-fields");

        // 先清空結果畫面與欄位狀態
        resultDiv.innerHTML = "";
        querySelect.disabled = false;
        keywordSelect.disabled = true;

        keywordSelect.innerHTML = `<option value="">請先選擇 運動 與 查詢方式</option>`;

        // F1 → 隱藏查詢欄位，直接 return
        if (sport_type === "2") {
            extraFields.style.display = "none";
            return;
        }

        // 其他運動 → 顯示欄位並繼續處理
        extraFields.style.display = "";

        // 如果還沒選查詢方式，停止
        if (!type) return;
        

        try {
            const res = await fetch(`/api/get_options?sport_type=${sport_type}&query_type=${type}`);
            const data = await res.json();

            keywordSelect.disabled = false; // 成功載入選項再打開

            console.log("關鍵字選項：", data);

            keywordSelect.innerHTML = `<option value="">請選擇</option>`;
            data.forEach(item => {
                const opt = document.createElement("option");
                opt.value = item.id;
                opt.textContent = item.name;
                keywordSelect.appendChild(opt);
            });
        } catch (err) {
            console.error("載入選項失敗：", err);
            keywordSelect.innerHTML = `<option value="">載入失敗</option>`;
        }
    }

    // 查詢比賽
    document.getElementById("SearchBtn").addEventListener("click", async () => {
        const type = querySelect.value;
        const sport = sportTypeSelect.value;
        const keyword = keywordSelect.value;
        const date = dateInput?.value;

        let keywordText = keywordSelect.options[keywordSelect.selectedIndex]?.textContent || keyword;
        let teamText = "";

        // 查隊伍名稱
        if (type === "team") {
            try {
                const res = await fetch(`/api/get_team_name?team_id=${keyword}`);
                const data = await res.json();
                if (data.team_name) keywordText = data.team_name;
            } catch (err) {
                console.warn("⚠️ 查詢隊伍名稱失敗", err);
            }
        }else if (type === "player") {
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

        if (!sport) {
          alert("請選擇運動種類");
          return;
        }
        if (sport !== "2" && (!type || !keyword)) {
          alert("請選擇查詢方式與關鍵字");
          return;
        }

        const params = new URLSearchParams({ sport, date });

        if (sport !== "2") {
            params.append("query_type", type);
            params.append("keyword", keyword);
        }

        try {
            const res = await fetch(`/api/search_matches?${params}`);
            const data = await res.json();

            resultDiv.innerHTML = "";

            if (!data || !data.matches || data.matches.length === 0) {
                resultDiv.innerHTML = "<p>查無比賽資料</p>";
                return;
            }

            console.log("比賽數量：", data.matches.length);

            if(type === "team" && sport !== "2"){
                resultDiv.innerHTML = `
                    <p>以「<strong>${sportmap[sport]}</strong> - <strong>${keywordText}</strong>」<br>查詢 ${date} 的比賽</p>
                    <p>找到 ${data.matches.length} 筆比賽：</p>
                `;
            }else if(type === "player"){
                resultDiv.innerHTML = `
                    <p>以「<strong>${sportmap[sport]}</strong> - <strong>${teamText}</strong>的${typemap[type]} <strong>${keywordText}</strong>」<br>查詢 ${date} 起的比賽</p>
                    <p>找到 ${data.matches.length} 筆比賽：</p>
                `;
            }else{
              resultDiv.innerHTML = `<p>找到 ${data.matches.length} 筆比賽：</p>`
            }

            data.matches.forEach(m => {
              const formattedDate = new Date(m.date).toISOString().slice(0, 10);
              const matchTitle = sport === "2"
                  ? m.match_name
                  : `${m.team_a_name} vs ${m.team_b_name}`;

              if(sport === "2"){
                resultDiv.innerHTML += `
                <div class="match-card" id="card_${m.game_no}" style="margin-bottom: 1rem;">
                  <strong>${matchTitle}</strong><br>
                  日期時間 : ${formattedDate} ${m.time}<br>
                  類型 : ${m.match_type}<br>
                </div>  
              `;
              }else{
                resultDiv.innerHTML += `
                <div class="match-card" id="card_${m.game_no}" style="margin-bottom: 1rem;">
                  <strong>${matchTitle}</strong><br>
                  日期時間 : ${formattedDate} ${m.time}<br>
                  比分：${m.point ?? "尚未公布"}<br>
                </div>  
              `;
              }

              
          });
        } catch (err) {
            console.error("查詢錯誤：", err);
            resultDiv.innerHTML = "<p>⚠️ 發生錯誤，請稍後再試</p>";
        }
    });

}else if (page === "mix_search") {

  window.addEventListener("DOMContentLoaded", () => {
    const page = document.body.dataset.page;

    if (page === "mix_search") {
      const queryTypeInput = document.getElementById("query-type");
      const sportTypeInput = document.getElementById("sport-type");
      const keywordSelect = document.getElementById("keyword");
      const searchBtn = document.getElementById("SearchBtn");
      const resetBtn = document.getElementById("ResetBtn");
      const resultArea = document.getElementById("mix-result-area");

      // 預設狀態
      sportTypeInput.value = "";
      queryTypeInput.value = "";
      keywordSelect.value = "";

      queryTypeInput.disabled = true;
      keywordSelect.disabled = true;
      searchBtn.disabled = true;

      keywordSelect.innerHTML = `<option value="">請選擇</option>`;
      resultArea.innerHTML = "";

      sportTypeInput.addEventListener("change", () => {
        const sportType = sportTypeInput.value;
        resultArea.innerHTML = "";

        queryTypeInput.value = "";
        keywordSelect.value = "";
        queryTypeInput.disabled = true;
        keywordSelect.disabled = true;
        searchBtn.disabled = true;
        keywordSelect.innerHTML = `<option value="">請選擇</option>`;
        
        const teamOption = [...queryTypeInput.options].find(opt => opt.value === "team");
        if (sportType === "5" && teamOption) {
          teamOption.disabled = true;
          // 如果原本選的是隊伍就自動清空
          if (queryTypeInput.value === "team") queryTypeInput.value = "";
        } else if (teamOption) {
          teamOption.disabled = false;
        }

        if (sportType) {
          queryTypeInput.disabled = false;
        }
      });

      queryTypeInput.addEventListener("change", () => {
        keywordSelect.disabled = true;
        keywordSelect.innerHTML = `<option value="">請選擇</option>`;
        searchBtn.disabled = true;
        resultArea.innerHTML = "";
        fetchKeywordList();
      });

      keywordSelect.addEventListener("change", () => {
        resultArea.innerHTML = "";
        searchBtn.disabled = !keywordSelect.value;
      });

      function fetchKeywordList() {
        const type = queryTypeInput.value;
        const sportType = sportTypeInput.value;

        if (!type || !sportType) {
          keywordSelect.disabled = true;
          keywordSelect.innerHTML = `<option value="">請選擇</option>`;
          return;
        }

        if (type === "team" && sportType === "5") {
          alert("BWF 不支援隊伍查詢");
          return;
        }

        fetch(`/api/get_keywords?type=${type}&sport_type=${sportType}`)
          .then(res => res.json())
          .then(data => {
            if (!Array.isArray(data)) {
              alert("後端回傳錯誤：" + (data.error || "未知錯誤"));
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
              alert("查詢失敗：" + (data.error || "請檢查參數"));
              return;
            }

            resultArea.innerHTML = "";

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
                    const batting = ((player.batting_avg * 100).toFixed(1));
                    const era = ((player.era * 100).toFixed(1));

                    html += `隊伍：${player.team_name}<br>
                            背號：${player.jersey_number}<br>
                            守備位置：${player.position}<br>
                            打擊習慣：${player.batting_hand}<br>`;
                    if (batting != 0) { html += `打擊率：${batting}%<br>`; }
                    if (era != 0) { html += `防守：${player.era}<br>`; }

                    break;
                  case 5:
                    html += `慣用手：${player.hand}<br>
                            世界排名：${player.world_rank === "null" ? "/" : player.world_rank}<br>
                            巡迴排名：${player.world_tour_rank === "null" ? "/" : player.world_tour_rank}<br>
                            世界 : ${player.world_rank_title} <br>巡迴 : ${player.world_tour_rank_title}<br>
                            積分頭銜：${player.point_title}｜積分：${player.point}`;
                    break;
                  default:
                    html += `（不支援顯示）`;
                }

                div.innerHTML = html;
                resultArea.appendChild(div);
              });
            } else if (type === "team") {
              data.forEach(team => {
                const div = document.createElement("div");
                div.className = "result-card";

                let html = `<strong>${team.team_name}</strong><br>`;

                switch (sportTypeNum) {
                  case 1:
                    html += `城市：${team.city_name}<br>
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
                    html += `聯盟：${team.league}<br>
                            城市：${team.city_name}<br>
                            主場：${team.stadium}`;                                            
                    break;
                  default:
                    html += "（不支援的運動種類）";
                }

                div.innerHTML = html;
                resultArea.appendChild(div);
              });
            } else if (type === "event") {
              data.forEach(match => {
                const div = document.createElement("div");
                div.className = "result-card";
                const m_n = (sportType === "2") ? match.match_name : match.team_a_name + " vs " + match.team_b_name;
                let html = `<strong> ${m_n}</strong><br>`;
                html += `時間：${match.date} ${match.time}<br>`;
                html += `比數：${match.point === null ? "尚未開始" : match.point}<br><br>`;

                div.innerHTML = html;
                resultArea.appendChild(div);
              });
            }
          });
      });

      // 重設按鈕
      resetBtn.addEventListener("click", () => {
        sportTypeInput.innerHTML = `<option value="">請選擇</option>`;
        const sportOptions = [
          { value: "1", label: "NBA" },
          { value: "2", label: "F1" },
          { value: "3", label: "MLB" },
          { value: "4", label: "CPBL" },
          { value: "5", label: "BWF" }
        ];
        sportOptions.forEach(opt => {
          const option = document.createElement("option");
          option.value = opt.value;
          option.textContent = opt.label;
          sportTypeInput.appendChild(option);
        });

        sportTypeInput.disabled = false;
        sportTypeInput.value = "";

        queryTypeInput.value = "";
        queryTypeInput.disabled = true;

        keywordSelect.innerHTML = `<option value="">請選擇</option>`;
        keywordSelect.disabled = true;

        searchBtn.disabled = true;
        resultArea.innerHTML = "";
      });
    }
  });


}else if(page === "recent_match"){
    //UID
    const uid = "10107670810";

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
      try {
          const res = await fetch(`/api/bookings/user/${uid}`);
          if (!res.ok) {
              throw new Error(`❌ fetch 錯誤: ${res.status}`);
          }
          
          const data = await res.json();

          existingBookings = data;  // ✅ 這樣會保留 game_no

          console.log("🎯 existingBookings:", existingBookings);
          displayBookedMatches();
          await loadTopPlatform(uid);
      } catch (err) {
          console.error("❌ loadBookings 發生錯誤:", err);
      }
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
              const list = rawList[date];
              const combinedMap = {};

              list.forEach(match => {
                const matchName = match.match_name || match.name || "未知比賽名稱";
                const key = `${matchName}_${match.time}`;

                if (!combinedMap[key]) {
                  combinedMap[key] = {
                    game_no: match.game_no,
                    name: matchName,
                    match_name: matchName,
                    time: match.time,
                    platform: [match.platform],
                    type: match.type
                  };
                } else {
                  // 如果已經存在此比賽名稱與時間 → 加入平台
                  if (!combinedMap[key].platform.includes(match.platform)) {
                    combinedMap[key].platform.push(match.platform);
                  }
                }
              });

              // 將 map 的值轉成陣列
              matchData[date] = Object.values(combinedMap);
            }


            await loadBookings();  //先載入 existingBookings
            renderCalendar(currentYear, currentMonth);
        } catch (err) {
            console.error('❌ 無法載入比賽資料:', err);
        }
        console.log("📦 matchData", matchData);
    }

    function isBooked(dateStr, matchName) {
        const data = existingBookings[dateStr] || [];
        return data.some(m => m.name === matchName && m.game_no === gameNo);
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
          const merged = {};

          for (let match of existingBookings[date]) {
            const key = `${match.name}_${match.time}`;

            if (!merged[key]) {
              merged[key] = {
                ...match,
                platform: [match.platform]  // 包成陣列
              };
            } else {
              if (!merged[key].platform.includes(match.platform)) {
                merged[key].platform.push(match.platform);
              }
            }
          }

          for (let matchKey in merged) {
            const mergedMatch = merged[matchKey];
            bookedEl.appendChild(createBookingCard(date, mergedMatch, false));
          }
        }

        let uniqueGameNos = new Set();

        // 把已預約的加入 Set
        for (let date in existingBookings) {
            for (let match of existingBookings[date]) {
                uniqueGameNos.add(match.game_no);
            }
        }

        // 把剛新增的也加入 Set
        for (let date in pendingBookings) {
            for (let match of pendingBookings[date]) {
                uniqueGameNos.add(match.game_no);
            }
        }

        const total = uniqueGameNos.size;
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
            📺 平台：${Array.isArray(match.platform) ? match.platform.join("、") : match.platform}
        `;

        const cancelBtn = document.createElement("button");
        cancelBtn.textContent = "X";
        cancelBtn.dataset.date = date;
        cancelBtn.dataset.name = match.name;
        cancelBtn.dataset.time = match.time;
        cancelBtn.dataset.isNew = isNew;
        cancelBtn.dataset.gameNo = match.game_no || "";


        card.appendChild(content);
        card.appendChild(cancelBtn);
        return card;
    }

    document.getElementById("booked-matches").addEventListener("click", function (e) {
        if (e.target.tagName === "BUTTON" && e.target.textContent === "X") {
            const { date, name, time, isNew } = e.target.dataset;
            const target = isNew === "true" ? pendingBookings : existingBookings;

            if (!target[date]) return;

            // 根據 name + time 刪掉全部相同比賽
            const removedList = target[date].filter(m => m.name === name && m.time === time);
            target[date] = target[date].filter(m => !(m.name === name && m.time === time));

            // 若當天已沒比賽，移除該日期
            if (target[date].length === 0) {
              delete target[date];
            }

            // 把每筆記錄都加入 deletedBookings（用來送出刪除資料）
            removedList.forEach(removed => {
              deletedBookings.push({
                date,
                match: removed,
                game_no: removed.game_no,
                isNew: isNew === "true"
              });
            });

            displayBookedMatches();
            refreshSelectedDate(date);
        }
    });

    function isAlreadySelected(dateStr, matchObj) {
      const normalizeTime = (t) => t.length === 5 ? t + ":00" : t;
      const matchName = matchObj.name;
      const matchTime = normalizeTime(matchObj.time);

      function check(list, label) {
          return (list[dateStr] || []).some(m =>
              m.name === matchName &&
              normalizeTime(m.time) === matchTime
          );
      }

      return check(existingBookings, "已預約") || check(pendingBookings, "剛新增");
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

            if (isAlreadySelected(dateStr, matchObj)) {
              console.log("已經選過了，跳過：", matchObj.name);
              return;
            }
            hasVisible = true; // 有比賽可以顯示

            const btn = document.createElement("button");
            btn.className = "match-card";
            const matchDisplayName = matchObj.type === 2 ? matchObj.match_name : matchObj.name;
            btn.textContent = `【${typeMap[matchObj.type]}】 ${matchDisplayName} 🕒 ${matchObj.time}`;

            if (diffMinutes < 3) {
                btn.classList.add("disabled");
                btn.addEventListener("click", () => {
                alert(`此比賽已過或即將開始，無法預約。\n ${matchObj.name}\n📅 ${dateStr}\n🕒 ${matchObj.time}`);
            });
            } else {
            btn.addEventListener("click", async () => {
                console.log('selected');
                if (!pendingBookings[dateStr]) pendingBookings[dateStr] = [];
                const now = new Date();
                pendingBookings[dateStr].push({
                  ...matchObj,
                  game_no: matchObj.game_no 
                });
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
            const uniqueGameNos = new Set();

            // 把已預約的加入 Set
            for (let date in existingBookings) {
                for (let match of existingBookings[date]) {
                    uniqueGameNos.add(match.game_no);
                }
            }

            // 把剛新增的也加入 Set（不會重複）
            for (let date in pendingBookings) {
                for (let match of pendingBookings[date]) {
                    uniqueGameNos.add(match.game_no);
                }
            }

            const total = uniqueGameNos.size;
            alert(`✅ 已儲存 ${total} 筆預約資料！`);

            // ✅ 更新 existingBookings
            for (let date in pendingBookings) {
                if (!existingBookings[date]) existingBookings[date] = [];
                existingBookings[date] = existingBookings[date].concat(pendingBookings[date]);
            }
            for (let { date, match } of deletedBookings) {
                if (!existingBookings[date]) continue;
                existingBookings[date] = existingBookings[date].filter(m => !(m.name === match.name && m.time === match.time));
                if (existingBookings[date].length === 0) delete existingBookings[date];
            }


            pendingBookings = {};
            deletedBookings = [];

            displayBookedMatches();
            await loadTopPlatform(uid);
        }else {
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
}else if(page === "super_admin"){
  const sessionId = parseInt("{{ session['admin_id'] }}");

    function updateAdmin(id) {
      const username = document.querySelector(`.edit-username[data-id='${id}']`)?.value;
      const password = document.querySelector(`.edit-password[data-id='${id}']`)?.value;

      fetch(`/api/admins/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      }).then(res => res.json()).then(data => {
        alert(data.message);
      });
    }

    function deleteAdmin(id) {
      if (!confirm("❗確定要刪除這位管理員嗎？")) return;

      fetch(`/api/admins/${id}`, {
        method: 'DELETE'
      }).then(res => res.json()).then(data => {
        alert(data.message);
        const row = document.querySelector(`button.delete[onclick*="${id}"]`)?.closest('tr');
        if (row) row.remove();
      });
    }

    function upgradeAdmin(id) {
      if (!confirm("❗確定要將此管理員升級為最高權限？")) return;

      fetch(`/api/admins/${id}/upgrade`, {
        method: 'POST'
      }).then(res => res.json()).then(data => {
        alert(data.message);
        if (data.admin) replaceAdminRow(data.admin);
      });
    }

    function downgradeAdmin(id) {
      if (!confirm("❗確定要將此管理員降為一般權限？")) return;

      fetch(`/api/admins/${id}/downgrade`, {
        method: 'POST'
      }).then(res => res.json()).then(data => {
        alert(data.message);
        if (data.admin) replaceAdminRow(data.admin);
      });
    }

    function replaceAdminRow(admin) {
      const row = document.querySelector(`button.update[onclick*="${admin.admin_id}"]`)?.closest('tr');
      if (!row) return;

      const isSelf = admin.admin_id === sessionId;
      const isTop = admin.permission_level === 1;

      row.innerHTML = `
        <td>${admin.admin_id}</td>
        <td>
          ${isSelf || isTop ? `<input type="text" value="${admin.user_name}" data-id="${admin.admin_id}" class="edit-username">` : admin.user_name}
        </td>
        <td>
          ${isSelf || isTop ? `<input type="text" value="${admin.password}" data-id="${admin.admin_id}" class="edit-password">` : '*****'}
        </td>
        <td>${admin.permission_level}</td>
        <td>
          <button class="update" onclick="updateAdmin(${admin.admin_id})">修改</button>
          ${!isSelf ? `
            <button class="delete" onclick="deleteAdmin(${admin.admin_id})">刪除</button>
            ${admin.permission_level === 1 ? `
              <button class="upgrade" onclick="upgradeAdmin(${admin.admin_id})">升級權限</button>
            ` : `
              <button class="downgrade" onclick="downgradeAdmin(${admin.admin_id})">降級權限</button>
            `}
          ` : ''}
        </td>
      `;
    }
}