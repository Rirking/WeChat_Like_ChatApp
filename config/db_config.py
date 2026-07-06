from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

ASYNC_MYSQL_DATABASE_URL = "mysql+aiomysql://root:your_password@localhost:3306/your_create_table?charset=utf8mb4"

# 创建异步引擎
async_engine = create_async_engine(
    ASYNC_MYSQL_DATABASE_URL,
    pool_size=20,
    echo=True,
    max_overflow=20
)

# 创建异步会话工厂
AsyncSessionMaker = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,        # 产出的会话类型是异步会话
    expire_on_commit=False
)

# 获取数据库会话

async def get_db():
    async with AsyncSessionMaker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

