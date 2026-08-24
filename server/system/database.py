import psycopg2, redis, time, os
import monitoring
from libs import log


redis_sessions = redis.Redis(
    host=os.environ["REDIS_HOST_SESSIONS"],
    port=int(os.environ["REDIS_PORT_SESSIONS"]),
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



def redis_sessions_set(key, value, ex=3600):
    try:
        monitoring.redis_operations_count.inc()
        log.log.debug(f"Redis key <{key}:{value}> was created on <{ex}> time")
        return redis_sessions.set(key, value, ex=ex)
    except Exception as error:
        log.log.error(error)
        monitoring.redis_errors_count.inc()
        return 0
        raise


def redis_sessions_get(key):
    try:
        log.log.debug(f"value from key <{key}> is geted")
        monitoring.redis_operations_count.inc()
        return redis_sessions.get(key)
    except Exception as error:
        log.log.error(error)
        monitoring.redis_errors_count.inc()
        return 0
        raise

def redis_sessions_del(key):
    try:
        log.log.debug(f"key <{key}> is deleted")
        monitoring.redis_operations_count.inc()
        redis_sessions.delete(key)
        return 1
    except Exception as error:
        log.log.error(error)
        monitoring.redis_errors_count.inc()
        return 0
        raise



def users_execute(command: str, params=None):
    start = time.time()

    monitoring.sql_request_queue.inc()

    try:
        cursor_users.execute(command, params)
        connect_users.commit()
        log.log.debug(f"users command <{command}>:<{params}>")
        return 1
    except Exception as error:
        connect_users.rollback()
        log.log.error(error)
        monitoring.sql_request_errors.inc()
        return 0
        raise
    finally:
        monitoring.sql_request_queue.dec()
        monitoring.sql_request_count.inc()
        monitoring.sql_request_time.observe(time.time() - start)

def chats_execute(command: str, params=None):
    start = time.time()

    monitoring.sql_request_queue.inc()
    
    try:
        cursor_chats.execute(command, params)
        connect_chats.commit()
        log.log.debug(f"chats command <{command}>:<{params}>")
        return 1
    except Exception as error:
        connect_chats.rollback()
        log.log.error(error)
        monitoring.sql_request_errors.inc()
        return 0
        raise
    finally:
        monitoring.sql_request_queue.dec()
        monitoring.sql_request_count.inc()
        monitoring.sql_request_time.observe(time.time() - start)
