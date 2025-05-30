const API_URL = 'https://localhost:5000/app/NBAscore';
// fetchScore();
function formatDateTime(date) {
  const year = date.getFullYear();
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const day = date.getDate().toString().padStart(2, '0');
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  const seconds = date.getSeconds().toString().padStart(2, '0');
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

async function fetchScore() {
  try {
    const response = await fetch(API_URL);
    const data = await response.json();

    if (data.error) {
      console.error('API 錯誤:', data.error);
      return;
    }

    document.getElementById('home-name').textContent = data.home_team;
    document.getElementById('away-name').textContent = data.away_team;
    document.getElementById('home-score').textContent = data.home_score;
    document.getElementById('away-score').textContent = data.away_score;
    document.getElementById('home-flag').src = data.home_flag;
    document.getElementById('away-flag').src = data.away_flag;
    document.getElementById('game-status').textContent = data.game_status || 'N/A';
    document.getElementById('series').textContent = data.series || 'N/A';
    document.getElementById('home-team-rank').textContent = data.home_team_rank || 'N/A';
    document.getElementById('away-team-rank').textContent = data.away_team_rank || 'N/A';
    document.getElementById('playoff-round').textContent = data.playoff_round || 'N/A';
    document.getElementById('game-number').textContent = data.game_number || 'N/A';
    
    const now = new Date();
    document.getElementById('last-update-time').textContent =
      '上次更新時間：' + formatDateTime(now);

    const homeScore = Number(data.home_score);
    const awayScore = Number(data.away_score);
    const gameStatus = data.game_status;
    const scoreArrow = document.getElementById('score-arrow');
    
    const rightArrowSVG = `
    <svg xmlns="http://www.w3.org/2000/svg" width="7" height="12" viewBox="0 0 7 12" class="GameCardMatchup_awayWin__zD021 GameCardMatchup_won__89eVM" data-no-icon="left" role="presentation">
      <path fill="currentColor" fill-rule="nonzero" d="M.5 6l6 5.5V.5z"></path>
    </svg>
    `;

    
    const leftArrowSVG = `
   <svg xmlns="http://www.w3.org/2000/svg" width="7" height="12" viewBox="0 0 7 12" class="GameCardMatchup_homeWin__5E_iM" data-no-icon="right" role="presentation">
      <path fill="currentColor" fill-rule="nonzero" d="M.5 6l6 5.5V.5z"></path>
   </svg>
    `;
    
    if (gameStatus === 'FINAL') {
        if (homeScore > awayScore) {
            scoreArrow.innerHTML = leftArrowSVG;  // 指向主隊
        } else if (homeScore < awayScore) {
            scoreArrow.innerHTML = rightArrowSVG; // 指向客隊
        } else {
            scoreArrow.innerHTML = '';
        }
    } else {
        scoreArrow.innerHTML = '';
    }
      

  } catch (error) {
    console.error('取得比分失敗:', error);
  }
}

fetchScore();
setInterval(fetchScore, 10000);