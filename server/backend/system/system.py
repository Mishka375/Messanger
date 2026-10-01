from libs import monitoring
from libs import errors
from libs import log
import database

import functools
import uuid
import time
import os
import uvicorn

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Response, Cookie
from pydantic import BaseModel, Field

import redis.asyncio as redis

import asyncio, json
from collections import defaultdict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

@asynccontextmanager
async def lifespan (app: FastAPI):
    monitoring.start_http_server(8000)

    for attempt in range(10):
        try:
            count = await database.count_users()
            monitoring.users_total.set(count)
            break
        except Exception:
            log.log.warning(f"init metrics attempt {attempt} failed, retrying")
            await asyncio.sleep(2)
    else:
        log.log.exception("init metrics failed")

    task = asyncio.create_task(listener())
    yield
    task.cancel()
    await database.users_engine.dispose()
    await database.chats_engine.dispose()

app = FastAPI(lifespan=lifespan)

rds = redis.Redis(
    host=os.environ["REDIS_HOST_SESSIONS"],
    port=int(os.environ["REDIS_PORT_SESSIONS"]),
    decode_responses=False
)

rooms: dict[str, set[WebSocket]] = defaultdict(set)

class Register_request (BaseModel):
    name: str = Field(min_length=1, max_length=50)
    login: str = Field(min_length=1, max_length=100)
    password: str

class Enter_request (BaseModel):
    login: str
    password: str

class New_chat_request (BaseModel):
    chat_name: str
    user_link: str

class Get_messeges (BaseModel):
    chat_id: int

class Send_messege (BaseModel):
    chat_id: int
    text: str


@app.post('/registry')
async def reg(body: Register_request):
    try:
        await register(body.login, body.password, body.name)

    except errors.IncorrectLogin:
        raise HTTPException(status_code=409, detail="Login is exist")
    
    except errors.SQLValueIsNull:
        raise HTTPException(status_code=400, detail="Enter values")
    
    except Exception as error:
        log.log.exception("reg failed")
        raise HTTPException(status_code=500, detail=str(error))

    return {"message": "User is registered"}

@app.post('/enter')
async def ent(body: Enter_request, response: Response):
    try:
        result = await enter(body.login, body.password)

        response.set_cookie(
            key="session_key",
            value=result["session_key"],
            max_age=3600,
            path="/api/",
            secure=False, #!!! Заменить при https
            httponly=True,
            samesite="lax"
        )

        response.set_cookie(
            key="name",
            value=result["user_name"],
            max_age=3600,
            path="/api/",
            secure=False, #!!! Заменить при https
            httponly=True,
            samesite="lax"
        )

    except errors.SQLValueIsNull:
        raise HTTPException(status_code=400, detail="Enter values")

    except errors.IncorrectLogin:
        raise HTTPException(status_code=401, detail="Uncorrect login or password")

    except errors.IncorrectKey:
        raise HTTPException(status_code=409, detail="Key is exist")
    
    except Exception as error:
        log.log.exception("reg failed")
        raise HTTPException(status_code=500, detail=str(error))
    
    return {"status": "ok"}

@app.post('/messeges')
async def mes(session_key: str = Cookie(...)):
    try:
        result = await get_chats(session_key)

    except errors.SQLValueIsNull:
        raise HTTPException(status_code=400, detail="Enter values")

    except errors.IncorrectLogin:
        raise HTTPException(status_code=401, detail="Uncorrect login or password")

    except errors.IncorrectKey:
        raise HTTPException(status_code=409, detail="Key is exist")
    
    except Exception as error:
        log.log.exception("reg failed")
        raise HTTPException(status_code=500, detail=str(error))
    
    return {"chats_data": result}

@app.post('/new_chat')
async def new_ch(body: New_chat_request, session_key: str = Cookie(...)):
    try:
        await new_chat(session_key, body.user_link, body.chat_name)

    except errors.SQLValueIsNull:
        raise HTTPException(status_code=400, detail="Enter values")

    except errors.IncorrectLogin:
        raise HTTPException(status_code=401, detail="Uncorrect login or password")

    except errors.IncorrectKey:
        raise HTTPException(status_code=409, detail="Key is exist")

    except Exception as error:
        log.log.exception("chat create failed")
        raise HTTPException(status_code=500, detail=str(error))
    
    return {"status": "ok"}

@app.post('/get_messeges')
async def get_msg(body: Get_messeges, session_key: str = Cookie(...)):
    try:
        res = await get_messeges(session_key, body.chat_id)

    except errors.SQLValueIsNull:
        raise HTTPException(status_code=400, detail="Enter values")

    except errors.IncorrectLogin:
        raise HTTPException(status_code=401, detail="Uncorrect login or password")

    except errors.IncorrectKey:
        raise HTTPException(status_code=409, detail="Key is exist")

    except errors.ChatError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except errors.RedisTimeoutError:
        raise HTTPException(status_code=503, detail="Redis unavailable")
    
    except Exception as error:
        log.log.exception("chat create failed")
        raise HTTPException(status_code=500, detail=str(error))
    return {"messeges": res}

