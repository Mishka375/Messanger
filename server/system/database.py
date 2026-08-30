from libs import monitoring
from libs import errors
from libs import log

import psycopg2
import redis
import time
import os


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
        redis_sessions.set(key, value, ex=ex)
    
    except redis.DataError:
        log.log.error("Data error")
        monitoring.redis_errors_count.inc()
        raise errors.RedisDataError("Incorrect data")

    except redis.TimeoutError:
        log.log.error("Timeout error")
        monitoring.redis_errors_count.inc()
        raise errors.RedisTimeoutError("Time is out")

    except redis.BusyLoadingError:
        log.log.error("Server is busy")
        monitoring.redis_errors_count.inc()
        raise errors.RedisBusyError("Server is budy")

    except Exception as error:
        log.log.error(error)
        monitoring.redis_errors_count.inc()
        raise error

def redis_sessions_get(key):
    try:
        log.log.debug(f"value from key <{key}> is geted")
        monitoring.redis_operations_count.inc()
        result = redis_sessions.get(key)

        return result
    
    except redis.DataError:
        log.log.error("Data error")
        monitoring.redis_errors_count.inc()
        raise errors.RedisDataError("Incorrect data")

    except redis.TimeoutError:
        log.log.error("Timeout error")
        monitoring.redis_errors_count.inc()
        raise errors.RedisTimeoutError("Time is out")

    except redis.BusyLoadingError:
        log.log.error("Server is busy")
        monitoring.redis_errors_count.inc()
        raise errors.RedisBusyError("Server is budy")

    except Exception as error:
        log.log.error(error)
        monitoring.redis_errors_count.inc()
        raise error

def redis_sessions_del(key):
    try:
        log.log.debug(f"key <{key}> is deleted")
        monitoring.redis_operations_count.inc()
        redis_sessions.delete(key)
    
    except redis.DataError:
        log.log.error("Data error")
        monitoring.redis_errors_count.inc()
        raise errors.RedisDataError("Incorrect data")

    except redis.TimeoutError:
        log.log.error("Timeout error")
        monitoring.redis_errors_count.inc()
        raise errors.RedisTimeoutError("Time is out")

    except redis.BusyLoadingError:
        log.log.error("Server is busy")
        monitoring.redis_errors_count.inc()
        raise errors.RedisBusyError("Server is budy")

    except Exception as error:
        log.log.error(error)
        monitoring.redis_errors_count.inc()
        raise error



def users_execute(command: str, params=None) -> list | None:
    start = time.time()

    monitoring.sql_request_queue.inc()

    try:
        cursor_users.execute(command, params)
        connect_users.commit()
        log.log.debug(f"users command <{command}>:<{params}>")

        try:
            res = cursor_users.fetchall()

            if res == []:
                return None
            return res

        except psycopg2.ProgrammingError:
            return None
        
        except Exception:
            raise
    
    except psycopg2.IntegrityError as error:
        if error.pgcode == "23505":
            connect_users.rollback()
            log.log.error("Value is exist")
            monitoring.sql_request_errors.inc()
            raise errors.SQLValueExist("Unique value already exist")

        elif error.pgcode == "23502":
            connect_users.rollback()
            log.log.error("Is Null")
            monitoring.sql_request_errors.inc()
            raise errors.SQLValueIsNull("Request value is null")

        else:
            connect_users.rollback()
            log.log.error(str(error.pgcode))
            monitoring.sql_request_errors.inc()
            raise errors.SQLError(error.pgcode)

    except psycopg2.ProgrammingError:
        connect_users.rollback()
        log.log.error("Request error")
        monitoring.sql_request_errors.inc()
        raise errors.SQLRequestError("Request is incorrect")

    except psycopg2.DataError:
        connect_users.rollback()
        log.log.error("Data error")
        monitoring.sql_request_errors.inc()
        raise errors.SQLDataError("Incorrect data")

    except Exception as error:
        connect_users.rollback()
        log.log.error(error)
        monitoring.sql_request_errors.inc()
        raise error

    finally:
        monitoring.sql_request_queue.dec()
        monitoring.sql_request_count.inc()
        monitoring.sql_request_time.observe(time.time() - start)

def chats_execute(command: str, params=None) -> list | None:
    start = time.time()

    monitoring.sql_request_queue.inc()
    
    try:
        cursor_chats.execute(command, params)
        connect_chats.commit()
        log.log.debug(f"chats command <{command}>:<{params}>")

        try:
            res = cursor_chats.fetchall()

            if res == []:
                return None
            return res

        except psycopg2.ProgrammingError:
            return None
        
        except Exception:
            raise
    
    except psycopg2.IntegrityError as error:
        if error.pgcode == "23505":
            connect_chats.rollback()
            log.log.error("Value is exist")
            monitoring.sql_request_errors.inc()
            raise errors.SQLValueExist("Unique value already exist")

        elif error.pgcode == "23502":
            connect_chats.rollback()
            log.log.error("Is Null")
            monitoring.sql_request_errors.inc()
            raise errors.SQLValueIsNull("Request value is null")

        else:
            connect_chats.rollback()
            log.log.error(str(error.pgcode))
            monitoring.sql_request_errors.inc()
            raise errors.SQLError(error.pgcode)

    except psycopg2.ProgrammingError:
        connect_chats.rollback()
        log.log.error("Request error")
        monitoring.sql_request_errors.inc()
        raise errors.SQLRequestError("Request is incorrect")

    except psycopg2.DataError:
        connect_chats.rollback()
        log.log.error("Data error")
        monitoring.sql_request_errors.inc()
        raise errors.SQLDataError("Incorrect data")

    except Exception as error:
        connect_chats.rollback()
        log.log.error(error)
        monitoring.sql_request_errors.inc()
        raise error

    finally:
        monitoring.sql_request_queue.dec()
        monitoring.sql_request_count.inc()
        monitoring.sql_request_time.observe(time.time() - start)
