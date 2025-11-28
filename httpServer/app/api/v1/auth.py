from fastapi import APIRouter, HTTPException, Depends
from app.core.security import create_access_token
from app.schemas.user import UserLogin

from app.db.database import get_db
from app.db.crud import login as login_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["认证管理"])

@router.post("/login")
async def login(user_: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    用户登录
    """
    # TODO: 连接数据库，验证用户信息
    user = await login_db(db, user_)
    if user is None:
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    # 创建访问令牌
    access_token = create_access_token(data={"sub": user.uid})
    return {"access_token": access_token, "token_type": "bearer"}