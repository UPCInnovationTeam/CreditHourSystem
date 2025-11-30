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
    用户登录
    """
    user = await login_db(db, user_)    # 从数据库中获取用户信息
    if user is None or not verify_password(user_.password, user.password):
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    # 创建访问令牌
    access_token = create_access_token(data={"sub": user.uid})
    return {"access_token": access_token, "token_type": "bearer"}