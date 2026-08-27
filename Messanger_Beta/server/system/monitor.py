import system
from system import log, database, gui, serv

log.log.info("System is boot")


local_server = system.Active()

try:
    while 1:
        conn = serv.accept()
        log.log.info("new connect")
        local_server.start(conn)

except KeyboardInterrupt:
    database.cursor_users.close()
    database.cursor_chats.close()

    database.connect_users.close()
    database.connect_chats.close()

    log.log.info("System is stoped")

except Exception as error:
    log.log.error(error)

# while True:
#     command = input(f"{user_name}-> ").strip()

#     match command:
#         case "register":
#             print("# REGISTER")

#             try:
#                 login = input("LOGIN------> ").strip()
#                 password = input("PASSWORD---> ").strip()
#                 name = input("NAME-------> ").strip()

#                 system.register(login, password, name)
                
#             except Exception as error:
#                 log.log.error(error)

#         case "enter":
#             if session_key is None:
#                 print("# ENTER")

#                 try:
#                     login = input("LOGIN------> ").strip()
#                     password = input("PASSWORD---> ").strip()

#                     session_key = system.enter(login, password)
#                     database.users_execute(f"SELECT name FROM personal WHERE id={database.redis_get(session_key)}")
#                     user_name = database.cursor_users.fetchone()[0]

#                 except Exception as error:
#                     log.log.error(error)
#             else:
#                 None

#         case "new_chat":
#             print("# NEW CHAT")

#             try:
#                 interlocur = input("INTERLOCUR-> ").strip()
#                 chat_name = input("CHAT_NAME--> ").strip()

#                 system.new_chat(session_key, interlocur, chat_name)
#             except Exception as error:
#                 log.log.error(error)

#         case "choose_chat":
#             print("# CHOOSE CHAT")

#             try:
#                 chat_name = input("CHAT_NAME--> ").strip()
#                 chat_id = system.choose_chat(session_key, chat_name)

#                 meesage = None
#                 while 1:
#                     message = input(f"{chat_name}:{user_name}-> ").strip()

#                     if message == "/exit":
#                         break

#                     system.message(session_key, chat_id, message)
                
#                 chat_id = None

#             except Exception as error:
#                 log.log.error(error)

#         case "out":
#             if session_key is not None:
#                 try:
#                     system.out(session_key)
#                     session_key = None
#                     user_name = "UNKNOWN"
#                 except Exception as error:
#                     log.log.error(error)
#             else:
#                 None
                
#         case "sql_users":
#             command = input("SQU> ")
#             try:
#                 database.users_execute(command)
#                 try:
#                     result = database.cursor_users.fetchall()
#                     if result:
#                         for row in result:
#                             print(row)
#                     else:
#                         print("Request is complete")
#                 except database.psycopg2.ProgrammingError:
#                     print("Request is comlete")
#             except Exception as e:
#                 print(f"SQL error: {e}")

#         case "sql_chats":
#             command = input("SQC> ")
#             try:
#                 database.chats_execute(command)
#                 try:
#                     result = database.cursor_chats.fetchall()
#                     if result:
#                         for row in result:
#                             print(row)
#                     else:
#                         print("Request is complete")
#                 except database.psycopg2.ProgrammingError:
#                     print("Request is comlete")
#             except Exception as e:
#                 print(f"SQL error: {e}")

#         case "whoami":
#             print(session_key, user_name)
        
#         case "get":
#             key = input("GET> ")
#             value = database.redis_get(key)
#             print(f"Value: {value}" if value else f"Key '{key}' is not found")
            
#         case "exit":
#             break
        
#         case _:
#             pass

# database.cursor_users.close()
# database.cursor_chats.close()

# database.connect_users.close()
# database.connect_chats.close()

# log.log.info("System is stoped")