@app.post('/send_messege')
async def send_msg(body: Send_messege, session_key: str = Cookie(...)):
    try:
        msg = await send_messege(session_key, body.chat_id, body.text)

        for uid in msg["participants"]:
            sess = await session_by_user(uid)
            if not sess:
                continue
            try:
                await push(sess, {
                                "type": "message",
                                "chat_id": body.chat_id,
                                "sender_id": msg["user_id"],
                                "date": msg["date"],
                                "text": body.text,
                                })
            except Exception as e:
                log.log.warning(f"push failed for user {uid}: {e}")
                

    except errors.SQLValueIsNull:
        raise HTTPException(status_code=400, detail="Enter values")

    except errors.IncorrectLogin:
        raise HTTPException(status_code=401, detail="Uncorrect login or password")

    except errors.IncorrectKey:
        raise HTTPException(status_code=409, detail="Key is exist")

    except errors.ChatError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except errors.RedisTimeoutError:
        raise HTTPException(status_code=503, detail="Redis unavailable")

    except Exception as error:
        log.log.exception("chat create failed")
        raise HTTPException(status_code=500, detail=str(error))

    return {"status": "ok"}


@app.get('/health')
async def health():
    return {"status": "ok"}


@app.middleware("http")
async def metrics(request: Request, call_next) -> None:
    monitoring.request_count.inc()
    monitoring.request_queue.inc()
    start = time.time()
    try:
        result = await call_next(request)

        if result.status_code >= 500:
            monitoring.request_errors.inc()
        return result

    except Exception:
        monitoring.request_errors.inc()
        raise

    finally:
        monitoring.request_time.observe(time.time() - start)
        monitoring.request_queue.dec()


def key_gen() -> str:
    return str(uuid.uuid4())


async def register(login: str, password: str, name: str) -> None:
    try:
        await database.registration(login, password, "^"+login, name)

        monitoring.users_total.inc()

        log.log.debug(f"User {name} is created")

    except errors.SQLValueExist as error:
        log.log.error(error)
        raise errors.IncorrectLogin("Login is exist")

    except errors.SQLValueIsNull as error:
        log.log.error(error)
        raise errors.IncorrectLogin("Login is null")

    except Exception as error:
        log.log.error(error)
        raise

async def enter (login: str, password: str) -> dict:
    try:
        data = await database.enter(login, password)

        id = data["id"]

        session_key = key_gen()

        if await check_session(session_key):
            log.log.warning ("Key is exist")
            raise errors.IncorrectKey("Key is exist")

        await database.redis_sessions_set(session_key, id)
        await database.redis_sessions_set(f"user_sessions:{id}", session_key)

        monitoring.users_online.inc()
        log.log.debug(f"User enter (key: {session_key});")

        return {"session_key":session_key, "chats_data":data["chats_data"], "user_name":data["user_name"]}

    except Exception as error:
        log.log.error(error)
        raise

async def out (key: str) -> None:
    try:
        user_id = await database.redis_sessions_get(key)
        if user_id is None:
            log.log.warning("Key is incorrect")
            raise errors.IncorrectKey("Key is incorrect")

        monitoring.users_online.dec()
        await database.redis_sessions_del(key)
        await database.redis_sessions_del(f"user_sessions:{user_id}")

    except Exception as error:
        log.log.error(error)
        raise

async def get_chats (key: str) -> list:
    try:
        return await database.get_chats(key)

    except Exception as error:
            log.log.error(error)
            raise

async def new_chat (key: str, user_link: str, name: str) -> None:
    try:
        if not await check_session(key):
            log.log.warning("Key is not exist")
            raise errors.IncorrectKey("Key is not exist")

        await database.new_chat(key, name, user_link)

    except Exception as error:
        log.log.error(error)
        raise

async def get_messeges (key: str, chat_id: int):
    try:
        if not await check_session(key):
            log.log.warning("Key is not exist")
            raise errors.IncorrectKey("Key is not exist")

        return await database.get_messeges(key, chat_id)

    except Exception as error:
        log.log.error(error)
        raise

async def send_messege (key: str, chat_id: int, text: str):
    try:
        if not await check_session(key):
            log.log.warning("Key is not exist")
            raise errors.IncorrectKey("Key is not exist")

        return await database.send_messege(key, chat_id, text)

    except Exception as error:
        log.log.error(error)
        raise


async def change_key (key: str) -> str:
    try:
        if not await check_session(key):
                log.log.warning("Key is not exist")
                raise errors.IncorrectKey("Key is not exist")

        new_key = key_gen()

        val = await database.redis_sessions_get(key)
        await database.redis_sessions_set(new_key, val)
        await database.redis_sessions_del(key)

        return new_key

    except Exception as error:
        log.log.error(error)
        raise

async def check_session(key: str) -> bool:
    if await database.redis_sessions_get(key) is not None:
        return True
    return False


async def send_local(key: str, data: dict):
    for ws in list(rooms[key]):
        try:
            await ws.send_json(data)
        except Exception as e:
            log.log.warning(f"WS send failed for {key}: {e}")
            rooms[key].discard(ws)

async def listener():
    ps = rds.pubsub()
    await ps.psubscribe("s:*")
    async for m in ps.listen():
        if m["type"] == "pmessage":
            await send_local(m["channel"].decode()[2:], json.loads(m["data"]))

async def push (key: str, data: dict):
    await rds.publish(f"s:{key}", json.dumps(data))

@app.websocket("/ws")
async def ws(ws: WebSocket, session_key: str | None = Cookie(None)):
    if not session_key:
        await ws.close(code=1008)
        return

    try:
        user_id = await database.redis_sessions_get(session_key)
    except errors.IncorrectKey:
        user_id = None

    if user_id is None:
        await ws.close(code=1008)
        return

    await ws.accept()
    rooms[session_key].add(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        rooms[session_key].discard(ws)

async def session_by_user(user_id: int) -> str | None:
    try:
        return await database.redis_sessions_get(f"user_sessions:{user_id}")
    except errors.IncorrectKey:
        return None

if __name__ == "__main__":
    uvicorn.run(
        "system:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        reload=True
    )