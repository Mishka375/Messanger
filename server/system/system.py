from libs import monitoring
from libs import server
from libs import errors
from libs import log
import database

import threading
import pickle
import uuid
import time


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


def send(func) -> None:
    def wrapper(*args, **kwargs):
        try:
            out = func(*args, **kwargs)

            conn = out[0]
            correct = out[1]
            result = out[2]

            serv.send(correct, conn)

            if result is None:
                pass

            elif type(result) is list:
                for value in result:
                    if type(value) is str | bytes:
                        serv.send(value, conn)
                    elif type(value) is list:
                        serv.send(pickle.dumps(value), conn)
                    else:
                        serv.send(str(value), conn)

                    time.sleep(0.1)

        except Exception as error:
            log.log.error(error)

        return None
    return wrapper

def errors_view(func) -> list:
    def wrapper(*args, **kwargs):
        res = None
        correct = "1"

        conn = kwargs["connect"]

        try:
            res = func(*args, **kwargs)
            correct = "0"

        except errors.RedisError:
            correct = "100"
        except errors.RedisDataError:
            correct = "101"
        except errors.RedisTimeoutError:
            correct = "102"
        except errors.RedisBusyError:
            correct = "103"

        except errors.SQLError:
            correct = "200"
        except errors.SQLValueExist:
            correct = "201"
        except errors.SQLValueIsNull:
            correct = "202"
        except errors.SQLRequestError:
            correct = "203"
        except errors.SQLDataError:
            correct = "204"

        except errors.IncorrectData:
            correct = "300"
        except errors.IncorrectLogin:
            correct = "301"
        except errors.IncorrectEnter:
            correct = "302"
        except errors.IncorrectKey:
            correct = "303"
        except errors.IncorrectConnect:
            correct = "304"

        except errors.ChatError:
            correct = "400"

        except Exception as error:
            log.log.error(error)

        return [conn, correct, res]

    return wrapper


def key_gen() -> str:
    return str(uuid.uuid4())

def new_sender() -> None:
    global connects

    log.log.debug("search new senders")

    while 1:
        try:
            sender = chat.accept()
            log.log.debug("try get new sender")
            chat.send("1", sender)
            key = chat.get_message(user = sender).decode()
            id = database.redis_sessions_get(key)

            if id is None:
                log.log.error(f"id is not found")

            else:
                connects[str(id)] = sender
                log.log.debug(f"new seder <{id}>")
                
        except Exception as error:
            log.log.error(error)

threading.Thread(target = new_sender, daemon = True).start()


@send
@errors_view
def register(login: str, password: str, name: str, **kwargs) -> None:
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

@send
@errors_view
def enter (login: str, password: str, **kwargs) -> list:
    start = time.time()

    try:
        id = database.users_execute("SELECT id FROM users WHERE login=%s AND password=%s;", (login, password))

        if id is None:
            raise errors.IncorrectEnter("Incorrect login or password")

        id = int(id[0][0])
        
        session_key = key_gen()

        if database.redis_sessions_get(session_key) is not None:
            log.log.warning ("Key is exist")
            raise errors.IncorrectKey("Key is exist")

        database.redis_sessions_set(session_key, id)

        monitoring.users_online.inc()
        log.log.debug(f"User enter (key: {session_key});")

        chats_data = database.chats_execute("SELECT id, name FROM chats WHERE user_1=%s OR user_2=%s", (id, id))

        user_name = database.users_execute("SELECT name FROM personal WHERE id=%s", (id,))

        if user_name is None:
            raise errors.IncorrectEnter("Incorrect login or password")

        return [split_symbol.join([session_key, user_name[0][0]]), chats_data]
        
    except Exception as error:
        log.log.error(error)
        raise

    finally:
        monitoring.sql_request_time.observe(time.time() - start)

@send
@errors_view
def out (key: str, **kwargs) -> None:
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
        del connects[str(id)]
            
        log.log.debug(f"User {id} is exit")
            
    except Exception as error:
        log.log.error(error)
        raise

    finally:
        monitoring.sql_request_time.observe(time.time() - start)

@send
@errors_view
def new_chat (key: str, user_link: str, name: str, **kwargs) -> list:
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

            return [int(chat_id[0][0])]

        else:
            log.log.warning(f"Chat {name} wasn't created, same id")
            raise errors.ChatError("One user in chat")

    except Exception as error:
        log.log.error(error)
        raise

    finally:
        monitoring.sql_request_time.observe(time.time() - start)

@send
@errors_view
def choose_chat (key: str, chat_name: str, **kwargs) -> list:
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
        return [chat_id]
    
    except Exception as error:
        chat_id = None
        log.log.error(error)
        raise

    finally:
        monitoring.sql_request_time.observe(time.time() - start)

@send
@errors_view
def message (key: str, chat_id: int, message: str, **kwargs) -> None:
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
            interlocur_conn = connects[str(interlocur_id)]
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
            data = serv.get_message(user = conn).decode()
            data = data.split(split_symbol)

            match data[0]:
                case "register":
                    try:
                        register(data[1], data[2], data[3], connect=conn)
                    except Exception as error:
                        log.log.error(error)

                case "enter":
                    try:
                        enter(data[1], data[2], connect=conn)
                    except Exception as error:
                        log.log.error(error)
                        
                case "new_chat":
                    try:
                        new_chat(data[1], data[2], data[3], connect=conn)
                    except Exception as error:
                        log.log.error(error)

                case "choose_chat":
                    try:
                        choose_chat(data[1], data[2], connect=conn)
                    except Exception as error:
                        log.log.error(error)

                case "message":
                    try:
                        message(data[1], int(data[2]), data[3], connect=conn)
                    except Exception as error:
                        log.log.error(error)
                
                case "out":
                    try:
                        out(data[1], connect=conn)
                    except Exception as error:
                        log.log.error(error)

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
