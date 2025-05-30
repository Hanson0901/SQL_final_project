function formatDateTime(date) {
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const seconds = date.getSeconds().toString().padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  }
  

let lastMatchCount = 0;

async function fetchAndRenderBWF() {
  const ul = document.getElementById('bwf-match-list');
  try {
    const response = await fetch('https://34.80.207.190:5000/app/BWFscore');
    const data = await response.json();

    // 如果賽事數量不同，重建 li 結構
    if (data.length !== lastMatchCount) {
      ul.innerHTML = '';
      data.forEach((match, idx) => {
        const li = document.createElement('li');
        li.className = 'bwf-match-item';
        li.id = `match-${idx}`;
        li.innerHTML = renderMatchHTML(match);
        ul.appendChild(li);
      });
      lastMatchCount = data.length;
    } else {
      // 只更新內容，不重建節點
      data.forEach((match, idx) => {
        const li = document.getElementById(`match-${idx}`);
        if (li) {
          li.innerHTML = renderMatchHTML(match);
        }
      });
    }
  } catch (e) {
    ul.innerHTML = '<li>資料載入失敗</li>';
    lastMatchCount = 0;
  }
}

// 只比第一局分數，決定誰顯示綠點
function getActiveDot(score1, score2) {
  const s1 = parseInt(score1 && score1[0] ? score1[0] : "0", 10);
  const s2 = parseInt(score2 && score2[0] ? score2[0] : "0", 10);
  if (s1 > s2) return [true, false];
  if (s2 > s1) return [false, true];
  return [false, false];
}

function renderMatchHTML(match) {
    // 判斷雙打
    const isDouble = (match.player2 && match.player2.trim()) && (match.player4 && match.player4.trim());
    const [dot1, dot2] = getActiveDot(match.score1, match.score2);
  
    // 分數渲染
    function renderScore(scores) {
      return (scores || []).map(s => `<span>${s}</span>`).join(' ');
    }
  
    const now = new Date();
    document.getElementById('last-update-time').textContent =
      '上次更新時間：' + formatDateTime(now);
    // 綠色圓點
    const dotHTML = `<span class="bwf-dot active"></span>`;
  
    // 單打
    if (!isDouble) {
      return `
        <div class="bwf-court-row">
          <span>${match.court}</span>
          <div>
            ${match.animated_gif ? `<img class="bwf-animated-gif" src="${match.animated_gif}" alt="animated gif">` : ""}
            <span class="bwf-match-time">${match.game_time || 'N/A'}</span>
          </div>
         
        </div>
        <div class="bwf-player-row">
          <div class="bwf-player">
            <img class="bwf-flag" src="${match.flag1}" alt="flag">
            <span class="bwf-player-names">${match.player1}</span>
            <div class="bwf-score-row">
              ${dot1 ? dotHTML : ""}
              ${renderScore(match.score1)}
            </div>
          </div>
          <div class="bwf-player">
            <img class="bwf-flag" src="${match.flag2 || ''}" alt="flag">
            <span class="bwf-player-names">${match.player3}</span>
            <div class="bwf-score-row">
              ${dot2 ? dotHTML : ""}
              ${renderScore(match.score2)}
            </div>
          </div>
        </div>
        <div class="bwf-match-info">
          <span class="bwf-match-type">${match.round_oop || 'N/A'}</span>
          <span class="bwf-match-status">${match.round_status || 'N/A'}</span>
          
        </div>
      `;
    } else {
      // 雙打
      return `
        <div class="bwf-court-row">
          <span>${match.court}</span>
            <div>
              ${match.animated_gif ? `<img class="bwf-animated-gif" src="${match.animated_gif}" alt="animated gif">` : ""}
              <span class="bwf-match-time">${match.game_time || 'N/A'}</span>
          </div>
        </div>
        <div class="bwf-player-row">
          <div class="bwf-player">
            <img class="bwf-flag" src="${match.flag1}" alt="flag">
            <span class="bwf-player-names">
              ${match.player1}<br>
              ${match.player2}
            </span>
            <div class="bwf-score-row">
              ${dot1 ? dotHTML : ""}
              ${renderScore(match.score1)}
            </div>
          </div>
          <div class="bwf-player">
            <img class="bwf-flag" src="${match.flag2 || ''}" alt="flag">
            <span class="bwf-player-names">
              ${match.player3}<br>
              ${match.player4}
            </span>
            <div class="bwf-score-row">
              ${dot2 ? dotHTML : ""}
              ${renderScore(match.score2)}
            </div>
          </div>
        </div>
        <div class="bwf-match-info">
          <span class="bwf-match-type">${match.round_oop || 'N/A'}</span>
          <span class="bwf-match-status">${match.round_status || 'N/A'}</span>
          
        </div>
      `;
    }
  }

// 初始化
fetchAndRenderBWF();
setInterval(fetchAndRenderBWF, 10000);
