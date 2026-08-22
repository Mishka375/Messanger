from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
from flask import Flask, Response, request

import psycopg2, redis
import os, threading, time, random, logging


app = Flask(__name__)


r = redis.Redis(
    host = "redis",
    port = 6379,
    decode_responses = True
)



http_request_total = Counter (
    "backend_http_request_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"]
)

http_request_duration = Histogram (
    "backend_http_request_duration",
    "HTTP request duration",
    ["method", "endpoint"]
)

http_requests_in_progress = Gauge (
    "backend_http_requests_in_progress",
    "Number of HTTP requests"
)

http_errors_total = Counter (
    "backend_http_errors_total",
    "Total number of HTTP errors"
)


users_total = Gauge (
    "backend_users_total",
    "Total number of registered users"
)

users_online = Gauge (
    "backend_users_online",
    "Number of users currently online"
)

users_login_total = Counter (
    "backend_user_login_total",
    "Total number of successful user login"
)

user_logouts_total = Counter (
    "backend_user_logout_total",
    "Total number of user logouts"
)


db_queries_total = Counter (
    "backend_db_queries_total",
    "Total number of database queries"
)

db_query_duration = Histogram (
    "backend_db_query_duration",
    "Database query duration"
)

db_errors_total = Counter (
    "backend_db_errors_total",
    "Total number of database errors"
)


redis_operations_total = Counter (
    "backend_redis_operations_total",
    "Total number of Redis operations"
)

redis_errors_total = Counter (
    "backend_redis_errors_total",
    "Total number of Redis error"
)






@app.route("/metrics")
def metrics():
    return Response(
        generate_latest(),
        mimetype="text/plain"
    )

def run_metrics_server():
    app.run(
        host = "0.0.0.0",
        port = 8000
    )


@app.before_request
def before_request ():
    request.start_time = time.time()
    http_requests_in_progress.inc()


@app.after_request
def after_request (response):
    duration = time.time() - request.start_time
    http_request_total.labels (
        method = request.method,
        endpoint = request.endpoint or "unknown",
        status = response.status_code
    ).inc()

    if response.status_code >= 400:
        http_errors_total.inc()
    
    http_request_duration.labels (
        method = request.method,
        endpoint = request.endpoint or "unknown"
    ).observe(duration)

    http_requests_in_progress.dec()

    return response


#@app.errorhandler(Exception)
#def handle_error (error):
#    http_errors_total.inc()
#    raise error


def update_users_total():
    connection = psycopg2.connect(
        dbname=os.environ["DATABASE_NAME"],
        user=os.environ["DATABASE_USER"],
        password=os.environ["DATABASE_PASSWORD"],
        host=os.environ["DATABASE_HOST_USERS"],
        port=os.environ["DATABASE_PORT"]
    )
    cursor = connection.cursor()

    while True:
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM users"
            )
            count = cursor.fetchone()[0]
            users_total.set(count)
        except Exception:
            db_errors_total.inc()
        time.sleep(5)

    cursor.close()
    connection.close()

def redis_set(key, value):
    try:
        redis_operations_total.inc()
        return r.set(key, value)
    except Exception:
        redis_errors_total.inc()
        raise

def redis_get(key):
    try:
        redis_operations_total.inc()
        return r.get(key)
    except Exception:
        redis_errors_total.inc()
        raise

def execute_query(query, params=None):
    start = time.time()
    try:
        _cursor_users.execute(
            query,
            params
        )
        db_queries_total.inc()
    except Exception:
        db_errors_total.inc()
        raise
    finally:
        db_query_duration.observe(
            time.time() - start
        )


def register (login, password, name):
    start = time.time()

    try:
        _cursor_users.execute("INSERT INTO users (login, password) VALUES (%s, %s);", (login, password))
        _cursor_users.execute("SELECT id FROM users WHERE login=%s", (login))
        id = _cursor_users.fetchall()[0][0]
        _cursor_users.execute("INSERT INTO personal VALUES (%d, %s, %s)", (id, "^"+login, name))
        _cursor_users.commit()
        users_login_total.inc()
    except Exception as error:
        db_errors_total.inc()
    finally:
        db_query_duration.observe(
            time.time() - start
        )

def enter (login, password):
    start = time.time()
    try:
        _cursor_users.execute("SELECT id FROM users WHERE login=%s AND password=%s", (login, password))
        id = (_cursor_users.fetchall())[0][0]
        key = f"{login}:{id}"        
        redis_set(key, id)
        return key
    except Exception as error:
        db_errors_total.inc()
        print(error)
    finally:
        db_query_duration.observe(
            time.time() - start
        )








def create_chat ():
    None
















print("started")


threading.Thread(
    target = run_metrics_server,
    daemon = True
).start()

threading.Thread(
    target = update_users_total,
    daemon = True
).start()




while 1:
    command = input("CMD> ")

    match command:

        case "new_user":
            _user = input("REG> ").split() # login password name
            register(_user[0], _user[1], _user[2])
            print("user had been create")

        case "enter":
            _ent = input("ENT> ").split() # login password
            print(enter(_ent[0], _ent[1]))

        case "sql":
            _command = input("SQL> ")
            execute_query(_command)
            _connect_users.commit()
            try:
                print(_cursor_users.fetchall())
            except psycopg2.ProgrammingError:
                print("Query executed")


        case "get":
            _log = input("GET> ")
            print(redis_get(_log))

        case "exit":
            break

        case _:
            pass

_cursor_users.close()
_connect_users.close()

_cursor_chats.close()
_connect_chats.close()

print("stoped")
