import React, { useState, useEffect, useRef, useCallback } from 'react';
import { createRoot } from 'react-dom/client';

const API = '/api';

/* ---------------- utils ---------------- */

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

function navigate(page) {
  location.hash = page;
}

function useHashRoute() {
  const [route, setRoute] = useState(
    () => location.hash.slice(1) || 'enter.html'
  );

  useEffect(() => {
    const onHash = () =>
      setRoute(location.hash.slice(1) || 'enter.html');
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  return route;
}

/* ---------------- layout ---------------- */

function HighMenu() {
  return (
    <header className="hight-menu">
      <button type="menu">...</button>
      <div type="account">
        <h3>Account</h3>
        <button type="account"></button>
      </div>
    </header>
  );
}

/* ---------------- pages ---------------- */

function Enter() {
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [out, setOut] = useState('');

  const handleSubmit = async () => {
    const l = login.trim();
    if (!l || !password) {
      setOut('Enter all');
      return;
    }

    const r = await fetch(`${API}/enter`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ login: l, password }),
    });
    const data = await r.json();

    if (!r.ok) {
      setOut(data.error);
      return;
    }

    navigate('main.html');
  };

  return (
    <>
      <HighMenu />
      <div className="enter-window">
        <h1>Enter</h1>
        <input
          type="login"
          placeholder="Login"
          value={login}
          onChange={(e) => setLogin(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
        />
        <h6>{out}</h6>
        <button onClick={handleSubmit}>Continue</button>
      </div>
    </>
  );
}

function Registry() {
  const [name, setName] = useState('');
  const [link, setLink] = useState('');
  const [login, setLogin] = useState('');
  const [p1, setP1] = useState('');
  const [p2, setP2] = useState('');
  const [out, setOut] = useState('');

  const handleSubmit = async () => {
    const n = name.trim();
    const l = login.trim();

    if (!n || !l || !p1) {
      setOut('Enter all');
      return;
    }
    if (p1 !== p2) {
      setOut('Password is not same');
      return;
    }

    const r = await fetch(`${API}/registry`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: n, login: l, password: p1 }),
    });
    const data = await r.json();

    if (!r.ok) {
      setOut(data.error);
      return;
    }

    setOut('Success');
    setTimeout(() => navigate('enter.html'), 10);
  };

  return (
    <>
      <HighMenu />
      <div className="registry-window">
        <h1>Registry</h1>
        <input
          type="name"
          placeholder="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          type="link"
          placeholder="@your_link"
          value={link}
          onChange={(e) => setLink(e.target.value)}
        />
        <input
          type="login"
          placeholder="Login"
          value={login}
          onChange={(e) => setLogin(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          value={p1}
          onChange={(e) => setP1(e.target.value)}
        />
        <input
          type="password"
          placeholder="Confim password"
          value={p2}
          onChange={(e) => setP2(e.target.value)}
        />
        <h6>{out}</h6>
        <button onClick={handleSubmit}>Continue</button>
      </div>
    </>
  );
}

function CreateChat() {
  const [chatName, setChatName] = useState('');
  const [userLink, setUserLink] = useState('');
  const [out, setOut] = useState('');

  const handleCreate = async () => {
    const name = chatName.trim();
    if (!name || !userLink) {
      setOut('Enter all');
      return;
    }

    const r = await fetch(`${API}/new_chat`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_name: name, user_link: userLink }),
    });
    const data = await r.json();

    if (!r.ok) {
      setOut(data.error);
      return;
    }

    navigate('main.html');
  };

  return (
    <>
      <HighMenu />
      <div className="enter-window">
        <h1>Create new chat</h1>
        <input
          type="text"
          placeholder="Chat name"
          value={chatName}
          onChange={(e) => setChatName(e.target.value)}
        />
        <input
          type="text"
          placeholder="@user_link"
          value={userLink}
          onChange={(e) => setUserLink(e.target.value)}
        />
        <h6>{out}</h6>
        <button onClick={handleCreate}>Create</button>
      </div>
    </>
  );
}

