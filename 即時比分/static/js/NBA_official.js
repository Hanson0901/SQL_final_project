document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.team-logo-block').forEach(function(block) {
        const name_list =['Celtics','Nets', 'Knicks', 'Philadelphia', 'Raptors',
                            'Bulls', 'Cavaliers', 'Pistons', 'Pacers',
                            'Bucks', 'Hawks', 'Hornets', 'Heat',
                            'Magic', 'Wizards', 'Nuggets', 'Timberwolves',
                            'Thunder', 'Blazers', 'Jazz', 'Warriors',
                            'Clippers', 'Lakers', 'Suns', 'Kings',
                            'Mavericks', 'Rockets', 'Grizzlies', 'Pelicans',
                            'Spurs'
                        ]
        const select = block.querySelector('.svg-select');
        const preview = block.querySelector('.svg-preview');
        const modal = block.querySelector('.svg-modal');
        const closeBtn = block.querySelector('.close-modal-btn');
        // 將 updatePreview 抽出，方便外部呼叫
        block.updatePreview = function() {
            const n = select.value;
            const path = `/static/img/NBA/logo(${n}).svg`;
            preview.innerHTML = `<img src="${path}" alt="logo${n}" style="max-width:50px;max-height:50px;">`;
            const teamNameDiv = block.querySelector('.team1-name') || block.querySelector('.team2-name');
            if (teamNameDiv) {
                teamNameDiv.textContent = name_list[n] || '';
            }
        }
        if(select && preview){
            select.addEventListener('change', block.updatePreview);
            block.updatePreview();
        }
        preview.addEventListener('click', function(){
            modal.style.display = 'flex';
        });
        modal.addEventListener('click', function(e){
            if(e.target.tagName === 'IMG' && e.target.dataset.n){
                select.value = e.target.dataset.n;
                block.updatePreview();
                modal.style.display = 'none';
                updateLogo(); // 新增：確保 modal 點選 logo 也會觸發 updateLogo
            }
            if(e.target === modal){
                modal.style.display = 'none';
            }
        });
        closeBtn.addEventListener('click', function(){
            modal.style.display = 'none';
        });
    });

    // fetch 分數與 logo，並更新畫面
    fetch('/get_score')
        .then(res => res.json())
        .then(data => {
            document.querySelectorAll('.score1').forEach(el => el.textContent = data.score1);
            document.querySelectorAll('.score2').forEach(el => el.textContent = data.score2);
            // 設定 logo 下拉選單與預覽
            document.querySelectorAll('.team1-logo .svg-select').forEach(sel => {
                sel.value = data.logo1 ?? 0; // 若 data.logo1 存在則用它，否則預設 0
                sel.closest('.team-logo-block').updatePreview();
            });
            document.querySelectorAll('.team2-logo .svg-select').forEach(sel => {
                sel.value = data.logo2 ?? 1; // 若 data.logo2 存在則用它，否則預設 1
                sel.closest('.team-logo-block').updatePreview();
            });
        });

    function updateLogo() {
        console.log('updateLogo called'); // 放在最前面，確認有無進入函式
        const logo1 = parseInt(document.querySelector('.team1-logo .svg-select').value);
        const logo2 = parseInt(document.querySelector('.team2-logo .svg-select').value);
        console.log('logo1:', logo1, 'logo2:', logo2); // 印出目前選擇
        // 取得目前分數
        const score1 = parseInt(document.querySelector('.score1').textContent) || 0;
        const score2 = parseInt(document.querySelector('.score2').textContent) || 0;
        console.log('updateLogo'); // 應放在這裡
        // 取得目前選擇的 logo
        console.log('logo1:', logo1, 'logo2:', logo2); // 一起印出
        fetch('/update_score', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ logo1, logo2, score1, score2 })
        })
        .then(res => res.json())
        .then(data => {
            // 同步更新 logo 預覽與隊名
            document.querySelectorAll('.team1-logo').forEach(block => block.updatePreview());
            document.querySelectorAll('.team2-logo').forEach(block => block.updatePreview());
            // 分數也同步
            document.querySelectorAll('.score1').forEach(el => el.textContent = data.score1);
            document.querySelectorAll('.score2').forEach(el => el.textContent = data.score2);
        });
    }

    // 當 logo 選擇改變時，發送 AJAX 更新
    document.querySelectorAll('.team1-logo .svg-select').forEach(sel => {
        sel.addEventListener('change', function() {
            console.log('team1 select changed'); // 新增：確認事件有無觸發
            updateLogo();
        });
        // console.log(sel.value); // 如需除錯可取消註解
    });
    document.querySelectorAll('.team2-logo .svg-select').forEach(sel => {
        sel.addEventListener('change', function() {
            console.log('team2 select changed'); // 新增：確認事件有無觸發
            updateLogo();
        });
        // console.log(sel.value); // 如需除錯可取消註解
    });

    document.querySelectorAll('.score-block').forEach(function(card) {
        const score1Span = card.querySelector('.score1');
        const score2Span = card.querySelector('.score2');
        const plus1 = card.querySelector('.score1-plus');
        const minus1 = card.querySelector('.score1-minus');
        const plus2 = card.querySelector('.score2-plus');
        const minus2 = card.querySelector('.score2-minus');
        function updateScore(delta1, delta2) {
            let score1 = parseInt(score1Span.textContent);
            let score2 = parseInt(score2Span.textContent);
            if (isNaN(score1)) score1 = 0;
            if (isNaN(score2)) score2 = 0;
            score1 += delta1;
            score2 += delta2;
            if (score1 < 0) score1 = 0;
            if (score2 < 0) score2 = 0;
            const logo1 = parseInt(document.querySelector('.team1-logo .svg-select').value);
            const logo2 = parseInt(document.querySelector('.team2-logo .svg-select').value);
            fetch('/update_score', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ score1, score2 ,logo1, logo2 })
            })
                .then(res => res.json())
                .then(data => {
                    score1Span.textContent = data.score1;
                    score2Span.textContent = data.score2;
                    // 分數更新後，也同步更新 logo 與隊名
                    document.querySelectorAll('.team1-logo').forEach(block => block.updatePreview());
                    document.querySelectorAll('.team2-logo').forEach(block => block.updatePreview());
                });
        }

        if (score1Span && plus1 && minus1) {
            plus1.addEventListener('click', function() { updateScore(1, 0); });
            minus1.addEventListener('click', function() { updateScore(-1, 0); });
        }
        if (score2Span && plus2 && minus2) {
            plus2.addEventListener('click', function() { updateScore(0, 1); });
            minus2.addEventListener('click', function() { updateScore(0, -1); });
        }
    });
    

});