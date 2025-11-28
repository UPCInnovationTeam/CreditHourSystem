from fastapi import APIRouter, Depends
from app.schemas.user import UserBase,UserCreate
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.crud import create_user

router = APIRouter(prefix="/user", tags=["用户管理"])

@router.get("/me", response_model=UserBase)
async def get_me(current_user: UserBase = Depends(get_current_user)):
    """
    获取当前用户信息
    """
    return current_user

@router.post("/register", response_model=UserCreate)
async def register(user: UserCreate, db = Depends(get_db)):
    """
    用户注册
    """
    return await create_user(db, user)

@router.patch("/me", response_model=UserBase)
async def update_me(user: UserBase, current_user: UserBase = Depends(get_current_user)):
    """
    更新当前用户信息
    """
    # TODO: 更新当前用户信息
    return None


