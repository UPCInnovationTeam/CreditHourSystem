from fastapi import APIRouter, HTTPException, Depends
from app.core.security import create_access_token
from app.schemas.user import UserLogin

from app.db.database import get_db
from app.db.crud import login as login_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.tools import hash_password, verify_password


router = APIRouter(prefix="/auth", tags=["认证管理"])

@router.post("/login")
async def login(user_: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    处理用户登录请求，验证用户凭据并返回访问令牌

    :param user_: UserLogin模型，包含用户登录信息（uid和password）
    :param db: 数据库会话，通过依赖注入获取
    :return: 包含访问令牌和令牌类型的字典
    """
     # 从数据库中获取用户信息进行验证
    user = await login_db(db, user_)    # 从数据库中获取用户信息
    # 验证用户是否存在且密码正确
    if user is None or not verify_password(user_.password, user.password):
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    # 创建访问令牌
    access_token = create_access_token(data={"sub": user.uid})
    # 返回令牌信息
    return {"access_token": access_token, "token_type": "bearer"}