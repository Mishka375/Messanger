import monitoring, database
from libs import log, gui, server, errors
import time, threading, uuid

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

connects = {}

def key_gen () -> str:
    return str(uuid.uuid4())

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
        id = database.cursor_users.fetchone()

        if id is None:
            log.log.warning("User is not found")
            raise errors.IncorrectEnter("User is not found")

        id = id[0]

        database.users_execute("INSERT INTO personal VALUES (%s, %s, %s);", (id, "^"+login, name))
        
        monitoring.users_total.inc()
        
        log.log.debug(f"User {name} is created (ID: {id})")

    except errors.SQLValueExist as error:
        log.log.error(error)
        raise errors.IncorrectLogin("Login is exist")

    except errors.SQLValueIsNull as error:
        log.log.error(error)
        raise errors.IncorrectLogin("Login is null")

    except Exception as error:
        log.log.error(error)
        raise

    finally:
        monitoring.sql_request_time.observe(time.time() - start)

def enter (login, password, conn):
    start = time.time()

    try:
        database.users_execute("SELECT id FROM users WHERE login=%s AND password=%s;", (login, password))
        id = database.cursor_users.fetchone()

        if id is None:
            raise errors.IncorrectEnter("Incorrect login or password")

        id = id[0]
        
        key = key_gen()

        if database.redis_sessions_get(key) is not None:
            log.log.warning ("Key is exist")
            raise errors.IncorrectKey("Key is exist")

        database.redis_sessions_set(key, id)
        monitoring.users_online.inc()
        database.users_execute('SELECT name FROM personal WHERE id=%s;', (id, ))
        log.log.debug(f"User {database.cursor_users.fetchone()[0]} enter (key: {key});")
        return key

    except errors.DataError as error:
        log.log.error(error)
        raise
        
    except Exception as error:
        log.log.error(error)
        raise

    finally:
        monitoring.sql_request_time.observe(time.time() - start)

def out (key):
    global connects
    start = time.time()
    
    try:
        id = database.redis_sessions_get(key)
        
        if id is not None:
            id = id[0]

            database.users_execute("SELECT name FROM personal WHERE id=%s;", (id,))
            result = database.cursor_users.fetchone()

            if result is None:
                log.log.warning("User is not found")
                raise errors.IncorrectEnter("User unfound")
            
            monitoring.users_online.dec()
            database.redis_sessions_del(key)
            del connects[id]
                
            log.log.debug(f"User {result} is exit")

        else:
            log.log.warning("Key is incorrect")
            raise errors.IncorrectKey("Key is incorrect")
            
    except Exception as error:
        log.log.error(error)
        raise

    finally:
        monitoring.sql_request_time.observe(time.time() - start)

def new_chat (key, user_link, name):
    start = time.time()

    try:
        id_1 = database.redis_sessions_get(key)

        if id_1 is None:
            log.log.warning("Key is not exist")
            raise errors.IncorrectKey("Key is not exist")
        
        id_1 = id_1[0]

        database.users_execute("SELECT id FROM personal WHERE identificator=%s;", (user_link,))
        id_2 = database.cursor_users.fetchone()

        if int(id_1) != int(id_2) and id_2 is not None:
            database.chats_execute("INSERT INTO chats (name, user_1, user_2) VALUES (%s, %s, %s);", (name, id_1, id_2[0]))
            log.log.debug(f"Chat {name} was created")

        elif id_2 is None:
            log.log.warning("User is not found")
            raise errors.IncorrectEnter("User unfound")

        elif id_1 == id_2[0]:
            log.log.warning(f"Chat {name} wasn't created, same id")
            raise errors.ChatError("One user in chat")

    except Exception as error:
        log.log.error(error)
        raise

    finally:
        monitoring.sql_request_time.observe(time.time() - start)

def choose_chat (key, chat_name):
    start = time.time()
    
    try:
        id = database.redis_sessions_get(key)

        if id is None:
            log.log.warning("Key is not exist")
            raise errors.IncorrectKey("Key is not exist")

        id = id[0]

        database.chats_execute("SELECT id FROM chats WHERE name=%s AND (user_1 = %s OR user_2 = %s);", (chat_name, id, id))
        chat_id = database.cursor_chats.fetchone()

        if chat_id is None:
            log.log.warning("Chat is not found")
            raise errors.ChatError("Chat is not found")

        log.log.debug(f"Chat {chat_name} is chossed")
        return chat_id[0]
    
    except Exception as error:
        chat_id = None
        log.log.error(error)
        raise

    finally:
        monitoring.sql_request_time.observe(time.time() - start)

