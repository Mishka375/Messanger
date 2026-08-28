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
                        result = database.users_execute(command)
                        if result:
                            for row in result:
                                print(row)
                        else:
                            print("Request is complete")
                    except Exception as e:
                        print(f"SQL error: {e}")

                case "sql_chats":
                    command = input("SQC> ")
                    try:
                        result = database.chats_execute(command)

                        if result:
                            for row in result:
                                print(row)
                        else:
                            print("Request is complete")

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