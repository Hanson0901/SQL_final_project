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
    
    document.querySelectorAll('.score-block').forEach(function(card) {
        const score1Span = card.querySelector('.score1');
        const score2Span = card.querySelector('.score2');
        const plus1 = card.querySelector('.score1-plus');
        const minus1 = card.querySelector('.score1-minus');
        const plus2 = card.querySelector('.score2-plus');
        const minus2 = card.querySelector('.score2-minus');
        if (score1Span && plus1 && minus1) {
            plus1.addEventListener('click', function() {
                score1Span.textContent = parseInt(score1Span.textContent) + 1;
            });
            minus1.addEventListener('click', function() {
                score1Span.textContent = Math.max(0, parseInt(score1Span.textContent) - 1);
            });
        }
        if (score2Span && plus2 && minus2) {
            plus2.addEventListener('click', function() {
                score2Span.textContent = parseInt(score2Span.textContent) + 1;
            });
            minus2.addEventListener('click', function() {
                score2Span.textContent = Math.max(0, parseInt(score2Span.textContent) - 1);
            });
        }
    });

});