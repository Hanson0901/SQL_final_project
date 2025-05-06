document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
  
    const res = await fetch('/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, password })
    });
  
    const data = await res.json();
    if (data.success) {
      window.location.href = '/control_panel';  // ✅ 登入成功跳轉
    } else {
      alert('帳號或密碼錯誤');
    }
  });