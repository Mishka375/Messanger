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

@asynccontextmanager
async def lifespan (app: FastAPI):
    monitoring.start_http_server(8000)

    for attempt in range(10):
        try:
            count = database.users_execute("SELECT COUNT(*) FROM users;")
            monitoring.users_total.set(int(count[0][0]))
            break

        except Exception:
            log.log.warning(f"init metrics attempt {attempt} failed, retrying")
            time.sleep(2)
    else:
        log.log.exception("init metrics failed")

    yield
app = FastAPI(lifespan=lifespan)


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
def reg(body: Register_request):
    try:
        register(body.login, body.password, body.name)

    except errors.IncorrectLogin:
        raise HTTPException(status_code=409, detail="Login is exist")
    
    except errors.SQLValueIsNull:
        raise HTTPException(status_code=400, detail="Enter values")
    
    except Exception as error:
        log.log.exception("reg failed")
        raise HTTPException(status_code=500, detail=str(error))

    return {"message": "User is registered"}

@app.post('/enter')
def ent(body: Enter_request, response: Response):
    try:
        result = enter(body.login, body.password)

        response.set_cookie(
            key="session_key",
            value=result["session_key"],
            max_age=3600,
            path="/",
            secure=False, #!!! Заменить при https
            httponly=True,
            samesite="lax"
        )

        response.set_cookie(
            key="name",
            value=result["user_name"],
            max_age=3600,
            path="/",
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
def mes(session_key: str = Cookie(...)):
    try:
        result = get_chats(session_key)

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
def new_ch(body: New_chat_request, session_key: str = Cookie(...)):
    try:
        new_chat(session_key, body.user_link, body.chat_name)

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
def get_msg(body: Get_messeges, session_key: str = Cookie(...)):
    try:
        res = get_messeges(session_key, body.chat_id)

    except errors.SQLValueIsNull:
        raise HTTPException(status_code=400, detail="Enter values")

    except errors.IncorrectLogin:
        raise HTTPException(status_code=401, detail="Uncorrect login or password")

    except errors.IncorrectKey:
        raise HTTPException(status_code=409, detail="Key is exist")

    except Exception as error:
        log.log.exception("chat create failed")
        raise HTTPException(status_code=500, detail=str(error))
    
    return {"messeges": res}

@app.post('/send_messege')
def send_msg(body: Send_messege, session_key: str = Cookie(...)):
    try:
        send_messege(session_key, body.chat_id, body.text)

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


@app.get('/health')
def health():
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


def register(login: str, password: str, name: str) -> None:
    try:
        database.registration(login, password, "^"+login, name)

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

def enter (login: str, password: str) -> dict:
    try:
        data = database.enter(login, password)

        id = data["id"]

        session_key = key_gen()

        if check_session(session_key):
            log.log.warning ("Key is exist")
            raise errors.IncorrectKey("Key is exist")

        database.redis_sessions_set(session_key, id)

        monitoring.users_online.inc()
        log.log.debug(f"User enter (key: {session_key});")

        return {"session_key":session_key, "chats_data":data["chats_data"], "user_name":data["user_name"]}

    except Exception as error:
        log.log.error(error)
        raise

def out (key: str) -> None:
    try:      
        if not check_session(key):
            log.log.warning("Key is incorrect")
            raise errors.IncorrectKey("Key is incorrect")
        
        monitoring.users_online.dec()
        database.redis_sessions_del(key)
            
    except Exception as error:
        log.log.error(error)
        raise

def get_chats (key: str) -> list:
    try:
        return database.get_chats(key)

    except Exception as error:
            log.log.error(error)
            raise

def new_chat (key: str, user_link: str, name: str) -> None:
    try:
        if not check_session(key):
            log.log.warning("Key is not exist")
            raise errors.IncorrectKey("Key is not exist")

        database.new_chat(key, name, user_link)

    except Exception as error:
        log.log.error(error)
        raise

def messege (key: str, chat_id: int, messege: str) -> None:
    try:
        if not check_session(key):
            log.log.warning("Key is not exist")
            raise errors.IncorrectKey("Key is not exist")
        
        sender_id = int(database.redis_sessions_get(key))

        sender_name = database.users_execute("SELECT name FROM personal WHERE id=%s", (sender_id,))

        if sender_name is None:
            log.log.warning("User is not exist")
            raise errors.IncorrectEnter("User is not exist")

        sender_name = sender_name[0][0]

        log.log.debug(f"User <{sender_id}:{sender_name}> send <{messege}>")

        database.chats_execute("INSERT INTO messeges (user_id, chat_id, text) VALUES (%s, %s, %s);", (sender_id, chat_id, message))

        log.log.debug(f"Messege {messege} was sended")
        monitoring.messeges_count.inc()
    
    except Exception as error:
        log.log.error(error)
        raise

def get_messeges (key: str, chat_id: int):
    try:
        if not check_session(key):
            log.log.warning("Key is not exist")
            raise errors.IncorrectKey("Key is not exist")

        return database.get_messeges(key, chat_id)

    except Exception as error:
        log.log.error(error)
        raise

def send_messege (key: str, chat_id: int, text: str):
    try:
        if not check_session(key):
            log.log.warning("Key is not exist")
            raise errors.IncorrectKey("Key is not exist")

        return database.send_messege(key, chat_id, text)

    except Exception as error:
        log.log.error(error)
        raise


def change_key (key: str) -> str:
    try:
        if not check_session(key):
                log.log.warning("Key is not exist")
                raise errors.IncorrectKey("Key is not exist")

        new_key = key_gen()

        database.redis_sessions_set(new_key, database.redis_sessions_get(key))
        database.redis_sessions_del(key)

        return new_key

    except Exception as error:
        log.log.error(error)
        raise

def check_session(key: str) -> bool:
    if database.redis_sessions_get(key) is not None:
        return True
    return False





if __name__ == "__main__":
    uvicorn.run(
        "system:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        reload=True
    )