function Main() {
  const [chats, setChats] = useState([]);
  const [curChatId, setCurChatId] = useState(0);
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState('');

  const curChatIdRef = useRef(0);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    curChatIdRef.current = curChatId;
  }, [curChatId]);

  /* ---- загрузка списка чатов ---- */
  useEffect(() => {
    (async () => {
      try {
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
        setChats(data.map(([id, name]) => ({ id: String(id), name })));
      } catch (e) {
        console.error(e);
      }
    })();
  }, []);

  /* ---- WebSocket ---- */
  useEffect(() => {
    let ws = null;
    let stopped = false;

    const connect = () => {
      if (stopped) return;
      const proto = location.protocol === 'https:' ? 'wss' : 'ws';
      ws = new WebSocket(`${proto}://${location.host}/api/ws`);

      ws.onmessage = (e) => {
        let msg;
        try {
          msg = JSON.parse(e.data);
        } catch {
          return;
        }
        if (msg.type !== 'message') return;
        if (String(msg.chat_id) === String(curChatIdRef.current)) {
          setMessages((prev) => [
            ...prev,
            { sender: msg.sender_name, date: msg.date, text: msg.text },
          ]);
        }
      };

      ws.onclose = (e) => {
        if (stopped || e.code === 1008) return;
        setTimeout(connect, 1000 + Math.random() * 500);
      };
    };

    connect();

    return () => {
      stopped = true;
      ws?.close();
    };
  }, []);

  /* ---- автоскролл ---- */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'auto' });
  }, [messages]);

  /* ---- загрузка сообщений ---- */
  const loadMessages = useCallback(async (chatId) => {
    try {
      const r = await fetch(`${API}/get_messeges`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id: chatId }),
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
      setMessages(
        data.map(([sender, date, text]) => ({ sender, date, text }))
      );
    } catch (e) {
      console.error(e);
    }
  }, []);

  const handleSelectChat = (chatId) => {
    setCurChatId(chatId);
    loadMessages(chatId);
  };

  /* ---- отправка ---- */
  const handleSend = async () => {
    const t = text;
    if (!t.trim() || !curChatId) return;

    setText('');
    try {
      const r = await fetch(`${API}/send_messege`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id: curChatId, text: t }),
      });
      if (!r.ok) {
        console.error('HTTP', r.status, await r.text());
        setText(t);
        return;
      }
      await loadMessages(curChatId);
    } catch (e) {
      console.error('Send failed:', e);
      setText(t);
    }
  };

  const currentChatName =
    chats.find((c) => c.id === String(curChatId))?.name || 'Chat name';

  return (
    <>
      <HighMenu />
      <div className="main-slide">
        <div className="chat-space">
          <h1>Chats</h1>
          <div>
            {chats.map((c) => (
              <button
                key={c.id}
                className={String(curChatId) === c.id ? 'active' : ''}
                onClick={() => handleSelectChat(c.id)}
              >
                {c.name}
              </button>
            ))}
            <button onClick={() => navigate('create_chat.html')}>
              + Create chat
            </button>
          </div>
        </div>

        <div className="message-space">
          <h1>{currentChatName}</h1>
          <div className="message-list">
            {messages.map((m, i) => (
              <div key={i}>
                <h4>{m.text}</h4>
                <h6>
                  {m.sender} {formatDate(m.date)}
                </h6>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
          <div className="send">
            <input
              type="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            />
            <button onClick={handleSend}>Send</button>
          </div>
        </div>
      </div>
    </>
  );
}

/* ---------------- root ---------------- */

function App() {
  const route = useHashRoute();

  switch (route) {
    case 'enter.html':
      return <Enter />;
    case 'registry.html':
      return <Registry />;
    case 'main.html':
    case 'messeges.html':
      return <Main />;
    case 'create_chat.html':
      return <CreateChat />;
    case 'home_unreg.html':
    default:
      return <Enter />;
  }
}

createRoot(document.getElementById('app')).render(<App />);
