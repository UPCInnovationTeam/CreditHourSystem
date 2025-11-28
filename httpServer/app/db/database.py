from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_session, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import SQLALCHEMY_DATABASE_URL

# 创建数据库引擎
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,       # 连接池大小
    max_overflow=20,    # 最大溢出连接数
    pool_pre_ping= True, # 检测连接是否可用
)

# 创建数据库会话
SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

# 创建ORM
Base = declarative_base()

# 获取数据库会话
async def get_db():
    async with SessionLocal() as db:
        yield db