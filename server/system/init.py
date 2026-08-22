import monitoring, database
from libs import log
import time

def register (login, password, name):
    start = time.time()

    try:
        database.users_execute("INSERT INTO users (login, password) VALUES (%s, %s);", (login, password))
        database.users_execute("SELECT id FROM users WHERE login=%s", (login,))
        id = database.cursor_users.fetchone()[0]
        database.users_execute("INSERT INTO personal VALUES (%s, %s, %s)", (id, "^"+login, name))
        
        monitoring.users_total.inc()
        
        print(f"Пользователь {login} создан (ID: {id})")
        
    except Exception as error:
        monitoring.sql_request_errors.inc()
        print(f"Ошибка регистрации: {error}")
    finally:
        monitoring.sql_request_time.observe(time.time() - start)

def enter (login, password):
    start = time.time()
    
    try:
        database.users_execute("SELECT id FROM users WHERE login=%s AND password=%s", (login, password))
        result = database.cursor_users.fetchone()
        
        if result:
            id = result[0]
            key = f"{login}:{id}"
            
            database.redis_set(key, id, ex=3600)

            monitoring.users_online.inc()

            database.users_execute('SELECT name FROM personal WHERE id=%s', (id, ))
            
            print(f"Пользователь {database.cursor_users.fetchone()[0]} вошел (ключ: {key})")
            return key
        else:
            print("Неверный логин или пароль")
            return None
            
    except Exception as error:
        monitoring.sql_request_errors.inc()
        print(f"Ошибка входа: {error}")
        return None
    finally:
        monitoring.sql_request_time.observe(time.time() - start)

def out (key):
    start = time.time()
    
    try:
        id = database.redis_get(key)
        database.users_execute("SELECT name FROM personal WHERE id=%s", (id))
        result = database.cursor_users.fetchone()[0]
        
        if result:
            monitoring.users_online.dec()
            database.redis_del(key)
            
            print(f"Пользователь {result} вышел")
        else:
            print("Неверный ключ")
            
    except Exception as error:
        monitoring.sql_request_errors.inc()
        print(f"Ошибка входа: {error}")
    finally:
        monitoring.sql_request_time.observe(time.time() - start)


def check_session(key):
    if database.redis_get(key):
        return True
    return False

print("Система запущена")
print("Команды: new_user, enter, sql, get, exit")

while True:
    command = input("CMD> ").strip()

    match command:
        case "new_user":
            user = input("REG> ").split()
            if len(user) == 3:
                register(user[0], user[1], user[2])
            else:
                print("Формат: логин пароль имя")
                
        case "enter":
            ent = input("ENT> ").split()
            if len(ent) == 2:
                key = enter(ent[0], ent[1])
                if key:
                    print(f"Сессия: {key}")
            else:
                print("Формат: логин пароль")

        case "out":
            key = input("OUT> ")
            out(key)
                
        case "sql":
            command = input("SQL> ")
            try:
                database.users_execute(command)
                try:
                    result = database.cursor_users.fetchall()
                    if result:
                        for row in result:
                            print(row)
                    else:
                        print("Запрос выполнен")
                except database.psycopg2.ProgrammingError:
                    print("Запрос выполнен")
            except Exception as e:
                print(f"Ошибка SQL: {e}")
                
        case "get":
            key = input("GET> ")
            value = database.redis_get(key)
            print(f"Значение: {value}" if value else f"Ключ '{key}' не найден")
            
        case "exit":
            break
            
        case _:
            pass

database.cursor_users.close()
database.cursor_chats.close()

database.connect_users.close()
database.connect_chats.close()

print("Система остановлена")
