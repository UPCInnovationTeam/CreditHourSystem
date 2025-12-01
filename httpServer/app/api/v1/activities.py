from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user
from app.schemas.activity import ActivityBase, ActivityCreate
from app.db.database import get_db
from app.schemas.user import UserBase
from app.db.crud import get_activity as get_activity_by_id, create_activity as create_activity_
from datetime import datetime

router = APIRouter(prefix="/activity", tags=["石光活动"])

@router.get("/",response_model=ActivityBase)
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
    return await create_activity_(db, activity)

