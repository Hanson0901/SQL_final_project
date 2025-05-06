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

  // 查詢功能
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

  // 重設reset功能
  function resetForm() {
    document.getElementById('sport').selectedIndex = document.getElementById('sport')[0];
    document.getElementById('player').value = "";
    document.getElementById('start-time').selectedIndex = 0;
    document.getElementById('end-time').selectedIndex = 0;
  }