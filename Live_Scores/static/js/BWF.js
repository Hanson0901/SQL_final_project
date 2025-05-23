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
        const response = await fetch('http://127.0.0.1:5000/app/BWFscore');
        const data = await response.json();

        // 如果賽事數量不同，重建 li 結構
        if (data.length !== lastMatchCount) {
            ul.innerHTML = '';
            data.forEach((match, idx) => {
                const li = document.createElement('li');
                li.className = 'bwf-match-item';
                li.id = `match-${idx}`;
                li.innerHTML = renderMatchHTML(match, idx);
                ul.appendChild(li);
            });
            lastMatchCount = data.length;
        } else {
            // 只更新內容，不重建節點
            data.forEach((match, idx) => {
                const li = document.getElementById(`match-${idx}`);
                if (li) {
                    li.innerHTML = renderMatchHTML(match, idx);
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

// 國旗選項
const flagOptions = [
    "Flag_of_Chinese_Taipei_for_Olympic_Games.svg.webp",
    "Flag_of_Denmark.svg.webp",
    "Flag_of_Singapore.svg.webp",
    "Flag_of_Thailand.svg.webp",
    "Flag_of_the_People's_Republic_of_China.svg.webp",
    "Flag_of_Japan.svg.webp"
];
function renderFlagSelect(selected) {
    return `<select class="bwf-flag-select">
        ${flagOptions.map(f => `<option value="${f}" ${selected===f?'selected':''}>${f.replace('Flag_of_','').replace('.svg.webp','')}</option>`).join('')}
    </select>`;
}
function renderScore(scores, prefix) {
    return (scores || []).map((s,i) => `<span class="bwf-score-edit" contenteditable="true" data-score="${prefix}-${i}">${s}</span>`).join(' ');
}

function renderMatchHTML(match, idx) {
    // 判斷雙打
    const isDouble = (match.player2 && match.player2.trim()) && (match.player4 && match.player4.trim());
    const [dot1, dot2] = getActiveDot(match.score1, match.score2);

    const now = new Date();
    const updateTime = document.getElementById('last-update-time');
    if (updateTime) {
        updateTime.textContent = '上次更新時間：' + formatDateTime(now);
    }
    // 綠色圓點
    const dotHTML = `<span class="bwf-dot active"></span>`;

    // 單打
    if (!isDouble) {
        return `
        <div class="bwf-court-row">
            <span>${match.court || ''}</span>
            <div>
                ${match.animated_gif ? `<img class="bwf-animated-gif" src="${match.animated_gif}" alt="animated gif">` : ""}
                <span class="bwf-match-time">${match.game_time || 'N/A'}</span>
            </div>
        </div>
        <div class="bwf-player-row">
            <div class="bwf-player">
                <img class="bwf-flag" src="static/img/BWF/${match.flag1}" alt="flag">
                ${renderFlagSelect(match.flag1)}
                <span class="bwf-player-names">${match.player1 || ''}</span>
                <div class="bwf-score-row">
                    ${dot1 ? dotHTML : ""}
                    ${renderScore(match.score1, "score1")}
                </div>
            </div>
            <div class="bwf-player">
                <img class="bwf-flag" src="static/img/BWF/${match.flag2 || ''}" alt="flag">
                ${renderFlagSelect(match.flag2)}
                <span class="bwf-player-names">${match.player3 || ''}</span>
                <div class="bwf-score-row">
                    ${dot2 ? dotHTML : ""}
                    ${renderScore(match.score2, "score2")}
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
            <span>${match.court || ''}</span>
            <div>
                ${match.animated_gif ? `<img class="bwf-animated-gif" src="${match.animated_gif}" alt="animated gif">` : ""}
                <span class="bwf-match-time">${match.game_time || 'N/A'}</span>
            </div>
        </div>
        <div class="bwf-player-row">
            <div class="bwf-player">
                <img class="bwf-flag" src="static/img/BWF/${match.flag1}" alt="flag">
                ${renderFlagSelect(match.flag1)}
                <span class="bwf-player-names">
                    ${match.player1 || ''}<br>
                    ${match.player2 || ''}
                </span>
                <div class="bwf-score-row">
                    ${dot1 ? dotHTML : ""}
                    ${renderScore(match.score1, "score1")}
                </div>
            </div>
            <div class="bwf-player">
                <img class="bwf-flag" src="static/img/BWF/${match.flag2 || ''}" alt="flag">
                ${renderFlagSelect(match.flag2)}
                <span class="bwf-player-names">
                    ${match.player3 || ''}<br>
                    ${match.player4 || ''}
                </span>
                <div class="bwf-score-row">
                    ${dot2 ? dotHTML : ""}
                    ${renderScore(match.score2, "score2")}
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

// 收集所有比賽的分數與國旗
function collectAllMatchData() {
    const lis = document.querySelectorAll('.bwf-match-item');
    const data = [];
    lis.forEach(li => {
        // 國旗
        const selects = li.querySelectorAll('.bwf-flag-select');
        const flag1 = selects[0]?.value || "";
        const flag2 = selects[1]?.value || "";
        // 分數
        const score1 = Array.from(li.querySelectorAll('[data-score^="score1"]')).map(span => parseInt(span.textContent.trim(),10)||0);
        const score2 = Array.from(li.querySelectorAll('[data-score^="score2"]')).map(span => parseInt(span.textContent.trim(),10)||0);
        data.push({flag1, flag2, score1, score2});
    });
    return data;
}

// 儲存所有比賽資料到後端
function saveAllMatchData() {
    const data = collectAllMatchData();
    fetch('/update_bwf_simple', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(data)
    });
}

// 監聽分數與國旗變動，自動儲存
document.addEventListener('input', function(e){
    if(e.target.matches('.bwf-score-edit')) saveAllMatchData();
});
document.addEventListener('change', function(e){
    if(e.target.matches('.bwf-flag-select')) saveAllMatchData();
});

// 初始化
fetchAndRenderBWF();
setInterval(fetchAndRenderBWF, 20000);