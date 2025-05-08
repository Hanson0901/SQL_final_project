function formatLocalTime(utcTimeString, offsetHours = -12) {
    const date = new Date(utcTimeString);
    date.setHours(date.getHours() + offsetHours);
    return date.toISOString().slice(11, 16);
  }
  
  (function autoRefresh() {
    const pageDate = window.pageDate;
    const today = new Date().toISOString().split('T')[0];
    console.log('pageDate:', pageDate, 'today:', today);
    if (pageDate !== today) return;
  
    const refreshInterval = setInterval(() => {
      console.log('定時刷新觸發:', new Date().toLocaleTimeString());
      fetch(`/finalpj/api/mlb_games?date=${today}&_=${Date.now()}`, {
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
    }, 60000);

    // 更新頁面內容的函數
    function updateGames(games) {
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
            </div>
          </div>
        `;
        container.insertAdjacentHTML('beforeend', gameHTML);
      });
    }
  })();

