
  async function goToSQL() {
    const res = await fetch('/sql');
    if (res.ok) {
      window.location.href = '/sql';
    } else {
      alert('無法前往 SQL 操作區');
    }
  }

  async function goToAnnouncements() {
    const res = await fetch('/announcements');
    if (res.ok) {
      window.location.href = '/announcements';
    } else {
      alert('無法載入公告管理');
    }
  }

  async function goToFeedback() {
    const res = await fetch('/feedback');
    if (res.ok) {
      window.location.href = '/feedback';
    } else {
      alert('載入意見回饋失敗');
    }
  }

  async function goToUpdateSummary() {
    const res = await fetch('/update-summary');
    if (res.ok) {
      window.location.href = '/update-summary';
    } else {
      alert('無法取得更新摘要');
    }
  }
