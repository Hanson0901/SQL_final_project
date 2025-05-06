function searchComposite() {
    const type = document.getElementById('query-type').value;
    const keyword = document.getElementById('keyword').value.trim();
    const typeText = document.getElementById('query-type').options[
      document.getElementById('query-type').selectedIndex
    ].text;
  
    if (!keyword) {
      alert("請輸入關鍵字！");
      return;
    }
  
    // 模擬導向查詢結果（你可以改成 location.href = "..."）
    alert(`🔎 查詢類型：${typeText}\n關鍵字：${keyword}\n即將導向對應資料頁面...`);
    
    const encodedKeyword = encodeURIComponent(keyword);
    location.href = `/result?type=${type}&keyword=${encodedKeyword}`;

}

  
function resetForm() {
    document.getElementById('query-type').selectedIndex = 0;
    document.getElementById('keyword').value = "";
}
  