from libs import server
from libs import log

import functools
import threading
import pickle
import time
import os

os.system("clear")

split_symbol = "*;:;*"

HOST = "192.168.0.20"
SERV_PORT = 70

session_key = None
user_name = "UNKNOWN"

in_chat = 0
chat = None

chat_name = ""
correct_chat_id = None
saved_chats = {}


def connect(func) -> None:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> None:
        conn = server.Client()
        conn.connect(HOST, SERV_PORT)
        res = func(conn, *args, **kwargs)

        return res
    return wrapper


@connect
def get_messages(conn):
    pass

@connect
def init_session(conn) -> bool:
    global session_key

    conn.send("1")
    session_key = conn.get_message().decode()

    log.log.debug(session_key)

    if session_key:
        log.log.info("connect")
        return True

    log.log.info("disconnect")
    return False


@connect
def register(conn) -> None:
    print("# REGISTER")

    try:
        login    = input("LOGIN------> ").strip()
        password = input("PASSWORD---> ").strip()
        name     = input("NAME-------> ").strip()

        conn.send_all(
            split_symbol.join(
                [session_key,
                 "register",
                 login,
                 password,
                 name]
            )
        )

        correct = int(conn.get_message().decode())

        match correct:
            case 0:
                pass
            case 303:
                print("! Key is incorrect")
            case 301:
                print("! The login is already taken")
            case 1:
                print("! Unknown error")
            case _:
                print(f"! Error code: {correct}")

    except Exception as error:
        log.log.error(error)

@connect
def enter(conn) -> None:
    global session_key, user_name, saved_chats

    print("# ENTER")

    try:
        login    = input("LOGIN------> ").strip()
        password = input("PASSWORD---> ").strip()

        conn.send(
            split_symbol.join(
                [session_key,
                 "enter",
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

            case 302:
                print("! Incorrect login or password")
            case 303:
                print("! Key is incorrect")
            case 1:
                print("! Unknown error")
            case _:
                print(f"! Error code: {correct}")

    except Exception as error:
        log.log.error(error)

@connect
def new_chat(conn) -> None:
    print("# NEW CHAT")

    try:
        interlocur = input("INTERLOCUR-> ").strip()
        chat_name  = input("CHAT_NAME--> ").strip()

        conn.send_all(
            split_symbol.join(
                [session_key,
                 "new_chat",
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
                print("! Key is incorrect")
            case 400:
                pass
            case 1:
                print("! Unknown error")
            case _:
                print(f"! Error code: {correct}")

    except Exception as error:
        log.log.error(error)

@connect
def message(conn) -> None:
    try:
        message = input(f"{chat_name}:{user_name}-> ").strip()

        if message == "/exit":
            return 1

        conn.send_all(
            split_symbol.join(
                [session_key,
                "message",
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

        return correct

    except Exception as error:
        log.log.error(error)

@connect
def choose_chat(conn) -> None:
    global in_chat

    print("# CHOOSE CHAT")

    try:
        chat_name = input("CHAT_NAME--> ").strip()

        conn.send_all(
            split_symbol.join(
                [session_key,
                 "choose_chat",
                 chat_name]
                )
        )

        correct = int(conn.get_message().decode())

        match correct:
            case 0:
                correct_chat_id = conn.get_message().decode()
                in_chat = 1
                saved_chats[correct_chat_id]=chat_name
            case 303:
                print("! Key is incorrect")
            case 400:
                print("! Chat is not found")
            case 1:
                print("! Unknown error")
            case _:
                print(f"! Error code: {correct}")


        while not correct:
            correct = message()

        in_chat = 0
        correct_chat_id = None
        chat_name = None

    except Exception as error:
        log.log.error(error)

@connect
def out(conn):
    global user_name, session_key

    try:
        conn.send_all(
            split_symbol.join(
                [session_key,
                 "out"]
            )
        )

        session_key = None
        user_name = "UNKNOWN"

        correct = int(conn.get_message().decode())

        match correct:
            case 0:
                pass
            case 303:
                print("! Key is incorrect")
            case 1:
                print("! Unknown error")
            case _:
                print(f"! Error code: {correct}")

    except Exception as error:
        log.log.error(error)


connect_status = init_session()

try:
    while connect_status:
        command = input(f"{user_name}-> ").strip()

        match command:
            case "register":
                register()

            case "enter":
                enter()

            case "new_chat":
                new_chat()

            case "choose_chat":
                choose_chat()

            case "out":
                out()

            case "exit":
                break

            case _:
                pass

    print("=== Disconnect ===")

    # while 1:
    #     pass

except KeyboardInterrupt:
    print("Disconnect")
    exit()

except Exception as error:
    print(error)
    log.log.error(error)
