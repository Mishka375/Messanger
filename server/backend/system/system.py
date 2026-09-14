from libs import monitoring
from libs import errors
from libs import log
import database

import functools
import uuid
import time


from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/registry', methods=['POST'])
def reg():
    data = request.get_json() or {}

    name = data.get('name')
    login = data.get('login')
    password = data.get('password')

    if not login:
        return jsonify({"error":"You should enter login"}), 400

    try:
        register(login, password, name)

    except errors.IncorrectLogin:
        return jsonify({"error": "Login is exist"}), 409
    except errors.SQLValueIsNull:
        return jsonify({"error": "Enter values"}), 400
    except Exception:
        log.log.exception("reg failed")
        return jsonify({"error": "Error"}), 500

    return jsonify({"message":"User is registered"})

@app.route('/enter', methods=['POST'])
def ent():
    data = request.get_json() or {}

    login = data.get('login')
    password = data.get('password')

    if not login or not password:
        return jsonify({"error": "You should enter login and password"}), 400

    try:
        result = enter(login, password)
    except errors.IncorrectEnter:
        return jsonify({"error": "Uncorrect login or password"}), 401
    except errors.IncorrectKey:
        return jsonify({"error": "Key is exist"}), 409
    except Exception:
        log.log.exception("enter failed")
        return jsonify({"error": "Enter error"}), 500

    return jsonify({
        "session_key": result["session_key"],
        "name":        result["user_name"],
        "chats":       result["chats_data"],
    }), 200


@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200


try:
    count = database.users_execute("SELECT COUNT(*) FROM users;")
    monitoring.users_total.set(int(count[0][0]))
except Exception:
    log.log.exception("init metrics failed")


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


@metrics
def register(login: str, password: str, name: str) -> None:
    try:
        database.users_execute("INSERT INTO users (login, password) VALUES (%s, %s);", (login, password))

        id = database.users_execute("SELECT id FROM users WHERE login=%s AND password=%s", (login, password))

        if id is None:
            log.log.warning("User is not found")
            raise errors.IncorrectEnter("User is not found")

        id = int(id[0][0])

        database.users_execute("INSERT INTO personal (id, identificator, name) VALUES (%s, %s, %s);", (id, "^"+login, name))

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

@metrics
def enter (login: str, password: str) -> list:
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

        return {"session_key":session_key, "chats_data":chats_data, "user_name":user_name[0][0]}

    except Exception as error:
        log.log.error(error)
        raise

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

        else:
            log.log.warning(f"Chat {name} wasn't created, same id")
            raise errors.ChatError("One user in chat")
        
        return {"chat_id": int(chat_id[0][0])}

    except Exception as error:
        log.log.error(error)
        raise

@metrics
def choose_chat (key: str, chat_name: str) -> list:
    try:
        if not check_session(key):
            log.log.warning("Key is not exist")
            raise errors.IncorrectKey("Key is not exist")

        id = int(database.redis_sessions_get(key))

        chat_id = database.chats_execute("SELECT id FROM chats WHERE name=%s AND (user_1 = %s OR user_2 = %s);", (chat_name, id, id))

        if chat_id is None:
            log.log.warning("Chat is not found")
            raise errors.ChatError("Chat is not found")

        chat_id = int(chat_id[0][0])

        log.log.debug(f"Chat {chat_name} is chossed")
        return {"chat_id":chat_id}
    
    except Exception as error:
        log.log.error(error)
        raise

@metrics
def message (key: str, chat_id: int, message: str) -> None:
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

        log.log.debug(f"User <{sender_id}:{sender_name}> send <{message}>")

        database.chats_execute("INSERT INTO messages (user_id, chat_id, text) VALUES (%s, %s, %s);", (sender_id, chat_id, message))

        log.log.debug(f"Message {message} was sended")
        monitoring.messages_count.inc()
    
    except Exception as error:
        log.log.error(error)
        raise


@metrics
def change_key (key: str) -> str:
    try:
        if not check_session(key):
                log.log.warning("Key is not exist")
                raise errors.IncorrectKey("Key is not exist")

        new_key = key_gen()

        database.redis_sessions_set(new_key, database.redis_sessions_get(key))
        database.redis_sessions_del(key)

        return new_key

    except Exception as error:
        log.log.error(error)
        raise

def check_session(key: str) -> bool:
    if database.redis_sessions_get(key) is not None:
        return True
    return False


if __name__ == "__main__":
    monitoring.start_http_server(8000)
    app.run(host='0.0.0.0', port=5000)