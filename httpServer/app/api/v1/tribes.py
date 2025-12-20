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
    """
        根据部落ID获取特定部落的详细信息

        :param tribe_id: 部落的唯一标识符
        :param db: 数据库会话，通过依赖注入获取
        :param user: 当前登录用户信息，通过依赖注入获取（用于权限验证）
        :return: 部落基本信息
        """
    return await get_tribe(db, tribe_id)

@router.post("/create")
async def create_tribe_(tribe: TribeCreate, db: AsyncSession = Depends(get_db), user: UserBase = Depends(get_current_user)):
     """
    创建新的部落并写入数据库

    :param tribe: TribeCreate模型，包含部落创建所需的基本信息
    :param db: 数据库会话，通过依赖注入获取
    :param user: 当前登录用户信息，通过依赖注入获取
    :return: 创建成功的部落信息和消息
    """
    # 检查用户权限，只有管理员才能创建部落
    if user.identity != "管理员":
        raise HTTPException(status_code=400, detail="权限不足")
    return await create_tribe(db, tribe)