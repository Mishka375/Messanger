from libs import server
from libs import log
import threading
import pickle
import time
import os

os.system("clear")

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

chat_name = ""
correct_chat_id = None
saved_chats = {}


def get_messages(key: str) -> None:
    log.log.debug("chat start")

    chat_conn = server.Client()
    chat_conn.connect(HOST, CHAT_PORT)

    correct = chat_conn.get_message().decode()

    if int(correct):
        chat_conn.send_all(key)
        log.log.debug("Chat is correct")

        while 1:
            message = (chat_conn.get_message().decode()).split(split_symbol)

            if in_chat:
                print(f"\r[{message[0]}]: {message[1]}")

            cursor = []
            if len(chat_name):
                cursor.append(chat_name)

            cursor.append(user_name)
            print(f"{':'.join(cursor)}-> ", end="")

            time.sleep(0.1)
    else:
        log.log.warning("Chat is disconnect")


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

                    match correct:
                        case 0:
                            pass
                        case 301:
                            print("! The login is already taken")
                        case 1:
                            print("! Unknown error")
                        case _:
                            print(f"! Error code: {correct}")

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

                        match correct:
                            case 0:
                                data = conn.get_message().decode()
                                data = data.split(split_symbol)

                                session_key = data[0]
                                user_name = data[1]

                                chats_data = conn.get_message()

                                if chats_data != b"None":
                                    chats_data = pickle.loads(chats_data)

                                    for chats in chats_data:
                                        saved_chats[chats[0]]=chats[1]

                                    log.log.debug(f"Chats data: {chats_data}")

                                chat = threading.Thread(
                                    target=get_messages,
                                    daemon=True,
                                    args=(session_key,)
                                )

                                chat.start()

                            case 302:
                                print("! Incorrect login or password")

                            case 303:
                                print("! Try again")

                            case 1:
                                print("! Unknown error")

                            case _:
                                print(f"! Error code: {correct}")

                    except Exception as error:
                        log.log.error(error)
                else:
                    pass

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

                    match correct:
                        case 0:
                            chat_id = int(conn.get_message().decode())
                            saved_chats[chat_id]=chat_name
                        case 302:
                            print("! Link is incorrect")
                        case 303:
                            print("! Incorrect session key")
                        case 400:
                            pass
                        case 1:
                            print("! Unknown error")
                        case _:
                            print(f"! Error code: {correct}")


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

                    match correct:
                        case 0:
                            correct_chat_id = conn.get_message().decode()
                            in_chat = 1
                            saved_chats[correct_chat_id]=chat_name
                        case 303:
                            print("! Incorrect key")
                        case 400:
                            print("! Chat is not found")
                        case 1:
                            print("! Unknown error")
                        case _:
                            print(f"! Error code: {correct}")


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

                        match correct:
                            case 0:
                                pass
                            case 303:
                                print("! Incorrect key")
                            case 400:
                                print("! Chat is not found")
                            case 1:
                                print("! Unknown error")
                            case _:
                                print(f"! Error code: {correct}")

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

                        match correct:
                            case 0:
                                pass
                            case 303:
                                print("! Incorrect key")
                            case 1:
                                print("! Unknown error")
                            case _:
                                print(f"! Error code: {correct}")

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
