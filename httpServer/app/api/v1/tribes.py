from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user
from app.db.crud import get_tribe,get_tribe_by_user,create_tribe
from app.db.database import get_db
from app.schemas.tribe import TribeCreate, TribeBase
from app.schemas.user import UserBase

router = APIRouter(prefix="/tribe", tags=["部落管理"])

@router.get("/{tribe_id}", response_model=TribeBase)
async def get_tribe_by_id(tribe_id: str, db: AsyncSession = Depends(get_db), user: UserBase = Depends(get_current_user)):
    return await get_tribe(db, tribe_id)

@router.post("/create")
async def create_tribe_(tribe: TribeCreate, db: AsyncSession = Depends(get_db), user: UserBase = Depends(get_current_user)):
    if user.identity != "管理员":
        raise HTTPException(status_code=400, detail="权限不足")
    return await create_tribe(db, tribe)