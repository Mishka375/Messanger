const app = document.getElementById('app');
const API = '/api';

// ---------- Роутер ----------
async function loadPage(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error('not found');
    app.innerHTML = await res.text();

    // Вызываем инициализацию нужной страницы
    if (url.endsWith('home_unreg.html'))   initHomeUnreg();
    if (url.endsWith('enter.html'))        initEnter();
    if (url.endsWith('registry.html'))     initRegistry();
    if (url.endsWith('messeges.html'))     initMesseges();
    if (url.endsWith('create_chat.html'))  newChat();
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
  const page = e.state?.page || location.hash.slice(1) || 'home_unreg.html';
  loadPage(page);
});

loadPage(location.hash.slice(1) || 'home_unreg.html');


// ---------- Страница "Вход" ----------
function initEnter() {
  const btn = document.querySelector('#enter_continue');
  btn.addEventListener('click', async () => {
    const login    = document.querySelector('#login').value.trim();
    const password = document.querySelector('#password').value;
    const out      = document.querySelector('#out');

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

    setTimeout(() => {
      history.pushState({ page: 'messeges.html' }, '', '#messeges.html');
      loadPage('messeges.html');
    }, 10);
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
    const out     = document.querySelector('#out');

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

    out.textContent = 'Success';

    setTimeout(() => {
      history.pushState({ page: 'enter.html' }, '', '#enter.html');
      loadPage('enter.html');
    }, 10);
  });
}

// ---------- Страница "Вход (не зарегестрированный)" ----------
function initHomeUnreg() {
  const ent = document.querySelector('#ent');
    ent.addEventListener('click', async () => {
    history.pushState({ page: 'enter.html' }, '', '#enter.html');
    loadPage('enter.html');
  });

  const reg = document.querySelector('#reg');
    reg.addEventListener('click', async () => {
    history.pushState({ page: 'registry.html' }, '', '#registry.html');
    loadPage('registry.html');
    });
}

// ---------- Страница "Сообщения" ----------
async function initMesseges() {
  const container = document.getElementById('buttons-container');

  cur_chat_id = 0;

  container.innerHTML = '';

  const r = await fetch(`${API}/messeges`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!r.ok) {
    console.error('HTTP', r.status, await r.text());
    return;
  }

  const response = await r.json();

  const data = response.chats_data;

  if (!Array.isArray(data)) {
    console.error('Await all package, now:', data);
    return;
  }

  data.forEach(([chatId, chatName]) => {
    const btn = document.createElement('button');
    btn.textContent = chatName;
    btn.dataset.chatID = chatId
  
    btn.addEventListener('click', () => {
      cur_chat_id = btn.dataset.chatID;
      loadMesseges(btn.dataset.chatID);
    });

    container.appendChild(btn);
  });

  const btn_new_chat = document.querySelector('#new_chat');
  if (btn_new_chat && !btn_new_chat.dataset.bound) {
    btn_new_chat.dataset.bound = '1';
    btn_new_chat.addEventListener('click', () => {
      history.pushState({ page: 'create_chat.html' }, '', '#create_chat.html');
      loadPage('create_chat.html');
    });
  }

  const btn_send = document.querySelector('#send_messege');
  if (btn_send && !btn_send.dataset.bound) {
    btn_send.dataset.bound = '1';
    btn_send.addEventListener('click', async () => {
      const input = document.querySelector('#messege_text');
      const text = input.value;
      if (!text.trim()) return;

      input.value = '';
      try {
        await sendMessege(cur_chat_id, text);
      } catch (e) {
        console.error('Send failed:', e);
        input.value = text;
      }
    });
  }
}

// ---------- "Загрузка сообщений" ----------
async function loadMesseges(chat_id) {
  const container = document.getElementById('messeges');

  container.innerHTML = '';

  const r = await fetch(`${API}/get_messeges`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: chat_id })
  });

  if (!r.ok) {
    console.error('HTTP', r.status, await r.text());
    return;
  }

  const response = await r.json();

  const data = response.messeges;

  if (!Array.isArray(data)) {
    console.error('Await all package, now:', data);
    return;
  }

  data.forEach(([sender, date, text]) => {
    const el = document.createElement('article');
    el.className = 'message';
    el.dataset.sender = sender;
    el.dataset.date = date;

    const meta = document.createElement('header');
    meta.className = 'message-meta';
    meta.textContent = `${sender} · ${formatDate(date)}`;

    const body = document.createElement('div');
    body.className = 'message-text';
    body.textContent = text;

    el.append(meta, body);
    container.appendChild(el);
  });

  container.scrollTop = container.scrollHeight;
}

// ---------- "Отправка сообщения" ----------
async function sendMessege(chat_id, text) {
  const r = await fetch(`${API}/send_messege`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({chat_id, text})
  });

  if (!r.ok) {
    console.error('HTTP', r.status, await r.text());
    return;
  }

  const data = await r.json();

  if (!r.ok) {
    out.textContent = data.error;
    return;
  }

  loadMesseges(chat_id);
}

// ---------- Страница "Создания чата" ----------
function newChat() {
  const btn = document.querySelector('#enter_continue');
  btn.addEventListener('click', async () => {
    const chat_name    = document.querySelector('#chat_name').value.trim();
    const user_link    = document.querySelector('#user_link').value;
    const out          = document.querySelector('#out');

    if (!chat_name || !user_link) {
      out.textContent = 'Enter all';
      return;
    }

    const r = await fetch(`${API}/new_chat`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({chat_name, user_link })
    });
    const data = await r.json();

    if (!r.ok) {
      out.textContent = data.error;
      return;
    }

    setTimeout(() => {
      history.pushState({ page: 'messeges.html' }, '', '#messeges.html');
      loadPage('messeges.html');
    }, 10);
  });
}







function formatDate(value) {
  const d = new Date(value);
  if (isNaN(d)) return String(value);

  const now = new Date();
  const sameDay = d.toDateString() === now.toDateString();

  return sameDay
    ? d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
    : d.toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      });
}