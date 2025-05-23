document.addEventListener('DOMContentLoaded', function () {
    // 定義 flags 陣列，改為 static 路徑
    const flags = [
        { src: "/static/img/BWF/Flag_of_Chinese_Taipei_for_Olympic_Games.svg.webp", n: 0 },
        { src: "/static/img/BWF/Flag_of_Denmark.svg.webp", n: 1 },
        { src: "/static/img/BWF/Flag_of_Singapore.svg.webp", n: 2 },
        { src: "/static/img/BWF/Flag_of_Thailand.svg.webp", n: 3 },
        { src: "/static/img/BWF/Flag_of_the_People's_Republic_of_China.svg.webp", n: 4 },
        { src: "/static/img/BWF/Flag_of_Japan.svg.webp", n: 5 }
    ];

    document.querySelectorAll('.team-logo-block').forEach(function (block) {
        // 取得 svg-preview 與 svg-modal
        const preview = block.querySelector('.svg-preview');
        const modal = block.querySelector('.svg-modal');
        const closeBtn = block.querySelector('.close-modal-btn');
        const logoList = block.querySelector('.logo-list');
        const select = block.querySelector('.svg-select');

        // 產生 logoList 內容
        if (logoList && logoList.children.length === 0) {
            flags.forEach(function (flag) {
                const img = document.createElement('img');
                img.src = flag.src;
                img.setAttribute('data-n', flag.n);
                logoList.appendChild(img);
            });
        }

        // 預設顯示第一個 logo
        function setLogoByIndex(idx) {
            let label = flags[idx] ? flags[idx].src.split('/').pop() : "";
            preview.innerHTML = `<img src="/static/img/BWF/${label}" style="width:32px;height:32px;">`;
            if (select) select.value = idx;
        }

        // 預設顯示第0個
        setLogoByIndex(0);

        // 點擊預覽開啟 modal
        preview.addEventListener('click', function () {
            modal.style.display = 'block';
        });

        // 點擊關閉按鈕關閉 modal
        closeBtn.addEventListener('click', function () {
            modal.style.display = 'none';
        });

        // 點擊 logo 選擇
        logoList.querySelectorAll('img').forEach(function (img) {
            img.addEventListener('click', function () {
                const idx = parseInt(img.getAttribute('data-n'), 10);
                setLogoByIndex(idx);
                modal.style.display = 'none';
            });
        });

        // select 下拉選單選擇
        if (select) {
            select.addEventListener('change', function () {
                setLogoByIndex(parseInt(select.value, 10));
            });
        }
    });
});