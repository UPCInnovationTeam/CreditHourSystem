from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.dbmodels2 import Activity
from app.schemas.activity import ActivityCreate,ActivityUpdate
from fastapi import HTTPException

async def create_activity(db: AsyncSession, activity: ActivityCreate):
    db_activity = Activity(**activity.model_dump())
    db.add(db_activity)
    await db.commit()
    await db.refresh(db_activity)
    return db_activity

async def get_activity(db: AsyncSession, activity_id: str):
    result = await db.execute(select(ActivityCreate).where(ActivityCreate.id == id))  # type: ignore
    result = result.scalar_one_or_none()
    return result

