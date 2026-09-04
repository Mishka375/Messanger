from libs import monitoring
from libs import server
from libs import errors
from libs import log
import database

import functools
import pickle
import uuid
import time


split_symbol = "*;:;*"

HOST = "0.0.0.0"
SERV_PORT = 70

serv = server.Server()
serv.create_socket(host = HOST, port = SERV_PORT)
serv.start()

count = database.users_execute("SELECT COUNT(*) FROM users;")
monitoring.users_total.set(int(count[0][0]))


def send(func) -> None:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            conn = kwargs.pop("connect")
            out = func(*args, **kwargs)

            correct = out[0]
            result = out[1]

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
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        res = None
        correct = "1"

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

        return [correct, res]

    return wrapper

def metrics(func) -> None:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        monitoring.request_count.inc()
        monitoring.request_queue.inc()
        start = time.time()
        try:
            res = func(*args, **kwargs)

        except Exception:
            monitoring.request_errors.inc()
            raise

        finally:
            monitoring.request_time.observe(time.time() - start)
            monitoring.request_queue.dec()

        return res
    return wrapper


def key_gen() -> str:
    return str(uuid.uuid4())


@send
@errors_view
@metrics
def register(key: str, login: str, password: str, name: str) -> None:
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

@send
@errors_view
@metrics
def enter (key: str, login: str, password: str) -> list:
    try:
        id = database.users_execute("SELECT id FROM users WHERE login=%s AND password=%s;", (login, password))

        if id is None:
            raise errors.IncorrectEnter("Incorrect login or password")

        id = int(id[0][0])
        
        session_key = key_gen()

        if check_session(session_key):
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

@send
@errors_view
@metrics
def out (key: str) -> None:
    try:      
        if not check_session(key):
            log.log.warning("Key is incorrect")
            raise errors.IncorrectKey("Key is incorrect")
        
        monitoring.users_online.dec()
        database.redis_sessions_del(key)
            
    except Exception as error:
        log.log.error(error)
        raise

@send
@errors_view
@metrics
def new_chat (key: str, user_link: str, name: str) -> list:
    try:
        if not check_session(key):
            log.log.warning("Key is not exist")
            raise errors.IncorrectKey("Key is not exist")

        id_1 = int(database.redis_sessions_get(key))

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

@send
@errors_view
@metrics
def choose_chat (key: str, chat_name: str) -> list:
    try:
        if not check_session(key):
            log.log.warning("Key is not exist")
            raise errors.IncorrectKey("Key is not exist")

        id = id = int(database.redis_sessions_get(key))

        chat_id = database.chats_execute("SELECT id FROM chats WHERE name=%s AND (user_1 = %s OR user_2 = %s);", (chat_name, id, id))

        if chat_id is None:
            log.log.warning("Chat is not found")
            raise errors.ChatError("Chat is not found")

        chat_id = int(chat_id[0][0])

        log.log.debug(f"Chat {chat_name} is chossed")
        return [chat_id]
    
    except Exception as error:
        monitoring.request_errors.inc()
        log.log.error(error)
        raise

@send
@errors_view
@metrics
def message (key: str, chat_id: int, message: str) -> None:
    global connects
    try:
        if not check_session(key):
            log.log.warning("Key is not exist")
            raise errors.IncorrectKey("Key is not exist")
        
        sender_id = int(database.redis_sessions_get(key))

        sender_name = database.users_execute("SELECT name FROM personal WHERE id=%s", (sender_id,))

        if sender_name is None:
            log.log.warning("User is not exist")
            raise errors.IncorrectEnter("User is not exist")

        sender_name = sender_name[0][0]

        database.chats_execute("INSERT INTO messages (user_id, chat_id, text) VALUES (%s, %s, %s);", (sender_id, chat_id, message))

        log.log.debug(f"Message {message} was sended")
        monitoring.messages_count.inc()
    
    except Exception as error:
        log.log.error(error)
        raise


def check_session(key: str) -> bool:
    if database.redis_sessions_get(key) is not None:
        return True
    return False


try:
    monitoring.start_http_server(8000)
    print("Monitoring is started")

    while 1:
        try:
            conn = serv.accept()
            log.log.info("connect")
            request = serv.get_message(user=conn).decode()

            if request == "1":
                session_key = key_gen()

                log.log.debug(f"new session: {session_key}")

                database.redis_sessions_set(session_key, 0)

                serv.send(session_key, conn)
                serv.disconnect_user(conn)

                continue

            request = request.split(split_symbol)

            session_key = request[0]

            if not check_session(session_key):
                serv.send("303")
                continue

            log.log.debug(f"request: {request[1]}")

            match request[1]:
                case "register":
                    try:
                        register(session_key, request[2], request[3], request[4], connect=conn)
                    except Exception as error:
                        log.log.error(error)

                case "enter":
                    try:
                        enter(session_key, request[2], request[3], connect=conn)
                    except Exception as error:
                        log.log.error(error)

                case "new_chat":
                    try:
                        new_chat(session_key, request[2], request[3], connect=conn)
                    except Exception as error:
                        log.log.error(error)

                case "choose_chat":
                    try:
                        choose_chat(session_key, request[2], connect=conn)
                    except Exception as error:
                        log.log.error(error)

                case "message":
                    try:
                        message(session_key, int(request[2]), request[3], connect=conn)
                    except Exception as error:
                        log.log.error(error)

                case "out":
                    try:
                        out(session_key, connect=conn)
                    except Exception as error:
                        log.log.error(error)

            serv.disconnect_user(conn)

        except Exception as error:
            log.log.error(error)

except Exception as error:
    log.log.fatal(error)
