from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user
from app.schemas.activity import ActivityBase, ActivityCreate
from app.db.database import get_db
from app.schemas.user import UserBase
from app.db.crud import (get_activity as get_activity_by_id, \
                         create_activity as create_activity_, get_20_activities_ids, join_activity_)
from app.db.crud import search_activity_tribe as search_activity_
from app.db.crud import set_activity_status
from datetime import datetime

router = APIRouter(prefix="/activity", tags=["石光活动"])

@router.get("/id",response_model=ActivityBase)
async def get_activity(id_:str, db: AsyncSession = Depends(get_db), current_user: UserBase = Depends(get_current_user)):
    """
    获取特定id活动，发请求时必须带token
    :param id_:
    :param db:
    :param current_user:
    :return:
    """
    return await get_activity_by_id(db, id_)

@router.post("/")
async def create_activity(
        activity: ActivityCreate, db: AsyncSession = Depends(get_db),
        current_user: UserBase = Depends(get_current_user)):
    """
        创建新的活动

        :param activity: ActivityCreate模型，包含活动的基本信息
        :param db: 数据库会话，通过依赖注入获取
        :param current_user: 当前登录用户信息，通过依赖注入获取
        :return: 创建成功的活动ID和消息
        """
    # 检查用户权限，只有管理员才能创建活动
    if current_user.identity != "管理员":
         raise HTTPException(status_code=400, detail="权限不足")
    # 自动设置活动发布者为当前用户ID
    activity.publisher = current_user.uid
    # 设置活动初始状态为"未开始"
    activity.status = "未开始"
    # 设置活动所属学院为当前用户所在学院
    activity.college = current_user.college

    # 调用数据库CRUD操作创建活动
    return await create_activity_(db, activity)

@router.get("/me", response_model=list[str])
async def get_my_activity(current_user: UserBase = Depends(get_current_user)):
    """
    返回当前登录用户参与的所有活动ID列表

    :param current_user: 通过依赖注入获取的当前登录用户信息
    :return: 用户参与的活动ID列表
    """
    # 从用户对象的activityId字段中提取所有活动ID的键值并返回

    return current_user.activityId.keys()

@router.get("/fetch_20", response_model=list[str])
async def fetch_20_activity(position:int,
                            db: AsyncSession = Depends(get_db),
                            current_user: UserBase = Depends(get_current_user)):
    """
    返回20个活动ID列表
    """
    return await get_20_activities_ids(db, position)

@router.post("/join/{activity_id}")
async def join_activity(activity_id: str,
                        current_user: UserBase = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)):
    """
    用户加入指定ID的活动

    :param activity_id: 要加入的活动ID
    :param current_user: 通过依赖注入获取的当前登录用户信息
    :param db: 通过依赖注入获取的数据库会话
    :return: 加入活动的结果信息
    """
    return await join_activity_(db, current_user, activity_id)

@router.get("/search",response_model=dict[str,list[str]])
async def search_activity(
        keyword:str = Query(...,description="搜索关键词"),
        db: AsyncSession = Depends(get_db),
        current_user: UserBase = Depends(get_current_user)
):
    """
    搜索活动、部落
    """
    return await search_activity_(db, keyword)

@router.patch("/{activity_id}",response_model=dict[str,str])
async def update_activity(activity_id:str,
                          status:str,
                          current_user: UserBase = Depends(get_current_user),
                          db : AsyncSession = Depends(get_db)):
    """
    根据关键词搜索活动和部落信息

    :param keyword: 搜索关键词，通过Query参数传入
    :param db: 数据库会话，通过依赖注入获取
    :param current_user: 当前登录用户信息，通过依赖注入获取
    :return: 包含活动和部落搜索结果的字典，格式为{"activity": [活动ID列表], "tribe": [部落ID列表]}
    """
    if current_user.identity != "管理员":
        raise HTTPException(status_code=400, detail="权限不足")
    return await set_activity_status(db, activity_id, status)