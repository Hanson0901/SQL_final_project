document.addEventListener('DOMContentLoaded', function () {
    // 國旗選項
    const flags = [
        { src: "Flag_of_Chinese_Taipei_for_Olympic_Games.svg.webp", n: 0 },
        { src: "Flag_of_Denmark.svg.webp", n: 1 },
        { src: "Flag_of_Singapore.svg.webp", n: 2 },
        { src: "Flag_of_Thailand.svg.webp", n: 3 },
        { src: "Flag_of_the_People's_Republic_of_China.svg.webp", n: 4 },
        { src: "Flag_of_Japan.svg.webp", n: 5 }
    ];

    // 載入分數與國旗
    fetch('/get_bwf_simple')
        .then(res => res.json())
        .then(data => {
            document.querySelectorAll('.match-card').forEach(function(card, idx) {
                // 設定 flag1
                let team1Logo = card.querySelector('.team1-logo .svg-preview');
                if (team1Logo && data[idx] && data[idx].flag1) {
                    team1Logo.innerHTML = `<img src="/static/img/BWF/${data[idx].flag1}" style="width:32px;height:32px;">`;
                }
                // 設定 flag2
                let team2Logo = card.querySelector('.team2-logo .svg-preview');
                if (team2Logo && data[idx] && data[idx].flag2) {
                    team2Logo.innerHTML = `<img src="/static/img/BWF/${data[idx].flag2}" style="width:32px;height:32px;">`;
                }
                // 設定 score1
                let score1Spans = card.querySelectorAll('.player-row .score div span[contenteditable="true"]');
                if (score1Spans.length && data[idx] && data[idx].score1) {
                    data[idx].score1.forEach((val, i) => {
                        if (score1Spans[i]) score1Spans[i].textContent = val;
                    });
                }
                // 設定 score2
                let playerRows = card.querySelectorAll('.player-row');
                if (playerRows.length > 1) {
                    let score2Spans = playerRows[1].querySelectorAll('.score div span[contenteditable="true"]');
                    if (score2Spans.length && data[idx] && data[idx].score2) {
                        data[idx].score2.forEach((val, i) => {
                            if (score2Spans[i]) score2Spans[i].textContent = val;
                        });
                    }
                }
            });
        });

    // 國旗選擇功能
    document.querySelectorAll('.team-logo-block').forEach(function (block) {
        const preview = block.querySelector('.svg-preview');
        const modal = block.querySelector('.svg-modal');
        const closeBtn = block.querySelector('.close-modal-btn');
        const logoList = block.querySelector('.logo-list');
        const select = block.querySelector('.svg-select');

        // 產生國旗選單
        if (logoList && logoList.children.length === 0) {
            flags.forEach(function (flag, idx) {
                const img = document.createElement('img');
                img.src = "/static/img/BWF/" + flag.src;
                img.setAttribute('data-n', idx);
                logoList.appendChild(img);
            });
        }

        function setLogoByIndex(idx) {
            let label = flags[idx] ? flags[idx].src : "";
            preview.innerHTML = `<img src="/static/img/BWF/${label}" style="width:32px;height:32px;">`;
            if (select) select.value = idx;
            // 觸發自動儲存
            saveAllMatchData();
        }

        // 預設第一個
        setLogoByIndex(0);

        preview.addEventListener('click', function () {
            modal.style.display = 'block';
        });

        closeBtn.addEventListener('click', function () {
            modal.style.display = 'none';
        });

        logoList.querySelectorAll('img').forEach(function (img) {
            img.addEventListener('click', function () {
                const idx = parseInt(img.getAttribute('data-n'), 10);
                setLogoByIndex(idx);
                modal.style.display = 'none';
            });
        });

        if (select) {
            select.addEventListener('change', function () {
                setLogoByIndex(parseInt(select.value, 10));
            });
        }
    });

    // 監聽分數變動自動儲存
    document.addEventListener('input', function (e) {
        if (e.target.matches('span[contenteditable="true"][data-score]')) {
            saveAllMatchData();
        }
    });

    // 監聽國旗下拉選單變動自動儲存
    document.addEventListener('change', function (e) {
        if (e.target.matches('.svg-select')) {
            saveAllMatchData();
        }
    });

    // 收集所有比賽的分數與國旗
    function collectAllMatchData() {
    const cards = document.querySelectorAll('.match-card');
    const data = [];
    cards.forEach(card => {
        // 國旗
        let flag1 = "";
        let flag2 = "";
        let team1Select = card.querySelector('.team1-logo .svg-select');
        let team2Select = card.querySelector('.team2-logo .svg-select');
        if (team1Select) {
            let idx = parseInt(team1Select.value, 10);
            flag1 = flags[idx]?.src || "";
        }
        if (team2Select) {
            let idx = parseInt(team2Select.value, 10);
            flag2 = flags[idx]?.src || "";
        }
        // 分數
        let score1Spans = card.querySelectorAll('.player-row .score div span[contenteditable="true"]');
        let score1 = Array.from(score1Spans).map(span => parseInt(span.textContent.trim(), 10) || 0);
        let playerRows = card.querySelectorAll('.player-row');
        let score2 = [];
        if (playerRows.length > 1) {
            let score2Spans = playerRows[1].querySelectorAll('.score div span[contenteditable="true"]');
            score2 = Array.from(score2Spans).map(span => parseInt(span.textContent.trim(), 10) || 0);
        }
        // 只收集有內容的卡片（有分數或有國旗）
        const hasScore = score1.some(s => s > 0) || score2.some(s => s > 0);
        const hasFlag = flag1 !== "" || flag2 !== "";
        if (hasScore || hasFlag) {
            data.push({ flag1, flag2, score1, score2 });
        }
    });
    return data;
}

    // 儲存所有比賽資料到後端
    function saveAllMatchData() {
        const data = collectAllMatchData();
        fetch('/update_bwf_simple', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    }
});