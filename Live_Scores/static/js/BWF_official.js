document.addEventListener('DOMContentLoaded', function () {
    // 國旗選項
    const flags = [
        { src: "/static/img/BWF/Flag_of_Chinese_Taipei_for_Olympic_Games.svg.webp", n: 0 },
        { src: "/static/img/BWF/Flag_of_Denmark.svg.webp", n: 1 },
        { src: "/static/img/BWF/Flag_of_Singapore.svg.webp", n: 2 },
        { src: "/static/img/BWF/Flag_of_Thailand.svg.webp", n: 3 },
        { src: "/static/img/BWF/Flag_of_the_People's_Republic_of_China.svg.webp", n: 4 },
        { src: "/static/img/BWF/Flag_of_Japan.svg.webp", n: 5 }
    ];

    // 取得比賽資料
    fetch('/get_bwf_simple')
        .then(res => res.json())
        .then(data => {
            // 假設每個比賽卡片有唯一 data-match-index
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

    // 以下為國旗選擇功能（如你原本的）
    document.querySelectorAll('.team-logo-block').forEach(function (block) {
        const preview = block.querySelector('.svg-preview');
        const modal = block.querySelector('.svg-modal');
        const closeBtn = block.querySelector('.close-modal-btn');
        const logoList = block.querySelector('.logo-list');
        const select = block.querySelector('.svg-select');

        if (logoList && logoList.children.length === 0) {
            flags.forEach(function (flag) {
                const img = document.createElement('img');
                img.src = flag.src;
                img.setAttribute('data-n', flag.n);
                logoList.appendChild(img);
            });
        }

        function setLogoByIndex(idx) {
            let label = flags[idx] ? flags[idx].src.split('/').pop() : "";
            preview.innerHTML = `<img src="/static/img/BWF/${label}" style="width:32px;height:32px;">`;
            if (select) select.value = idx;
        }

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
});