def message (key, chat_id, message):
    global connects
    start = time.time()
    
    try:
        sender_id = database.redis_sessions_get(key)
        
        if sender_id is None:
            log.log.warning("Key is not exist")
            raise errors.IncorrectKey("Key is not exist")
        
        sender_id = sender_id[0]

        database.chats_execute("INSERT INTO messages (user_id, chat_id, text) VALUES (%s, %s, %s);", (sender_id, chat_id, message))

        database.chats_execute("SELECT user_1, user_2 FROM chats WHERE id=%s", (chat_id,))
        data = database.cursor_chats.fetchone()

        if data is None:
            log.log.warning("Chat is not found")
            raise errors.ChatError("Chat is not found")

        interlocur_id = data[0] if data[0] != int(sender_id) else data[1]
        interlocur_conn = connects[str(interlocur_id)]
        chat.send_all(message, interlocur_conn)

        log.log.debug(f"Message {message} was sended")
        monitoring.messages_count.inc()
    
    except Exception as error:
        monitoring.sql_request_errors.inc()
        log.log.error(error)
        raise

    finally:
        monitoring.sql_request_time.observe(time.time() - start)

def check_session(key):
    if database.redis_sessions_get(key) is not None:
        return True
    return False


def users_active (conn, bufsize: int = 1024):
    try:
        serv.send("1", conn)

        while 1:
            data = serv.get_message(user = conn)
            data = data.split("*;:;*")

            match data[0]:
                case "register":
                    try:
                        register(data[1], data[2], data[3])
                        serv.send("0", conn)

                    except errors.IncorrectLogin:
                        serv.send("301", conn)

                    except Exception:
                        serv.send("1", conn)

                case "enter":
                    try:
                        session_key = enter(data[1], data[2], conn)

                        id = database.redis_sessions_get(session_key)

                        if id is None:
                            serv.send("303", conn)
                            continue

                        database.users_execute("SELECT name FROM personal WHERE id=%s", (id,))
                        user_name = database.cursor_users.fetchone()

                        if user_name is None:
                            serv.send("302", conn)
                            continue

                        serv.send("0", conn)
                        time.sleep(0.1)
                        serv.send(f"{session_key}*;:;*{user_name[0]}", conn)

                    except errors.IncorrectEnter:
                        serv.send("302", conn)

                    except errors.IncorrectKey:
                        serv.send("303", conn)

                    except Exception:
                        serv.send("1", conn)
                        
                case "new_chat":
                    try:
                        current = new_chat(data[1], data[2], data[3])
                        serv.send("0", conn)

                    except errors.IncorrectEnter:
                        serv.send("302", conn)

                    except errors.IncorrectKey:
                        serv.send("303", conn)

                    except errors.ChatError:
                        serv.send("400", conn)

                    except Exception:
                        serv.send("1", conn)

                case "choose_chat":
                    try:
                        chat_id = choose_chat(data[1], data[2])

                        serv.send("0", conn)
                        time.sleep(0.1)
                        serv.send(f"{chat_id}", conn)

                    except errors.IncorrectKey:
                        serv.send("303", conn)

                    except errors.ChatError:
                        serv.send("400", conn)

                    except Exception:
                        serv.send("1", conn)

                case "message":
                    try:
                        message(data[1], data[2], data[3])
                        serv.send("0", conn)

                    except errors.IncorrectKey:
                        serv.send("303", conn)

                    except errors.ChatError:
                        serv.send("400", conn)

                    except Exception:
                        serv.send("1", conn)
                
                case "out":
                    try:
                        out(data[1])
                        serv.send("0", conn)

                    except errors.IncorrectEnter:
                        serv.send("302", conn)

                    except errors.IncorrectKey:
                        serv.send("303", conn)

                    except Exception:
                        serv.send("1", conn)

    except Exception as error:
        log.log.error(error)
        serv.send("0", conn)

def main_way():
    while 1:
        conn = serv.accept()
        log.log.info("new connect")
        local_server =  threading.Thread(target = users_active, daemon = True, args = (conn,))
        local_server.start()

main_way = threading.Thread(target = main_way, daemon = True)

try:
    monitoring.start_http_server(8000)
    main_way.start()
    print("Monitoring is started")

    while 1:
        pass

except Exception:
    None