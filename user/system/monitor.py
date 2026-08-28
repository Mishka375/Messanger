from libs import server
from libs.server import log
import threading
import pickle
import sqlite3
import time


split_symbol = "*;:;*"

HOST = "192.168.0.20"
SERV_PORT = 70
CHAT_PORT = 71

conn = server.Client()
conn.connect(HOST, SERV_PORT)

session_key = None
user_name = "UNKNOWN"

in_chat = 0
chat = None

correct_chat_id = None
saved_chats = {}

def print_error(error_code: int) -> None:
    error = ""
    match error_code:

        # Unknown errors
        case 1:
            error = "Unknown error"

        # Redis errors
        case 101:
            error = "Redis: Incorrect data"

        case 102:
            error = "Redis: Timeout"

        case 102:
            error = "Redis: Busy"

        # SQL errors
        case 200:
            error = "SQL: Error"

        case 201:
            error = "SQL: Value exist"

        case 202:
            error = "SQL: Value is Null"

        case 203:
            error = "SQL: Request"

        case 204:
            error = "SQL: Data"

        # Incorrect actions
        case 301:
            error = "Incorrect login"

        case 302:
            error = "Incorrect enter"

        case 303:
            error = "Incorrect key"

        # Chat errors
        case 400:
            error = "Chat: Error"

        # Correct
        case 0:
            error = "Correct"

        case _:
            error = error_code
    print(f"# {error}")


def get_messages(key: str) -> None:
    log.log.debug("chat start")

    chat_conn = server.Client()
    chat_conn.connect(HOST, CHAT_PORT)

    correct = chat_conn.get_message().decode()

    if int(correct):
        chat_conn.send_all(key)

        while 1:
            message = (chat_conn.get_message().decode()).split(split_symbol)

            if in_chat:
                print(f"# {message[0]}: {message[1]}")

            time.sleep(0.1)

try:
    connect = conn.get_message().decode()

    if connect:
        print("=== Connect ===")

    while connect:
        command = input(f"{user_name}-> ").strip()

        match command:
            case "register":
                print("# REGISTER")

                try:
                    login = input("LOGIN------> ").strip()
                    password = input("PASSWORD---> ").strip()
                    name = input("NAME-------> ").strip()

                    conn.send_all(
                        split_symbol.join(
                            [command,
                             login,
                             password,
                             name]
                        )
                    )

                    correct = int(conn.get_message().decode())

                    print_error(correct)

                except Exception as error:
                    log.log.error(error)

            case "enter":
                if session_key is None:
                    print("# ENTER")

                    try:
                        login = input("LOGIN------> ").strip()
                        password = input("PASSWORD---> ").strip()

                        conn.send_all(
                            split_symbol.join(
                                [command,
                                 login,
                                 password]
                            )
                        )

                        correct = int(conn.get_message().decode())

                        if not correct:
                            data = conn.get_message().decode()
                            data = data.split(split_symbol)

                            session_key = data[0]
                            user_name = data[1]

                            chats_data = pickle.loads(conn.get_message())
                            for chats in chats_data:
                                saved_chats[chats[0]]=chats[1]

                            print(f"Your chats {chats_data}")

                            log.log.debug(f"Chats data: {chats_data}")

                            chat = threading.Thread(
                                target=get_messages,
                                daemon=True,
                                args=(session_key,)
                            )

                            chat.start()

                        print_error(correct)

                    except Exception as error:
                        log.log.error(error)
                else:
                    None

            case "new_chat":
                print("# NEW CHAT")

                try:
                    interlocur = input("INTERLOCUR-> ").strip()
                    chat_name = input("CHAT_NAME--> ").strip()

                    conn.send_all(
                        split_symbol.join(
                            [command,
                             session_key,
                             interlocur,
                             chat_name]
                        )
                    )

                    correct = int(conn.get_message().decode())

                    print_error(correct)

                    if correct:
                        chat_id = int(conn.get_message().decode())
                        saved_chats[chat_id]=chat_name

                except Exception as error:
                    log.log.error(error)

            case "choose_chat":
                print("# CHOOSE CHAT")

                try:
                    chat_name = input("CHAT_NAME--> ").strip()

                    conn.send_all(
                        split_symbol.join(
                            [command,
                             session_key,
                             chat_name]
                            )
                    )

                    correct = int(conn.get_message().decode())

                    meesage = None

                    if not correct:
                        correct_chat_id = conn.get_message().decode()
                        in_chat = 1
                        saved_chats[correct_chat_id]=chat_name
                    else:
                        print_error(correct)

                    while not correct:
                        message = input(f"{chat_name}:{user_name}-> ").strip()

                        if message == "/exit":
                            break

                        conn.send_all(
                            split_symbol.join(
                                ["message",
                                 session_key,
                                 correct_chat_id,
                                 message]
                            )
                        )

                        correct = int(conn.get_message().decode())

                        print_error(correct)

                    in_chat = 0
                    correct_chat_id = None
                    chat_name = None

                except Exception as error:
                    log.log.error(error)

            case "out":
                if session_key is not None:
                    try:
                        conn.send_all(
                            split_symbol.join(
                                [command,
                                 session_key]
                            )
                        )

                        session_key = None
                        user_name = "UNKNOWN"

                        correct = int(conn.get_message().decode())

                        print_error(correct)

                    except Exception as error:
                        log.log.error(error)
                else:
                    None

            case "exit":
                connect = 0
                break

            case _:
                pass

    print("=== Disconnect ===")

except KeyboardInterrupt:
    print("Disconnect")
    exit()

except Exception as error:
    print(error)
    log.log.error(error)
