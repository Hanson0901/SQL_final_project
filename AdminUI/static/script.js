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
      <td><button id="removebtn" onclick="this.closest('tr').remove();">X</button></td>
    `;
    tbody.appendChild(tr);
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

      const title = document.createElement('strong');
      title.className = 'match-title';
      title.textContent = m.match;

      const datetime = document.createElement('span');
      datetime.className = 'match-datetime';
      datetime.textContent = ` | ${m.date} ${m.time}`;

      const editBtn = document.createElement('button');
      editBtn.textContent = '修改';
      editBtn.addEventListener('click', () => {
        toggleEditForm(m.id, m.match, m.date, m.time);
      });


      const editDiv = document.createElement('div');
      editDiv.id = `editForm_${m.id}`;
      editDiv.className = 'edit-form';
      editDiv.style.marginTop = '0.5rem';
      editDiv.style.marginBottom = '5%';

      
      div.appendChild(title);
      div.appendChild(datetime);
      div.appendChild(editBtn);
      div.appendChild(editDiv);

      resultDiv.appendChild(div);
    });
  }

  function showEditForm(id, match, date, time) {
    const container = document.getElementById(`editForm_${id}`);
    container.innerHTML = '';

    const matchInput = document.createElement('input');
    matchInput.type = 'text';
    matchInput.id = `match_${id}`;
    matchInput.value = match;

    const dateInput = document.createElement('input');
    dateInput.type = 'text';
    dateInput.id = `date_${id}`;
    dateInput.value = date;

    const timeInput = document.createElement('input');
    timeInput.type = 'text';
    timeInput.id = `time_${id}`;
    timeInput.value = time;

    const saveBtn = document.createElement('button');
    saveBtn.textContent = '儲存';
    saveBtn.addEventListener('click', () => saveEdit(id));

    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = '刪除';
    deleteBtn.classList.add('delete-btn');
    deleteBtn.addEventListener('click', () => confirmDelete(id));

    container.appendChild(matchInput);
    container.appendChild(dateInput);
    container.appendChild(timeInput);
    container.appendChild(saveBtn);
    container.appendChild(deleteBtn);
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
      const timestamp = Date.now();
      const status = document.getElementById("announceStatus");
      

      //抓管理者帳號
      const author = document.body.dataset.username;

      if (!content) {
          status.innerText = "❌ 請輸入公告內容";
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

      [...data].reverse().forEach((ann) => {
          const div = document.createElement('div');
          div.className = 'announcement';
          div.innerHTML = `
          <p>📣 ${ann.content}</p>
          <hr>
          <div class="meta">
          🕒 ${ann.datetime} ｜ 👤 ${ann.author}
          <button class="DeleteAnsBtn" data-timestamp="${ann.timestamp}" style="margin: 0.3rem auto 0 auto;">刪除</button>
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
            Object.entries(data).forEach(([uid, feedbacks]) => {
                Object.entries(feedbacks).forEach(([date, fb]) => {
                    const card = createFeedbackCard(uid, date, fb);
                    // 根據狀態分類放到對應的區塊
                    if (fb.status === '已處理') {
                        doneList.appendChild(card);
                    } else if (fb.status === '處理中') {
                        processingList.appendChild(card);
                    } else if (fb.status === '未處理') {
                        unprocessedList.appendChild(card);
                    } else if (fb.status === '不採納') {
                        rejectedList.appendChild(card);
                    }
                });
            });
        });


    // === createFeedbackCard 函數 ===

    function createFeedbackCard(uid, date, fb) {
        const card = document.createElement('div');
        card.className = 'feedback-card';
        card.style.cursor = 'pointer';

        const title = document.createElement('div');
        title.className = 'feedback-title';
        title.innerHTML = `<strong>使用者 ${uid}</strong> | 🏸 ${fb.type} | 🗓️ ${date} ${fb.time}`;

        const detail = document.createElement('div');
        detail.className = 'feedback-detail';
        detail.style.display = 'none';

        const p = document.createElement('p');
        p.textContent = `✏️ ${fb.feedback}`;
        detail.appendChild(p);

        const status = document.createElement('div');
        status.innerHTML = `❓ 狀態：<span class="status-text">${fb.status}</span>`;
        detail.appendChild(status);

        if (fb.admin) {
            const admin = document.createElement('div');
            admin.innerHTML = `👤 管理者：<span>${fb.admin}</span>`;
            detail.appendChild(admin);
        }
        if (fb.reply_date || fb.reply_time) {
            const replyTime = document.createElement('div');
            replyTime.innerHTML = `📅 回覆時間：<span>${fb.reply_date} ${fb.reply_time}</span>`;
            detail.appendChild(replyTime);
        }

        // 顯示回覆內容（reply 或 reason）
        if ((fb.status === '已處理' || fb.status === '不採納')) {
            const reply = document.createElement('div');
            reply.innerHTML = `💬 回覆內容：<span>${fb.reply || fb.reason || '（無內容）'}</span>`;
            detail.appendChild(reply);
        }

        // 🔘 認領按鈕：僅在 admin 欄位為空且狀態為未處理時顯示
        if (!fb.admin && fb.status === '未處理') {
            const claimBtn = document.createElement('button');
            claimBtn.textContent = '認領';
            claimBtn.className = 'claim-btn';
            claimBtn.addEventListener('click', async () => {
                const res = await fetch(`/api/feedback/${uid}/${date}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        admin: document.body.dataset.username,
                        status: '處理中'
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

        // ✅ 僅「處理中」且 admin 為當前使用者才顯示可編輯區塊（可提交為已處理/不採納）
        if (fb.status === '處理中' && fb.admin === document.body.dataset.username) {
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

                const payload = {
                    status: finalStatus,
                    admin: document.body.dataset.username,
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