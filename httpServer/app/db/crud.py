from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.dbModels import User
from app.schemas.user import UserBase,UserCreate,UserLogin
from datetime import datetime
from app.dependencies.tools import hash_password
import logging
from app.models.dbModels import Activity
from app.schemas.activity import ActivityCreate, ActivityUpdate, ActivityBase

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

async def get_user(db: AsyncSession, uid: str) -> UserBase:
    """
    根据UID获取用户
    :param db: get_db()依赖注入
    :param uid: 用户的UID
    :return: 返回用户信息(Tuple)
    """
    result = await db.execute(select(User).where(User.uid == uid))  # type: ignore
    result = result.scalar_one_or_none()
    return result

async def login(db: AsyncSession, user: UserLogin) -> UserBase:
    return await get_user(db, user.uid)

async def set_credit(db: AsyncSession, uid: str, credit: dict) :
    user = await get_user(db, uid)
    user.creditHours = credit
    user_ = User(**user.model_dump())
    await db.commit()
    await db.refresh(user_)
    return {"message": "修改成功", "data": user.model_dump()["creditHours"]}

async def create_activity(db: AsyncSession, activity: ActivityCreate):
    """
    创建石光活动，并写入数据库
    :param db:
    :param activity: 活动信息
    :return:
    """
    last_activity = await get_last_activity(db)
    activity.uid = str(int(last_activity.uid) + 1) if last_activity else "1"
    db_activity = Activity(**activity.model_dump())
    db.add(db_activity)
    await db.commit()
    await db.refresh(db_activity)
    return {"id": db_activity.uid, "message": "创建成功"}

async def get_activity(db: AsyncSession, activity_id: str) -> ActivityBase:
    """
    根据活动id获取活动具体信息
    :param db:
    :param activity_id: 活动id
    :return: 活动信息
    """
    result = await db.execute(select(Activity).where(Activity.uid == activity_id))  # type: ignore
    result = result.scalar_one_or_none()
    return result

async def get_last_activity(db: AsyncSession) -> ActivityBase:
    """
    获取Activity表的最后一行数据（按uid排序）
    """
    result = await db.execute(
        select(Activity).order_by(Activity.uid.desc()).limit(1)
    )
    result = result.scalar_one_or_none()
    return result