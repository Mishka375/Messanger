from libs import monitoring
from libs import errors
from libs import log

import functools
from typing import Literal, TypedDict
import time
import os

import redis.asyncio as redis

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from sqlalchemy import URL
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey
from sqlalchemy.exc import IntegrityError, ProgrammingError, DataError

from sqlalchemy import insert, select, update, delete, text

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=1,
    hash_len=32,
    salt_len=16
)


url_users = URL.create(
    drivername="postgresql+asyncpg",
    username=os.environ["DATABASE_USER"],
    password=os.environ["DATABASE_PASSWORD"],
    host=os.environ["DATABASE_HOST_USERS"],
    port=int(os.environ["DATABASE_PORT"]),
    database=os.environ["DATABASE_NAME_USERS"],
)
engine_users = create_async_engine(
    url_users,
    echo=os.getenv("SQL_ECHO", "0") == "1",
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
)
connect_users = async_sessionmaker(
    bind=engine_users,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,
)


url_chats = URL.create(
    drivername="postgresql+asyncpg",
    username=os.environ["DATABASE_USER"],
    password=os.environ["DATABASE_PASSWORD"],
    host=os.environ["DATABASE_HOST_CHATS"],
    port=int(os.environ["DATABASE_PORT"]),
    database=os.environ["DATABASE_NAME_CHATS"],
)
engine_chats = create_async_engine(
    url_chats,
    echo=os.getenv("SQL_ECHO", "0") == "1",
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
)
connect_chats = async_sessionmaker(
    bind=engine_chats,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,
)

metadata = MetaData()

_ref_users = create_engine(URL.create(
    drivername="postgresql+psycopg2",
    username=os.environ["DATABASE_USER"],
    password=os.environ["DATABASE_PASSWORD"],
    host=os.environ["DATABASE_HOST_USERS"],
    port=int(os.environ["DATABASE_PORT"]),
    database=os.environ["DATABASE_NAME_USERS"],
))
users    = Table("users",    metadata, autoload_with=_ref_users)
personal = Table("personal", metadata, autoload_with=_ref_users)
_ref_users.dispose()

_ref_chats = create_engine(URL.create(
    drivername="postgresql+psycopg2",
    username=os.environ["DATABASE_USER"],
    password=os.environ["DATABASE_PASSWORD"],
    host=os.environ["DATABASE_HOST_CHATS"],
    port=int(os.environ["DATABASE_PORT"]),
    database=os.environ["DATABASE_NAME_CHATS"],
))
chats    = Table("chats",    metadata, autoload_with=_ref_chats)
messeges = Table("messeges", metadata, autoload_with=_ref_chats)
_ref_chats.dispose()


redis_sessions = redis.Redis(
    host=os.environ["REDIS_HOST_SESSIONS"],
    port=int(os.environ["REDIS_PORT_SESSIONS"]),
    decode_responses=True
)


class Enter_request(TypedDict):
    id: str
    chats_data: list
    user_name: str


