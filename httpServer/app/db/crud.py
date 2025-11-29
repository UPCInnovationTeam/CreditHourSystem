from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.dbModels import User
from app.schemas.user import UserBase,UserCreate,UserLogin


async def create_user(db: AsyncSession, user: UserCreate):
    # TODO: 密码哈希
    user.identity = "使用者"
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