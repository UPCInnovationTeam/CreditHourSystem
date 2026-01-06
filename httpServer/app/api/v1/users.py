from fastapi import APIRouter, Depends, HTTPException, Body, Query
from app.schemas.user import UserBase,UserCreate
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.crud import create_user, update_user
from app.dependencies.tools import verify_code
from app.dependencies.tools import send_verify_code
import logging
from app.core.config import identity_pwd

from app.db.crud import get_user as get_user_by_uid , get_user_by_name, delete_user


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
#发送邮箱验证码
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

#根据输入uid还有name，输出用户的API
@router.get("/search", response_model=UserBase)
async def search_user(
        uid: str = None,
        name: str = None,
        current_user: UserBase = Depends(get_current_user),
        db=Depends(get_db)
):
    """
    根据uid或name查询用户信息
    :param uid: 用户ID，可选参数
    :param name: 用户姓名，可选参数
    :param current_user: 当前用户，用于权限验证
    :param db: 数据库会话
    :return: 匹配的用户信息
    """


    if not uid and not name:
        raise HTTPException(status_code=400, detail="必须提供uid或name参数")

    user = None
    if uid:
        user = await get_user_by_uid(db, uid)
    elif name:
        user = await get_user_by_name(db, name)

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return user

#根据输入uid删除指定用户信息（管理员权限）
@router.delete("/{uid}", response_model=dict)
async def delete_user_by_uid(
    uid: str,
    current_user: UserBase = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    删除指定用户信息（仅管理员可用）
    :param uid: 要删除的用户ID
    :param current_user: 当前用户，用于权限验证
    :param db: 数据库会话
    :return: 删除结果信息
    """
    # 验证权限 - 仅管理员可删除用户
    if current_user.identity != "管理员":
        raise HTTPException(status_code=403, detail="权限不足，仅管理员可删除用户")

    # 检查要删除的用户是否存在
    try:
        user_to_delete = await get_user_by_uid(db, uid)
        logger.info(f"准备删除用户: {user_to_delete.uid}")
    except ValueError:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 防止管理员删除自己
    if current_user.uid == uid:
        raise HTTPException(status_code=400, detail="不能删除自己的账户")

    # 执行删除操作
    await delete_user(db, uid)

    return {
        "success": True,
        "message": f"用户 {uid} 已成功删除"
    }






from app.schemas.user import PageResponse
from app.db.crud import get_page_users

@router.get("/pages", response_model=PageResponse)
async def get_users(page: int = Query(1, description="页数", ge=1),
                    page_size: int = Query(50, description="每页返回的数量", le=100),
                    db = Depends(get_db),
                    current_user: UserBase = Depends(get_current_user)):
    if current_user.identity != "管理员":
        raise HTTPException(status_code=400, detail=f"无权限")
    logger.info(f"{current_user.uid}获取用户列表: {page}, {page_size}")
    return await get_page_users(db, page, page_size)

