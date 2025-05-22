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
        
        // [' ','Brooklyn Nets', 'New York Knicks', 'Philadelphia 76ers', 'Toronto Raptors',
        //     'Chicago Bulls', 'Cleveland Cavaliers', 'Detroit Pistons', 'Indiana Pacers',
        //     'Milwaukee Bucks', 'Atlanta Hawks', 'Charlotte Hornets', 'Miami Heat',
        //     'Orlando Magic', 'Washington Wizards', 'Denver Nuggets', 'Minnesota Timberwolves',
        //     'Oklahoma City Thunder', 'Portland Trail Blazers', 'Utah Jazz', 'Golden State Warriors',
        //     'Los Angeles Clippers', 'Los Angeles Lakers', 'Phoenix Suns', 'Sacramento Kings',
        //     'Dallas Mavericks', 'Houston Rockets', 'Memphis Grizzlies', 'New Orleans Pelicans',
        //     'San Antonio Spurs'
        // ]
        const select = block.querySelector('.svg-select');
        const preview = block.querySelector('.svg-preview');
        const modal = block.querySelector('.svg-modal');
        const closeBtn = block.querySelector('.close-modal-btn');
        function updatePreview() {
            const n = select.value;
            const path = `/static/img/NBA/logo(${n}).svg`;
            preview.innerHTML = `<img src="${path}" alt="logo${n}" style="max-width:50px;max-height:50px;">`;
            const teamName = name_list[n] || '';
            preview.innerHTML = `
                <img src="${path}" alt="logo${n}" style="max-width:50px;max-height:50px;">`;
            const teamNameDiv = block.querySelector('.team1-name') || block.querySelector('.team2-name');
            if (teamNameDiv) {
                teamNameDiv.textContent = name_list[n] || '';
            }
            }
        if(select && preview){
            select.addEventListener('change', updatePreview);
            updatePreview();
        }
        preview.addEventListener('click', function(){
            modal.style.display = 'flex';
        });
        modal.addEventListener('click', function(e){
            if(e.target.tagName === 'IMG' && e.target.dataset.n){
                select.value = e.target.dataset.n;
                updatePreview();
                modal.style.display = 'none';
            }
            if(e.target === modal){
                modal.style.display = 'none';
            }
        });
        closeBtn.addEventListener('click', function(){
            modal.style.display = 'none';
        });
    });
    fetch('/get_score')
        .then(res => res.json())
        .then(data => {
            document.querySelectorAll('.score1').forEach(el => el.textContent = data.score1);
            document.querySelectorAll('.score2').forEach(el => el.textContent = data.score2);
             // 設定 logo 下拉選單與預覽
            document.querySelectorAll('.team1-logo .svg-select').forEach(sel => sel.value = data.logo1 ?? 0);
            document.querySelectorAll('.team2-logo .svg-select').forEach(sel => sel.value = data.logo2 ?? 1);
        });
    function updateLogo() {
            const logo1 = parseInt(document.querySelector('.team1-logo .svg-select').value);
            const logo2 = parseInt(document.querySelector('.team2-logo .svg-select').value);
            fetch('/update_score', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ logo1, logo2 })
            })
            .then(res => res.json())
            .then(data => {
                // 可選：同步更新預覽或其他 UI
            });
        }
    // 當 logo 選擇改變時，發送 AJAX 更新
    document.querySelectorAll('.team1-logo .svg-select').forEach(sel => {
        sel.addEventListener('change', function() {
            updateLogo();
        });
    });
    document.querySelectorAll('.team2-logo .svg-select').forEach(sel => {
        sel.addEventListener('change', function() {
            updateLogo();
        });
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
            fetch('/update_score', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ score1, score2 })
            })
                .then(res => res.json())
                .then(data => {
                    score1Span.textContent = data.score1;
                    score2Span.textContent = data.score2;
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