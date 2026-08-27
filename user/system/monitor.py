from libs import server
from libs.server import log
import threading, time

HOST = "192.168.0.22"
SERV_PORT = 70
CHAT_PORT = 71

conn = server.Client()
conn.connect(HOST, SERV_PORT)

session_key = None
chat_id = None
user_name = "UNKNOWN"

in_chat = 0

chat = None

def print_error(error_code):
    error = ""
    match error_code:

        case 101:
            error = "Redis: Incorrect data"

        case 102:
            error = "Redis: Timeout"

        case 102:
            error = "Redis: Busy"

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

        case 301:
            error = "Incorrect login"
        
        case 302:
            error = "Incorrect enter"

        case 303:
            error = "Incorrect key"

        case 400:
            error = "Chat: Error"

        case 0:
            error = "Correct"
    print(f"# {error}")


def get_messages (key):
    log.log.debug("chat start")

    global in_chat

    chat_conn = server.Client()
    chat_conn.connect(HOST, CHAT_PORT)

    print(chat_conn.get_message())
    chat_conn.send_all(key)

    while 1:
        message = chat_conn.get_message()

        if in_chat:
            print(f"# Message: {message}")
            
        time.sleep(0.1)

try:
    connect = int(conn.get_message())

    while connect:
        command = input(f"{user_name}-> ").strip()

        match command:
            case "register":
                print("# REGISTER")

                try:
                    login = input("LOGIN------> ").strip()
                    password = input("PASSWORD---> ").strip()
                    name = input("NAME-------> ").strip()

                    conn.send_all (f"{command}*;:;*{login}*;:;*{password}*;:;*{name}")

                    correct = int(conn.get_message())

                    print_error(correct)
                    
                except Exception as error:
                    log.log.error(error)

            case "enter":
                if session_key is None:
                    print("# ENTER")

                    try:
                        login = input("LOGIN------> ").strip()
                        password = input("PASSWORD---> ").strip()

                        conn.send_all(f"{command}*;:;*{login}*;:;*{password}")

                        correct = int(conn.get_message())

                        if not correct:
                            data = conn.get_message()
                            data = data.split("*;:;*")

                            if data[0] != "0":
                                session_key = data[0]
                                user_name = data[1]

                                chat = threading.Thread(target = get_messages, daemon = True, args = (session_key,))
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

                    conn.send_all(f"{command}*;:;*{session_key}*;:;*{interlocur}*;:;*{chat_name}")
                
                    correct = int(conn.get_message())

                    print_error(correct)
                
                except Exception as error:
                    log.log.error(error)

            case "choose_chat":
                print("# CHOOSE CHAT")

                try:
                    chat_name = input("CHAT_NAME--> ").strip()

                    conn.send_all(f"{command}*;:;*{session_key}*;:;*{chat_name}")

                    correct = int(conn.get_message())

                    meesage = None

                    if not correct:
                        chat_id = conn.get_message()
                        in_chat = 1
                    else:
                        print_error(correct)

                    while not correct:
                        message = input(f"{chat_name}:{user_name}-> ").strip()

                        if message == "/exit":
                            break

                        conn.send_all(f"message*;:;*{session_key}*;:;*{chat_id}*;:;*{message}")

                        correct = int(conn.get_message())

                        print_error(correct)

                    in_chat = 0
                    chat_id = None
                    chat_name = None

                except Exception as error:
                    log.log.error(error)

            case "out":
                if session_key is not None:
                    try:
                        conn.send_all(f"out*;:;*{session_key}")
                        session_key = None
                        user_name = "UNKNOWN"

                        correct = int(conn.get_message())

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

except KeyboardInterrupt:
    print("Disconnect")
    exit()

except Exception as error:
    print(error)
    log.log.error(error)