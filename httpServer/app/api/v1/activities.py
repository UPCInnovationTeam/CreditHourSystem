from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user
from app.schemas.activity import ActivityBase, ActivityCreate
from app.db.database import get_db
from app.schemas.user import UserBase
from app.db.crud import (get_activity as get_activity_by_id, \
                         create_activity as create_activity_, get_20_activities_ids, join_activity_)
from app.db.crud import search_activity as search_activity_
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
    if current_user.identity != "管理员":
        raise HTTPException(status_code=400, detail="权限不足")
    activity.publisher = current_user.uid
    activity.status = "未开始"
    activity.college = current_user.college
    return await create_activity_(db, activity)

@router.get("/me", response_model=list[str])
async def get_my_activity(current_user: UserBase = Depends(get_current_user)):
    return current_user.activityId.keys()

@router.get("/fetch_20", response_model=list[str])
async def fetch_20_activity(position:int,
                            db: AsyncSession = Depends(get_db),
                            current_user: UserBase = Depends(get_current_user)):
    return await get_20_activities_ids(db, position)

@router.post("/join/{activity_id}")
async def join_activity(activity_id: str,
                        current_user: UserBase = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)):
    return await join_activity_(db, current_user, activity_id)

@router.get("/search",response_model=list[str])
async def search_activity(
        keyword:str = Query(...,description="搜索关键词"),
        db: AsyncSession = Depends(get_db),
        current_user: UserBase = Depends(get_current_user)
):
    return await search_activity_(db, keyword)