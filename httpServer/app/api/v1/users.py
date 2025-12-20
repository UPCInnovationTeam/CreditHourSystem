from fastapi import APIRouter, Depends, HTTPException, Body
from app.schemas.user import UserBase,UserCreate
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.crud import create_user, update_user
from app.dependencies.tools import verify_code
from app.dependencies.tools import send_verify_code
import logging
from app.core.config import identity_pwd

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
async def update_me(user: UserBase, current_user: UserBase = Depends(get_current_user), db = Depends(get_db)):
    """
    更新当前用户信息
    """
    user_patch = UserBase(**current_user.model_dump())
    if current_user.identity != "管理员":
        user_patch.name = user.name # 只允许改名
    else:
        user_patch = user   # 管理员可以修改所有信息
        user_patch.uid = current_user.uid # uid不做更改

    return await update_user(db, current_user.uid, user_patch)

@router.patch("/identity", response_model=UserBase)
async def update_identity(identity: str = Body(...),
                          password: str = Body(...),
                          current_user: UserBase = Depends(get_current_user),
                          db = Depends(get_db)):
    """
    更新当前用户身份
    """
    if password != identity_pwd:
        raise HTTPException(status_code=400, detail=f"密码错误")
    current_user.identity = identity
    return await update_user(db, current_user.uid, current_user)


