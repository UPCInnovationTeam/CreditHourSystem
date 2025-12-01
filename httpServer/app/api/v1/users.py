from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserBase,UserCreate
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.crud import create_user
from app.dependencies.tools import verify_code
from app.dependencies.tools import send_verify_code
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter(prefix="/user", tags=["用户管理"])

@router.get("/me", response_model=UserBase)
async def get_me(current_user: UserBase = Depends(get_current_user)):
    """
    获取当前用户信息
    """
    return current_user

@router.post("/register", response_model=UserBase)
async def register(user: UserCreate, db = Depends(get_db)):
    """
    用户注册
    """
    logger.info(f"用户注册: {user.activityId}")
    if not verify_code(user.email, user.code):
        raise HTTPException(status_code=400, detail=f"验证码错误")
    return await create_user(db, user)

@router.get("/verify_code")
async def get_verify_code(email: str):
    await send_verify_code(email)
    return {"status": "success"}

@router.patch("/me", response_model=UserBase)
async def update_me(user: UserBase, current_user: UserBase = Depends(get_current_user)):
    """
    更新当前用户信息
    """
    # TODO: 更新当前用户信息
    return None


