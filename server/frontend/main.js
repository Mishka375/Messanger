const API = 'http://127.0.0.1:5000';

document.querySelector('#enter_continue').addEventListener('click', async () => {
    const login = document.querySelector('#login').value.trim();
    const password = document.querySelector('#password').value.trim();
    if (!login || !password) return;

    const r = await fetch(`${API}/enter`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({login, password})
    });
    const data = await r.json();
    if (!r.ok) {
        document.querySelector('#user_id').textContent = data.error;
        return;
    }
    localStorage.setItem('session_key', data.session_key);
    document.querySelector('#user_id').textContent =
        `${data.name} (${data.session_key.slice(0, 8)}…)`;
});