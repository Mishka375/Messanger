const app = document.getElementById('app');
const API = '/api';

// ---------- Роутер ----------
async function loadPage(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error('not found');
    app.innerHTML = await res.text();

    // Вызываем инициализацию нужной страницы
    if (url.endsWith('enter.html'))    initEnter();
    if (url.endsWith('registry.html')) initRegistry();
  } catch (e) {
    app.innerHTML = '<p>Page is not found</p>';
  }
}

document.querySelectorAll('nav a').forEach(a => {
  a.addEventListener('click', e => {
    e.preventDefault();
    const page = a.dataset.page;
    history.pushState({ page }, '', '#' + page);
    loadPage(page);
  });
});

window.addEventListener('popstate', e => {
  const page = e.state?.page || location.hash.slice(1) || 'enter.html';
  loadPage(page);
});

loadPage(location.hash.slice(1) || 'enter.html');


// ---------- Страница "Вход" ----------
function initEnter() {
  const btn = document.querySelector('#enter_continue');
  btn.addEventListener('click', async () => {
    const login    = document.querySelector('#login').value.trim();
    const password = document.querySelector('#password').value;
    const out      = document.querySelector('#user_id');

    if (!login || !password) {
      out.textContent = 'Enter all';
      return;
    }

    const r = await fetch(`${API}/enter`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ login, password })
    });
    const data = await r.json();

    if (!r.ok) {
      out.textContent = data.error;
      return;
    }

    localStorage.setItem('session_key', data.session_key);
    out.textContent = `${data.name} (${data.session_key.slice(0, 8)}…)`;
  });
}


// ---------- Страница "Регистрация" ----------
function initRegistry() {
  const btn = document.querySelector('#reg_continue');
  btn.addEventListener('click', async () => {
    const name    = document.querySelector('#reg_name').value.trim();
    const login   = document.querySelector('#reg_login').value.trim();
    const p1      = document.querySelector('#reg_password').value;
    const p2      = document.querySelector('#reg_password2').value;
    const out     = document.querySelector('#reg_error');

    if (!name || !login || !p1) {
      out.textContent = 'Enter all';
      return;
    }
    if (p1 !== p2) {
      out.textContent = 'Password is not same';
      return;
    }

    const r = await fetch(`${API}/registry`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, login, password: p1 })
    });
    const data = await r.json();

    if (!r.ok) {
      out.textContent = data.error;
      return;
    }

    out.textContent = 'Готово! Теперь войдите.';
    // Автопереход на вход через 1 сек
    setTimeout(() => {
      history.pushState({ page: 'enter.html' }, '', '#enter.html');
      loadPage('enter.html');
    }, 1000);
  });
}