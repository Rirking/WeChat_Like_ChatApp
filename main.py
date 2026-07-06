from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.db_config import async_engine
from models.users import Base


from models import users, friends, friends_request, messages

from router import users, friends, messages, friends_request, ai_analys


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:    # 连接绑定的数据库

        # create_all会将所有注册过Base表里的所有表定义翻译成 CREATE TABLE...SQL语句，
        # 但是这是同步操作，可是这整个确实个异步操作，所以需要run_sync(),把同步包装成异步
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_engine.dispose()
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def root():
    return {"message": "Rirking"}

app.include_router(users.router)

app.include_router(friends.router)

app.include_router(messages.router)

app.include_router(friends_request.router)

app.include_router(ai_analys.router)
