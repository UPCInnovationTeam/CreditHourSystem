from fastapi import APIRouter, Depends
from app.schemas.user import UserBase,UserCreate
from app.core.security import get_current_user

router = APIRouter(prefix="/user", tags=["用户管理"])

@router.get("/me", response_model=UserBase)
async def get_me(current_user: UserBase = Depends(get_current_user)):
    """
    获取当前用户信息
    """
    return current_user

@router.post("/register", response_model=UserCreate)
async def register(user: UserCreate):
    """
    用户注册
    """
    return None # TODO: 用户注册


