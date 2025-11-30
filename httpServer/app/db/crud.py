from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.dbModels import User
from app.schemas.user import UserBase,UserCreate,UserLogin
from datetime import datetime
from app.dependencies.tools import hash_password
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

async def create_user(db: AsyncSession, user: UserCreate):
    # logger.info(f"密码：{user.password}")
    user.password = hash_password(user.password)
    # logger.info(f"哈希后的密码：{user.password}")
    user.identity = "使用者"
    user.registerTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user.tribeId = []
    user.activityId = []
    user.creditHours = {"mentalGrowth": 0, "innovation": 0, "culturalSports": 0, "socialPractice": 0, "skill": 0}

    del user.email
    del user.code
    db_user = User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return UserBase(**user.model_dump())

async def get_user(db: AsyncSession, uid: str):
    """
    根据UID获取用户
    :param db: get_db()依赖注入
    :param uid: 用户的UID
    :return: 返回用户信息(Tuple)
    """
    result = await db.execute(select(User).where(User.uid == uid))  # type: ignore
    result = result.scalar_one_or_none()
    return result

async def login(db: AsyncSession, user: UserLogin):
    return await get_user(db, user.uid)

async def set_credit(db: AsyncSession, uid: str, credit: dict):
    user = await get_user(db, uid)
    user.creditHours = credit
    await db.commit()
    await db.refresh(user)
    return user