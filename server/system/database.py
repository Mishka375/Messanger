import psycopg2, redis, time, os
import monitoring


r = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    decode_responses=True
)

connect_users = psycopg2.connect(
    dbname=os.environ["DATABASE_NAME_USERS"],
    user=os.environ["DATABASE_USER"],
    password=os.environ["DATABASE_PASSWORD"],
    host=os.environ["DATABASE_HOST_USERS"],
    port=int(os.environ["DATABASE_PORT"])
)
cursor_users = connect_users.cursor()

connect_chats = psycopg2.connect(
    dbname=os.environ["DATABASE_NAME_CHATS"],
    user=os.environ["DATABASE_USER"],
    password=os.environ["DATABASE_PASSWORD"],
    host=os.environ["DATABASE_HOST_CHATS"],
    port=int(os.environ["DATABASE_PORT"])
)
cursor_chats = connect_chats.cursor()



def redis_set(key, value, ex=None):
    try:

        monitoring.redis_operations_count.inc()
        return r.set(key, value, ex=ex)
    except Exception:

        monitoring.redis_errors_count.inc()
        raise

def redis_get(key):
    try:

        monitoring.redis_operations_count.inc()
        return r.get(key)
    except Exception:

        monitoring.redis_errors_count.inc()
        raise

def redis_del(key):
    try:
        monitoring.redis_operations_count.inc()
        r.delete(key)
    except Exception:

        monitoring.redis_errors_count.inc()
        raise


def users_execute(command: str, params=None):
    start = time.time()

    monitoring.sql_request_queue.inc()
    
    try:
        cursor_users.execute(command, params)
        connect_users.commit()
        
    except Exception:
        connect_users.rollback()

        monitoring.sql_request_errors.labels(request=command[:50]).inc()
        raise
    finally:
        monitoring.sql_request_queue.dec()
        monitoring.sql_request_count.inc()
        monitoring.sql_request_time.observe(time.time() - start)
