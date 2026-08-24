from libs import server
from libs.server import log
import threading

HOST = "192.168.0.22"
SERV_PORT = 70
CHAT_PORT = 71

conn = server.Client()
conn.connect(HOST, SERV_PORT)

session_key = None
chat_id = None
user_name = "UNKNOWN"

in_chat = threading.Event()

chat = None

def get_messages (key):
    log.log.debug("chat start")

    global in_chat

    chat_conn = server.Client()
    chat_conn.connect(HOST, CHAT_PORT)

    print(chat_conn.get_message())
    chat_conn.send_all(key)

    while in_chat.is_set():
        message = chat_conn.get_message()
        print(f"# Message: {message}")

try:
    print(conn.get_message())

    while True:
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

                    if correct:
                        print("# Correct")
                    else:
                        print("# Incorrect")
                    
                except Exception as error:
                    log.log.error(error)

            case "enter":
                if session_key is None:
                    print("# ENTER")

                    try:
                        login = input("LOGIN------> ").strip()
                        password = input("PASSWORD---> ").strip()

                        conn.send_all(f"{command}*;:;*{login}*;:;*{password}")

                        data = conn.get_message()
                        data = data.split("*;:;*")
                        correct = conn.get_message()

                        if data[0] != "0" and correct:
                            session_key = data[0]
                            user_name = data[1]

                            chat = threading.Thread(target = get_messages, daemon = True, args = (session_key,))
                        
                            print("# Correct")
                        else:
                            print("# Incorrect")

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

                    if correct:
                        print("# Correct")
                    else:
                        print("# Incorrect")
                
                except Exception as error:
                    log.log.error(error)

            case "choose_chat":
                print("# CHOOSE CHAT")

                try:
                    chat_name = input("CHAT_NAME--> ").strip()

                    conn.send_all(f"{command}*;:;*{session_key}*;:;*{chat_name}")
                    chat_id = conn.get_message()

                    meesage = None

                    correct = int(conn.get_message())

                    if correct:
                        print("# Correct")
                        in_chat.set()
                        chat.start()
                    else:
                        print("# Incorrect")

                    while correct:
                        message = input(f"{chat_name}:{user_name}-> ").strip()

                        if message == "/exit":
                            break

                        conn.send_all(f"message*;:;*{session_key}*;:;*{chat_id}*;:;*{message}")

                        correct = int(conn.get_message())

                        if correct:
                            print("# Correct")
                        else:
                            print("# Incorrect")

                    in_chat.clear()
                    chat_id = None

                except Exception as error:
                    log.log.error(error)

            case "out":
                if session_key is not None:
                    try:
                        conn.send_all(f"out*;:;*{session_key}")
                        session_key = None
                        user_name = "UNKNOWN"

                        correct = int(conn.get_message())

                        if correct:
                            print("# Correct")
                        else:
                            print("# Incorrect")

                    except Exception as error:
                        log.log.error(error)
                else:
                    None
                    
            # case "sql_users":
            #     command = input("SQU> ")
            #     try:
            #         database.users_execute(command)
            #         try:
            #             result = database.cursor_users.fetchall()
            #             if result:
            #                 for row in result:
            #                     print(row)
            #             else:
            #                 print("Request is complete")
            #         except database.psycopg2.ProgrammingError:
            #             print("Request is comlete")
            #     except Exception as e:
            #         print(f"SQL error: {e}")

            # case "sql_chats":
            #     command = input("SQC> ")
            #     try:
            #         database.chats_execute(command)
            #         try:
            #             result = database.cursor_chats.fetchall()
            #             if result:
            #                 for row in result:
            #                     print(row)
            #             else:
            #                 print("Request is complete")
            #         except database.psycopg2.ProgrammingError:
            #             print("Request is comlete")
            #     except Exception as e:
            #         print(f"SQL error: {e}")

            case "whoami":
                print(session_key, user_name)
            
            # case "get":
            #     key = input("GET> ")
            #     value = database.redis_get(key)
            #     print(f"Value: {value}" if value else f"Key '{key}' is not found")
            
            case "exit":
                break
            
            case _:
                pass

except KeyboardInterrupt:
    print("Disconnect")
    exit()

except Exception as error:
    log.log.error(error)