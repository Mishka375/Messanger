from libs import monitoring
from libs import errors
from libs import log

import functools
from typing import Literal, TypedDict
import time
import os

import psycopg2
import redis

from sqlalchemy import URL
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey
from sqlalchemy.exc import IntegrityError, ProgrammingError, DataError

from sqlalchemy import insert, select, update, delete, text



url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.environ["DATABASE_USER"],
    password=os.environ["DATABASE_PASSWORD"],
    host=os.environ["DATABASE_HOST_USERS"],
    port=int(os.environ["DATABASE_PORT"]),
    database=os.environ["DATABASE_NAME_USERS"],
)
connect_users = create_engine(url, pool_size=5, max_overflow=10, echo=False)

url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.environ["DATABASE_USER"],
    password=os.environ["DATABASE_PASSWORD"],
    host=os.environ["DATABASE_HOST_CHATS"],
    port=int(os.environ["DATABASE_PORT"]),
    database=os.environ["DATABASE_NAME_CHATS"],
)
connect_chats = create_engine(url, pool_size=5, max_overflow=10, echo=False)


metadata = MetaData()


users = Table("users", metadata, autoload_with=connect_users)
personal = Table("personal", metadata, autoload_with=connect_users)

chats = Table("chats", metadata, autoload_with=connect_chats)
messeges = Table("messeges", metadata, autoload_with=connect_chats)



redis_sessions = redis.Redis(
    host=os.environ["REDIS_HOST_SESSIONS"],
    port=int(os.environ["REDIS_PORT_SESSIONS"]),
    decode_responses=True
)

# connect_users = psycopg2.connect(
#     dbname=os.environ["DATABASE_NAME_USERS"],
#     user=os.environ["DATABASE_USER"],
#     password=os.environ["DATABASE_PASSWORD"],
#     host=os.environ["DATABASE_HOST_USERS"],
#     port=int(os.environ["DATABASE_PORT"])
# )

# connect_chats = psycopg2.connect(
#     dbname=os.environ["DATABASE_NAME_CHATS"],
#     user=os.environ["DATABASE_USER"],
#     password=os.environ["DATABASE_PASSWORD"],
#     host=os.environ["DATABASE_HOST_CHATS"],
#     port=int(os.environ["DATABASE_PORT"])
# )


class Enter_request(TypedDict):
    id: str
    chats_data: list
    user_name: str


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
def redis_sessions_set(key, value, ex = 300) -> None:
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


def registration (login: str, password: str, identificator: str, name: str) -> None:
    try:
        with connect_users.begin() as conn:
            conn.execute (
                insert (users),
                [
                    {"login": login, "password":password}
                ],
            )

            id = conn.execute(select (users).where(users.c.login == login)).scalar()

            conn.execute (
                insert (personal),
                [
                    {"id":id, "identificator":identificator, "name":name}
                ],
            )

        return None

    except IntegrityError as error:
        pgcode = getattr(error.orig, "pgcode", None)

        if pgcode == "23505":
            raise errors.SQLValueExist("Unique value already exist")
        
        elif pgcode == "23502":
            raise errors.SQLValueIsNull("Request value is null")
        
        elif pgcode == "23503":
            raise errors.SQLForeignKeyError("Foreign key violation")
        
        elif pgcode == "23514":
            raise errors.SQLCheckError("Check constraint violation")
        
        else:
            raise errors.SQLError(pgcode)

def enter (login: str, password: str) -> dict[Enter_request]:
    try:
        with connect_users.connect() as conn:
            user_id = conn.execute(select(users.c.id).where((users.c.login==login)&(users.c.password==password))).scalar()

            if user_id is None:
                raise errors.IncorrectEnter("Incorrect login or password")

            name = conn.execute(select(personal.c.name).where(personal.c.id==user_id)).scalar()

        with connect_chats.connect() as conn:
            chats_data = conn.execute(select(chats.c.id, chats.c.name).where((chats.c.user_1==user_id) | (chats.c.user_2==user_id))).fetchall()

        return {"id":user_id, "chats_data":chats_data, "user_name":name}

    except IntegrityError as error:
        pgcode = getattr(error.orig, "pgcode", None)

        if pgcode == "23505":
            raise errors.SQLValueExist("Unique value already exist")

        elif pgcode == "23502":
            raise errors.SQLValueIsNull("Request value is null")

        elif pgcode == "23503":
            raise errors.SQLForeignKeyError("Foreign key violation")

        elif pgcode == "23514":
            raise errors.SQLCheckError("Check constraint violation")

        else:
            raise errors.SQLError(pgcode)