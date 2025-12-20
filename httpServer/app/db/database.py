from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_session, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import SQLALCHEMY_DATABASE_URL

# 创建数据库引擎
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,#数据库链接地址
    pool_size=10,       # 连接池大小，控制同时活跃的连接数
    max_overflow=20,    # 最大溢出连接数
    pool_pre_ping= True, # 检测连接是否可用
)

# 创建数据库会话
SessionLocal = async_sessionmaker(
    autocommit=False,#是否自动提交事务
    autoflush=False,#是否自动刷新
    bind=engine,#绑定到前面创建的引擎
    class_=AsyncSession
)

# 创建ORM
Base = declarative_base()

# 获取数据库会话
async def get_db():
    """
    获取数据库会话的异步生成函数
    使用方法：在路由函数中通过依赖注入获取db会话
    """
    async with SessionLocal() as db:
        yield db