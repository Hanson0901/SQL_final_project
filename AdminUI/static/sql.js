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
  