def redis_monitoring(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        monitoring.redis_request_count.inc()
        log.log.debug(f"function {func.__name__} called with args: <{args}>, kwargs: <{kwargs}>")

        try:
            res = await func(*args, **kwargs)
            return res

        except Exception as error:
            monitoring.redis_errors_count.inc()
            log.log.error(f"Redis error: {error}")
            raise

    return wrapper

def sql_monitoring(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()

        log.log.debug(f"users command in {func.__name__}: args:<{args}>, kwargs:<{kwargs}>")

        monitoring.sql_request_count.inc()
        monitoring.sql_request_queue.inc()

        try:
            res = await func(*args, **kwargs)
            return res

        except Exception as error:
            monitoring.sql_request_errors.inc()
            log.log.error(f"SQL error: {error}")
            raise

        finally:
            monitoring.sql_request_queue.dec()
            monitoring.sql_request_time.observe(time.time() - start)

    return wrapper

def _raise_pg(error: IntegrityError) -> None:
    o = error.orig
    code = getattr(o, "pgcode", None) or getattr(o, "sqlstate", None)
    exc = {
        "23505": errors.SQLValueExist,
        "23502": errors.SQLValueIsNull,
        "23503": errors.SQLForeignKeyError,
        "23514": errors.SQLCheckError,
    }.get(code, errors.SQLError)
    raise exc(f"pgcode={code}")

@redis_monitoring
async def redis_sessions_set(key, value, ex = 3600) -> None:
    try:
        await redis_sessions.set(key, value, ex = ex)
    except redis.DataError:
        raise errors.RedisDataError("Incorrect data")

    except redis.TimeoutError:
        raise errors.RedisTimeoutError("Time is out")

    except redis.BusyLoadingError:
        raise errors.RedisBusyError("Server is budy")

    except Exception:
        raise

@redis_monitoring
async def redis_sessions_get(key):
    try:
        result = await redis_sessions.get(key)

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
async def redis_sessions_del(key) -> None:
    try:
        await redis_sessions.delete(key)

    except redis.DataError:
        raise errors.RedisDataError("Incorrect data")

    except redis.TimeoutError:
        raise errors.RedisTimeoutError("Time is out")

    except redis.BusyLoadingError:
        raise errors.RedisBusyError("Server is budy")

    except Exception:
        raise


@sql_monitoring
async def count_users() -> int:
    async with connect_users() as conn:
        result = await conn.execute(text("SELECT COUNT(*) FROM users"))
        return int(result.scalar() or 0)


@sql_monitoring
async def registration (login: str, password: str, identificator: str, name: str) -> None:
    try:
        async with connect_users.begin() as conn:
            await conn.execute (
                insert (users),
                [{
                    "login": login,
                    "password":ph.hash(password)
                }],
            )

            result = await conn.execute(select (users).where(users.c.login == login))
            id = result.scalar()

            await conn.execute (
                insert (personal),
                [{
                    "id":id,
                    "identificator":identificator,
                    "name":name
                }],
            )

        return None

    except IntegrityError as error:
        _raise_pg(error)

@sql_monitoring
async def enter(login: str, password: str) -> dict[Enter_request]:
    try:
        async with connect_users() as conn:
            result = await conn.execute(
                select(users.c.id, users.c.password, personal.c.name)
                .join(personal, personal.c.id == users.c.id)
                .where(users.c.login == login)
            )
            row = result.fetchone()

        if row is None:
            raise errors.IncorrectEnter("Incorrect login")

        user_id, password_hash, name = row
        ph.verify(password_hash, password)

        async with connect_chats() as conn:
            result = await conn.execute(
                select(chats.c.id, chats.c.name)
                .where((chats.c.user_1 == user_id) | (chats.c.user_2 == user_id))
            )
            chats_data = [[r[0], r[1]] for r in result.fetchall()]

        return {"id": user_id, "chats_data": chats_data, "user_name": name}

    except IntegrityError as error:
        _raise_pg(error)
    except VerifyMismatchError:
        raise errors.IncorrectEnter("Password is incorrect")

@sql_monitoring
async def new_chat (key: str, name: str, user_link: str) -> None:
    try:
        id_1 = await redis_sessions_get(key)
        if id_1 is None:
            raise errors.IncorrectKey("Session expired")
        id_1 = int(id_1)

        async with connect_users() as conn:
            result = await conn.execute(select(personal.c.id).where(personal.c.identificator==user_link))
            id_2 = result.fetchall()[0][0]

        id_2 = int(id_2)

        async with connect_chats.begin() as conn:
            if id_1 != id_2:
                await conn.execute(
                    insert(chats),
                    [{
                        "name":name,
                        "user_1":id_1,
                        "user_2":id_2
                    }],
                )

                log.log.debug(f"Chat {name} was created")

            else:
                log.log.warning(f"Chat {name} wasn't created, same id")
                raise errors.ChatError("One user in chat")

    except IndexError:
        raise errors.IncorrectEnter("Incorrect link")

    except IntegrityError as error:
        _raise_pg(error)

@sql_monitoring
async def get_chats (key: str) -> list:
    try:
        user_id = int(await redis_sessions_get(key))

        async with connect_chats() as conn:
            result = await conn.execute(select(chats.c.id, chats.c.name).where((chats.c.user_1==user_id) | (chats.c.user_2==user_id)))
            chats_data = result.fetchall()

        return [[row[0], row[1]] for row in chats_data]

    except IndexError:
        raise errors.IncorrectEnter("Incorrect login")

    except IntegrityError as error:
        _raise_pg(error)

@sql_monitoring
async def get_messeges (key: str, chat_id: int) -> list:
    try:
        user_id = int(await redis_sessions_get(key))

        async with connect_chats() as conn:
            result = await conn.execute(select(messeges.c.user_id, messeges.c.date, messeges.c.text).where(messeges.c.chat_id==chat_id).order_by(messeges.c.date))
            res = result.fetchall()

            result = await conn.execute(select(chats.c.user_1, chats.c.user_2).where(chats.c.id==chat_id))
            users_id = result.fetchall()[0]

        async with connect_users() as conn:
            user_2_id = users_id[0] if users_id[0] != user_id else users_id[1]
            result = await conn.execute(select(personal.c.name).where(personal.c.id == user_2_id))
            other_name = result.scalar() or "Unknown"

            res = [[("" if row[0]==user_id else other_name), row[1], row[2]] for row in res]

        return res

    except IndexError:
        raise errors.IncorrectEnter("Incorrect chat id")

    except IntegrityError as error:
        _raise_pg(error)

@sql_monitoring
async def send_messege(key: str, chat_id: int, text: str):
    raw = await redis_sessions_get(key)
    if raw is None:
        raise errors.IncorrectKey("Session expired")
    user_id = int(raw)

    async with connect_chats.begin() as conn:
        result = await conn.execute(
            select(chats.c.user_1, chats.c.user_2).where(chats.c.id == chat_id)
        )
        users = result.fetchone()

        if users is None:
            raise errors.ChatError("Chat is not found")


        result = await conn.execute(
            insert(messeges).returning(
                messeges.c.date
            ),
            [{"user_id": user_id, "chat_id": chat_id, "text": text}],
        )

        row = result.fetchone()

        async with connect_users() as conn:
            result = await conn.execute(
                select(personal.c.name).where(personal.c.id==user_id)
            )

            user_name = result.fetchone()
            user_name = user_name[0] if user_name else ''

    return {"date": row.date.isoformat(), "user_name": user_name, "participants": list(users)}
