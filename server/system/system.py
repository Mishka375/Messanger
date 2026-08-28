import monitoring
import database
from libs import log
from libs import server
from libs import errors
import time
import threading
import pickle
import uuid


split_symbol = "*;:;*"

HOST = "0.0.0.0"
SERV_PORT = 70
CHAT_PORT = 71

serv = server.Server()
serv.create_socket(host = HOST, port = SERV_PORT)
serv.start()

chat = server.Server()
chat.create_socket(host = HOST, port = CHAT_PORT)
chat.start()

count = database.users_execute("SELECT COUNT(*) FROM users;")
monitoring.users_total.set(int(count[0][0]))

connects = {}


def key_gen() -> str:
    return str(uuid.uuid4())

def new_sender() -> None:
    global chat, connects

    while 1:
        conn = chat.accept()
        chat.send_all("1", conn)
        key = chat.get_message(user = conn)
        id = database.redis_sessions_get(key)

        if id is None:
            log.log.error(f"id is not found")

        else:
            id = int(id)
            connects[id] = conn
            log.log.debug(f"new seder <{id}>")

threading.Thread(target = new_sender, daemon = True).start()

def register(login: str, password: str, name: str) -> None:
    start = time.time()

    try:
        database.users_execute("INSERT INTO users (login, password) VALUES (%s, %s);", (login, password))

        id = database.users_execute("SELECT id FROM users WHERE login=%s AND password=%s", (login, password))

        if id is None:
            log.log.warning("User is not found")
            raise errors.IncorrectEnter("User is not found")

        id = int(id[0][0])

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


def enter (login: str, password: str) -> str:
    start = time.time()

    try:
        id = database.users_execute("SELECT id FROM users WHERE login=%s AND password=%s;", (login, password))

        if id is None:
            raise errors.IncorrectEnter("Incorrect login or password")

        id = int(id[0][0])
        
        key = key_gen()

        if database.redis_sessions_get(key) is not None:
            log.log.warning ("Key is exist")
            raise errors.IncorrectKey("Key is exist")

        database.redis_sessions_set(key, id)

        monitoring.users_online.inc()
        log.log.debug(f"User enter (key: {key});")

        chats_data = database.chats_execute("SELECT id, name FROM chats WHERE user_1=%s OR user_2=%s", (id, id))

        return key, chats_data
        
    except Exception as error:
        log.log.error(error)
        raise

    finally:
        monitoring.sql_request_time.observe(time.time() - start)


def out (key: str) -> None:
    global connects
    start = time.time()
    
    try:
        id = database.redis_sessions_get(key)
        
        if id is None:
            log.log.warning("Key is incorrect")
            raise errors.IncorrectKey("Key is incorrect")
        
        id = int(id)
        
        monitoring.users_online.dec()
        database.redis_sessions_del(key)
        del connects[id]
            
        log.log.debug(f"User {id} is exit")
            
    except Exception as error:
        log.log.error(error)
        raise

    finally:
        monitoring.sql_request_time.observe(time.time() - start)


def new_chat (key: str, user_link: str, name: str) -> int:
    start = time.time()

    try:
        id_1 = database.redis_sessions_get(key)

        if id_1 is None:
            log.log.warning("Key is not exist")
            raise errors.IncorrectKey("Key is not exist")

        id_1 = int(id_1)

        id_2 = database.users_execute("SELECT id FROM personal WHERE identificator=%s;", (user_link,))

        if id_2 is None:
            log.log.warning("Link is incorrect")
            raise errors.IncorrectEnter("Link is incorrect")

        id_2 = int(id_2[0][0])

        if id_1 != id_2:
            database.chats_execute("INSERT INTO chats (name, user_1, user_2) VALUES (%s, %s, %s);", (name, id_1, id_2))
            log.log.debug(f"Chat {name} was created")

            chat_id = database.chats_execute("SELECT id FROM chats WHERE name=%s AND user_1=%s AND user_2=%s", (name, id_1, id_2))

            if chat_id is None:
                log.log.warning("Chat is not found")
                raise errors.ChatError

            return int(chat_id[0][0])

        else:
            log.log.warning(f"Chat {name} wasn't created, same id")
            raise errors.ChatError("One user in chat")

    except Exception as error:
        log.log.error(error)
        raise

    finally:
        monitoring.sql_request_time.observe(time.time() - start)


