from libs import log, gui
import database

try:
    while True:
        command = input("ROOT-> ").strip()

        try:
            match command:
                case "sql_users":
                    command = input("SQU> ")
                    try:
                        database.users_execute(command)
                        try:
                            result = database.cursor_users.fetchall()
                            if result:
                                for row in result:
                                    print(row)
                            else:
                                print("Request is complete")
                        except database.psycopg2.ProgrammingError:
                            print("Request is comlete")
                    except Exception as e:
                        print(f"SQL error: {e}")

                case "sql_chats":
                    command = input("SQC> ")
                    try:
                        database.chats_execute(command)
                        try:
                            result = database.cursor_chats.fetchall()
                            if result:
                                for row in result:
                                    print(row)
                            else:
                                print("Request is complete")
                        except database.psycopg2.ProgrammingError:
                            print("Request is comlete")
                    except Exception as e:
                        print(f"SQL error: {e}")

                case "exit":
                    break
                
                case _:
                    pass

        except Exception as error:
            log.log.error(error)
            print(error)

except Exception as error:
    log.log.error(error)
    print(error)