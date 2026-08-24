import monitoring, database
from libs import log, gui, server
import time, threading

HOST = "0.0.0.0"
SERV_PORT = 70
CHAT_PORT = 71

serv = server.Server()
serv.create_socket(host = HOST, port = SERV_PORT)
serv.start()

chat = server.Server()
chat.create_socket(host = HOST, port = CHAT_PORT)
chat.start()

database.users_execute("SELECT COUNT(*) FROM users;")
count = database.cursor_users.fetchone()[0]
monitoring.users_total.set(int(count))

connects ={}

def new_sender ():
    global chat, connects

    while 1:
        conn = chat.accept()
        chat.send_all("# Chat Connect", conn)
        key = chat.get_message(user = conn)
        id = database.redis_sessions_get(key)
        connects[id] = conn

threading.Thread(target = new_sender, daemon = True).start()

def register (login, password, name):
    start = time.time()

    current = None

    try:
        database.users_execute("INSERT INTO users (login, password) VALUES (%s, %s);", (login, password))
        database.users_execute("SELECT id FROM users WHERE login=%s;", (login,))
        id = database.cursor_users.fetchone()[0]
        current = database.users_execute("INSERT INTO personal VALUES (%s, %s, %s);", (id, "^"+login, name))
        
        monitoring.users_total.inc()
        
        log.log.debug(f"User {name} is created (ID: {id})")

        return current
        
    except Exception as error:
        monitoring.sql_request_errors.inc()
        log.log.error(f"Enters error: {error}")
        return 0
    finally:
        monitoring.sql_request_time.observe(time.time() - start)

def enter (login, password, conn):
    start = time.time()

    try:
        database.users_execute("SELECT id FROM users WHERE login=%s AND password=%s;", (login, password))
        id = database.cursor_users.fetchone()[0]
        
        if id:
            key = f"{login}:{id}"
            
            database.redis_sessions_set(key, id)

            monitoring.users_online.inc()

            database.users_execute('SELECT name FROM personal WHERE id=%s;', (id, ))
            
            log.log.debug(f"User {database.cursor_users.fetchone()[0]} enter (key: {key});")
            return key
        else:
            log.log.warning("Incorrect password or login")
            return 0
            
    except Exception as error:
        monitoring.sql_request_errors.inc()
        log.log.error(f"Enters error: {error}")
        return 0
    finally:
        monitoring.sql_request_time.observe(time.time() - start)

def out (key):
    global connects
    start = time.time()
    
    try:
        id = database.redis_sessions_get(key)
        database.users_execute("SELECT name FROM personal WHERE id=%s;", (id,))
        result = database.cursor_users.fetchone()[0]
        
        if result:
            monitoring.users_online.dec()
            id = database.redis_sessions_get(key)
            database.redis_sessions_del(key)
            del connects[id]
            
            log.log.debug(f"User {result} is exit")

            return 1
        else:
            log.log.warning("Incorrect key")
            return 0
            
    except Exception as error:
        monitoring.sql_request_errors.inc()
        log.log.error(f"Enters error: {error}")
        return 0
    finally:
        monitoring.sql_request_time.observe(time.time() - start)

def new_chat (key, user_link, name):
    start = time.time()

    current = None
    
    try:
        id_1 = database.redis_sessions_get(key)
        database.users_execute("SELECT id FROM personal WHERE identificator=%s;", (user_link,))
        id_2 = database.cursor_users.fetchone()[0]

        log.log.debug(f"__________________________{id_1, id_2}___________________________")

        if id_1 != id_2 and id_2:
            current = database.chats_execute("INSERT INTO chats (name, user_1, user_2) VALUES (%s, %s, %s);", (name, id_1, id_2))
            log.log.debug(f"Chat {name} was created")
        else:
            current = 0
            log.log.warning(f"Chat {name} wasn't created, same id")

        return current
    
    except Exception as error:
        monitoring.sql_request_errors.inc()
        log.log.error(f"Enters error: {error}")
        return 0
    finally:
        monitoring.sql_request_time.observe(time.time() - start)

def choose_chat (key, chat_name):
    start = time.time()
    
    try:
        id = database.redis_sessions_get(key)

        database.chats_execute("SELECT id FROM chats WHERE name=%s AND (user_1 = %s OR user_2 = %s);", (chat_name, id, id))
        chat_id = database.cursor_chats.fetchone()[0]
        log.log.debug(f"Chat {chat_name} is chossed")
    
    except Exception as error:
        chat_id = None
        monitoring.sql_request_errors.inc()
        log.log.error(f"Enters error: {error}")
        return 0
    finally:
        monitoring.sql_request_time.observe(time.time() - start)
        return chat_id

def message (key, chat_id, message):
    global connects
    start = time.time()
    
    current = None

    try:
        sender_id = database.redis_sessions_get(key)
        current = database.chats_execute("INSERT INTO messages (user_id, chat_id, text) VALUES (%s, %s, %s);", (sender_id, chat_id, message))

        database.chats_execute("SELECT user_1, user_2 FROM chats WHERE id=%s", (chat_id,))
        data = database.cursor_chats.fetchone()

        interlocur_id = data[0] if data[0] != int(sender_id) else data[1]
        interlocur_conn = connects[str(interlocur_id)]
        chat.send_all(message, interlocur_conn)

        log.log.debug(f"Message {message} was sended")
        monitoring.messages_count.inc()

        return current
    
    except Exception as error:
        monitoring.sql_request_errors.inc()
        log.log.error(f"Enters error: {error}")
        return 0
    finally:
        monitoring.sql_request_time.observe(time.time() - start)

def check_session(key):
    if database.redis_sessions_get(key):
        return True
    return False


def users_active (conn, bufsize: int = 1024):
    try:
        serv.send("Connect", conn)

        current = 0

        while 1:
            data = serv.get_message(user = conn)
            data = data.split("*;:;*")

            match data[0]:
                case "register":
                    current = register(data[1], data[2], data[3])
                    serv.send(str(current), conn)

                case "enter":
                    session_key = enter(data[1], data[2], conn)

                    id = database.redis_sessions_get(session_key)

                    if session_key:
                        database.users_execute("SELECT name FROM personal WHERE id=%s", (id,))
                        user_name = database.cursor_users.fetchone()[0]
                    else:
                        user_name = 0

                    current = 1 if user_name else 0

                    serv.send(f"{session_key}*;:;*{user_name}", conn)
                    time.sleep(0.1)
                    serv.send(str(current), conn)

                case "new_chat":
                    current = new_chat(data[1], data[2], data[3])
                    serv.send(str(current), conn)

                case "choose_chat":
                    chat_id = choose_chat(data[1], data[2])

                    current = 1 if chat_id else 0

                    serv.send(f"{chat_id}", conn)
                    time.sleep(0.1)
                    serv.send(str(current), conn)

                case "message":
                    current = message(data[1], data[2], data[3])
                    serv.send(str(current), conn)
                
                case "out":
                    current = out(data[1])
                    serv.send(str(current), conn)

    except Exception as error:
        log.log.error(error)
        serv.send(None, conn)

class Active:
    def __init__ (self, function = users_active):
        self.thread = None
        self.target = function
        self.daemon = True

    def start (self, conn):
        self.thread = threading.Thread(target = self.target, daemon = self.daemon, args = (conn,))
        self.thread.start()
        log.log.debug("new thread")

try:
    monitoring.start_http_server(8000)
    print("Monitoring is started")
except Exception:
    None