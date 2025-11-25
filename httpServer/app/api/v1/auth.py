from fastapi import APIRouter, HTTPException, Depends
from app.core.security import create_access_token
from app.schemas.user import UserLogin

router = APIRouter(prefix="/auth", tags=["认证管理"])

@router.post("/login")
async def login(user: UserLogin):
    """
    用户登录
    """
    # TODO: 连接数据库，验证用户信息

    # 创建访问令牌
    access_token = create_access_token(data={"sub": user.uid})
    return {"access_token": access_token, "token_type": "bearer"}