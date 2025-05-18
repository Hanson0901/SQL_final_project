        function updateData() {
            $.getJSON('/get_live_data', function(data) {
                $('#last-updated').text(`Last Updated: ${data.last_updated}`);
                
                let html = '';
                data.data.forEach(row => {
                    html += `
                    <tr class="text-center align-middle driver-row">
                        <td>${row.Position}</td>
                        <td>
                            <span class="team-color-bar" style="background:${row.TeamColor};"></span>
                            ${row.Driver}
                        </td>
                        <td>${row.Team}</td>
                        <td>${row.Gap}</td>
                        <td>${row.Tyre}</td>
                        <td>${row.Tyres_Used}</td>
                    </tr>
                    `;
                });
                $('#timing-data').html(html);
            });
        }

        // 初始載入
        updateData();
        // 每3秒更新一次
        setInterval(updateData, 10000);
