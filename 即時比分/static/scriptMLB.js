function formatLocalTime(utcTimeString, offsetHours = -12) {
    const date = new Date(utcTimeString);
    date.setHours(date.getHours() + offsetHours);
    return date.toISOString().slice(11, 16);
  }
  document.addEventListener('DOMContentLoaded', function () {
  // 選出所有 class="bag" 的元素
  document.querySelectorAll('.bag').forEach(function(bagDiv) {
    // 檢查是否有內容（去除空白後長度大於 0）
    if (bagDiv.innerHTML.trim().length > 0) { // [4][7]
      // 建立新的 div
      var rheRow = document.createElement('div');
      rheRow.className = 'bag-inner-space';
      // 插入到 bagDiv 最前面
      bagDiv.insertBefore(rheRow, bagDiv.firstChild); // [5][6]
    }
  });
  document.querySelectorAll('.bag').forEach(function(bagDiv) {
    // 檢查內容是否為空（去除空白後長度大於 0）
    if (bagDiv.innerHTML.trim().length > 0) {
      // 建立新的 div
      var rheRow = document.createElement('div');
      rheRow.className = 'bag-space';
      // 將 rheRow 插入到 bagDiv 的前面（bag 的父元素下）
      bagDiv.parentNode.insertBefore(rheRow, bagDiv);
    }
  });
});

  (function autoRefresh() {
    const pageDate = window.pageDate;
    // 取得明天的日期字串 (yyyy-mm-dd)
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate());
    const today = tomorrow.toISOString().split('T')[0];
    console.log('pageDate:', pageDate, 'today:', today);
  
    const refreshInterval = setInterval(() => {
      console.log('定時刷新觸發:', new Date().toLocaleTimeString());
      fetch(`/api/mlb_games?date=${today}&_=${Date.now()}`, {
        headers: { 'Cache-Control': 'no-cache' }
      })
        .then(response => {
          if (!response.ok) throw new Error(`HTTP 錯誤! 狀態碼: ${response.status}`);
          return response.json();
        })
        .then(data => {
          console.log('收到新資料:', data);
          updateGames(data.games);
        })
        .catch(error => {
          console.error('更新失敗:', error);
          clearInterval(refreshInterval);
        });
    }, 10000);

    // 更新頁面內容的函數
    function updateGames(games) {
    // 取得現在本地時間並格式化
      const now = new Date();
      const formatted = now.getFullYear() + '-' +
        String(now.getMonth() + 1).padStart(2, '0') + '-' +
        String(now.getDate()).padStart(2, '0') + ' ' +
        String(now.getHours()).padStart(2, '0') + ':' +
        String(now.getMinutes()).padStart(2, '0') + ':' +
        String(now.getSeconds()).padStart(2, '0');

      // 顯示到 refresh-time 區塊
      const refreshDiv = document.querySelector('.refresh-time');
      if (refreshDiv) {
        refreshDiv.textContent = '最後更新時間：' + formatted;
      }
      const container = document.querySelector('.scoreboards');
      if (!container) return;

      // 清空現有內容
      container.innerHTML = '';

      // 重建所有比賽區塊
      games.forEach(game => {
        const gameHTML = `
          <div class="scoreboard">
            <div class="game-time">${game.time.slice(0, 5)}</div> <!-- 顯示前5字符 -->
            <div class="game-status">
              <div class="teams">
                <div>隊伍</div>
                <div class="team-info">
                  <img src="${game.img[0]}" class="team-logo">
                  <div><div class="team-name">${game.teams[0]}</div></div>
                </div>
                <div class="team-info">
                  <img src="${game.img[1]}" class="team-logo">
                  <div><div class="team-name">${game.teams[1]}</div></div>
                </div>
              </div>
              <div class="rhe">
                <div class="rhe-header">
                  <span>R</span><span>H</span><span>E</span>
                </div>
                <div class="rhe-row">
                  <span><b>${game.rhe.away.R}</b></span>
                  <span>${game.rhe.away.H}</span>
                  <span>${game.rhe.away.E}</span>
                </div>
                <div class="rhe-row">
                  <span><b>${game.rhe.home.R}</b></span>
                  <span>${game.rhe.home.H}</span>
                  <span>${game.rhe.home.E}</span>
                </div>
              </div>
              <div class="bag">
                ${ game.bag }
              </div>
            </div>
          </div>
        `;
        container.insertAdjacentHTML('beforeend', gameHTML);

        document.addEventListener('DOMContentLoaded', function () {
  // 選出所有 class="bag" 的元素
  document.querySelectorAll('.bag').forEach(function(bagDiv) {
    // 檢查是否有內容（去除空白後長度大於 0）
    if (bagDiv.innerHTML.trim().length > 0) { // [4][7]
      // 建立新的 div
      var rheRow = document.createElement('div');
      rheRow.className = 'bag-inner-space';
      // 插入到 bagDiv 最前面
      bagDiv.insertBefore(rheRow, bagDiv.firstChild); // [5][6]
    }
  });
  document.querySelectorAll('.bag').forEach(function(bagDiv) {
    // 檢查內容是否為空（去除空白後長度大於 0）
    if (bagDiv.innerHTML.trim().length > 0) {
      // 建立新的 div
      var rheRow = document.createElement('div');
      rheRow.className = 'bag-space';
      // 將 rheRow 插入到 bagDiv 的前面（bag 的父元素下）
      bagDiv.parentNode.insertBefore(rheRow, bagDiv);
    }
  });
})
      });
    }
  })();

