from libs import monitoring
from libs import errors
from libs import log

import functools
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

connect_chats = psycopg2.connect(
    dbname=os.environ["DATABASE_NAME_CHATS"],
    user=os.environ["DATABASE_USER"],
    password=os.environ["DATABASE_PASSWORD"],
    host=os.environ["DATABASE_HOST_CHATS"],
    port=int(os.environ["DATABASE_PORT"])
)


def redis_monitoring(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        monitoring.redis_request_count.inc()
        log.log.debug(f"function {func.__name__} called with args: <{args}>, kwargs: <{kwargs}>")

        try:
            res = func(*args, **kwargs)
            return res

        except Exception as error:
            monitoring.redis_errors_count.inc()
            log.log.error(f"Redis error: {error}")
            raise

    return wrapper

def sql_monitoring(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()

        log.log.debug(f"users command in {func.__name__}: args:<{args}>, kwargs:<{kwargs}>")

        monitoring.sql_request_count.inc()
        monitoring.sql_request_queue.inc()

        try:
            res = func(*args, **kwargs)
            return res

        except Exception as error:
            monitoring.sql_request_errors.inc()
            log.log.error(f"SQL error: {error}")
            raise

        finally:
            monitoring.sql_request_queue.dec()
            monitoring.sql_request_time.observe(time.time() - start)

    return wrapper


@redis_monitoring
def redis_sessions_set(key, value, ex = 3600) -> None:
    try:
        redis_sessions.set(key, value, ex = ex)
    except redis.DataError:
        raise errors.RedisDataError("Incorrect data")

    except redis.TimeoutError:
        raise errors.RedisTimeoutError("Time is out")

    except redis.BusyLoadingError:
        raise errors.RedisBusyError("Server is budy")

    except Exception:
        raise

@redis_monitoring
def redis_sessions_get(key):
    try:
        result = redis_sessions.get(key)

        return result
    
    except redis.DataError:
        raise errors.RedisDataError("Incorrect data")

    except redis.TimeoutError:
        raise errors.RedisTimeoutError("Time is out")

    except redis.BusyLoadingError:
        raise errors.RedisBusyError("Server is budy")

    except Exception:
        raise

@redis_monitoring
def redis_sessions_del(key) -> None:
    try:
        redis_sessions.delete(key)
    
    except redis.DataError:
        raise errors.RedisDataError("Incorrect data")

    except redis.TimeoutError:
        raise errors.RedisTimeoutError("Time is out")

    except redis.BusyLoadingError:
        raise errors.RedisBusyError("Server is budy")

    except Exception:
        raise


@sql_monitoring
def users_execute(command: str, params: None | tuple = None) -> list | None:
    try:
        cursor_users = connect_users.cursor()
        cursor_users.execute(command, params)
        connect_users.commit()

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
            raise errors.SQLValueExist("Unique value already exist")

        elif error.pgcode == "23502":
            connect_users.rollback()
            raise errors.SQLValueIsNull("Request value is null")

        else:
            connect_users.rollback()
            raise errors.SQLError(error.pgcode)

    except psycopg2.ProgrammingError:
        connect_users.rollback()
        raise errors.SQLRequestError("Request is incorrect")

    except psycopg2.DataError:
        connect_users.rollback()
        raise errors.SQLDataError("Incorrect data")

    except Exception:
        connect_users.rollback()
        raise

    finally:
        cursor_users.close()

@sql_monitoring
def chats_execute(command: str, params: None | tuple = None) -> list | None:  
    try:
        cursor_chats = connect_chats.cursor()
        cursor_chats.execute(command, params)
        connect_chats.commit()

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
            raise errors.SQLValueExist("Unique value already exist")

        elif error.pgcode == "23502":
            connect_chats.rollback()
            raise errors.SQLValueIsNull("Request value is null")

        else:
            connect_chats.rollback()
            raise errors.SQLError(error.pgcode)

    except psycopg2.ProgrammingError:
        connect_chats.rollback()
        raise errors.SQLRequestError("Request is incorrect")

    except psycopg2.DataError:
        connect_chats.rollback()
        raise errors.SQLDataError("Incorrect data")

    except Exception:
        connect_chats.rollback()
        raise

    finally:
        cursor_chats.close()