def choose_chat (key: str, chat_name: str) -> int:
    start = time.time()
    
    try:
        id = database.redis_sessions_get(key)

        if id is None:
            log.log.warning("Key is not exist")
            raise errors.IncorrectKey("Key is not exist")

        id = int(id)

        chat_id = database.chats_execute("SELECT id FROM chats WHERE name=%s AND (user_1 = %s OR user_2 = %s);", (chat_name, id, id))

        if chat_id is None:
            log.log.warning("Chat is not found")
            raise errors.ChatError("Chat is not found")

        chat_id = int(chat_id[0][0])

        log.log.debug(f"Chat {chat_name} is chossed")
        return chat_id
    
    except Exception as error:
        chat_id = None
        log.log.error(error)
        raise

    finally:
        monitoring.sql_request_time.observe(time.time() - start)


def message (key: str, chat_id: int, message: str) -> None:
    global connects
    start = time.time()
    
    try:
        sender_id = database.redis_sessions_get(key)
        
        if sender_id is None:
            log.log.warning("Key is not exist")
            raise errors.IncorrectKey("Key is not exist")
        
        sender_id = int(sender_id)

        sender_name = database.users_execute("SELECT name FROM personal WHERE id=%s", (sender_id,))

        if sender_name is None:
            log.log.warning("User is not exist")
            raise errors.IncorrectEnter("User is not exist")

        sender_name = sender_name[0][0]

        database.chats_execute("INSERT INTO messages (user_id, chat_id, text) VALUES (%s, %s, %s);", (sender_id, chat_id, message))

        data = database.chats_execute("SELECT user_1, user_2 FROM chats WHERE id=%s", (chat_id,))

        if data is None:
            log.log.warning("Chat is not found")
            raise errors.ChatError("Chat is not found")

        user_1, user_2 = data[0]

        interlocur_id = int(user_1) if int(user_1) != sender_id else int(user_2)
        try:
            interlocur_conn = connects[int(interlocur_id)]
            chat.send_all(split_symbol.join([sender_name, message]), interlocur_conn)

        except KeyError:
            log.log.warning("User is not online")

        except Exception:
            raise

        log.log.debug(f"Message {message} was sended")
        monitoring.messages_count.inc()
    
    except Exception as error:
        monitoring.sql_request_errors.inc()
        log.log.error(error)
        raise

    finally:
        monitoring.sql_request_time.observe(time.time() - start)


def check_session(key: str) -> bool:
    if database.redis_sessions_get(key) is not None:
        return True
    return False


def users_active (conn) -> None:
    try:
        serv.send("1", conn)

        while 1:
            data = serv.get_message(user = conn)
            data = data.split(split_symbol)

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
                        session_key, chats_data = enter(data[1], data[2])

                        id = database.redis_sessions_get(session_key)

                        if id is None:
                            serv.send("303", conn)
                            continue

                        id = int(id)

                        user_name = database.users_execute("SELECT name FROM personal WHERE id=%s", (id,))

                        if user_name is None:
                            serv.send("302", conn)
                            continue

                        serv.send("0", conn)
                        time.sleep(0.1)
                        serv.send(split_symbol.join([session_key, user_name[0][0]]), conn)
                        time.sleep(0.1)
                        serv.send_all(pickle.dumps(chats_data), conn)

                    except errors.IncorrectEnter:
                        serv.send("302", conn)

                    except errors.IncorrectKey:
                        serv.send("303", conn)

                    except Exception as error:
                        log.log.error(error)
                        serv.send("1", conn)
                        
                case "new_chat":
                    try:
                        chat_id = new_chat(data[1], data[2], data[3])
                        serv.send("0", conn)
                        time.sleep(0.1)
                        serv.send(str(chat_id, conn))

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
                        message(data[1], int(data[2]), data[3])
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

                    except errors.IncorrectKey:
                        serv.send("303", conn)

                    except Exception:
                        serv.send("1", conn)

    except Exception as error:
        log.log.error(error)
        serv.send("0", conn)


def main_way() -> None:
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