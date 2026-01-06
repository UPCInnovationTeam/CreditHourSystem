from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user
from app.db.crud import get_tribe,get_tribe_by_user,create_tribe,join_tribe_
from app.db.database import get_db
from app.schemas.tribe import TribeCreate, TribeBase, TribeUpdate
from app.schemas.user import UserBase
from app.db.crud import set_tribe_status

router = APIRouter(prefix="/tribe", tags=["部落管理"])

@router.get("/{tribe_id}", response_model=TribeBase)
async def get_tribe_by_id(tribe_id: int, db: AsyncSession = Depends(get_db), user: UserBase = Depends(get_current_user)):
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
        raise HTTPException(status_code=403, detail="权限不足")
    tribe.manager = [user.uid]
    return await create_tribe(db, tribe)


@router.post("/join/{tribe_id}")
async def join_tribe(tribe_id: int,
                        current_user: UserBase = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)):
    """
    用户加入指定ID的部落

    :param tribe_id: 要加入的部落ID
    :param current_user: 通过依赖注入获取的当前登录用户信息
    :param db: 通过依赖注入获取的数据库会话
    :return: 加入活动的结果信息
    """
    return await join_tribe_(db, current_user, tribe_id)

@router.patch("/{tribe_id}",response_model=dict[str,str])
async def update_tribe(tribe_id:int,
                          status:str,
                          current_user: UserBase = Depends(get_current_user),
                          db : AsyncSession = Depends(get_db)):
    if current_user.identity != "管理员":
        raise HTTPException(status_code=400, detail="权限不足")
    return await set_tribe_status(db, tribe_id, status)


@router.delete("/quit/{tribe_id}", response_model=dict[str, str])
async def quit_tribe(tribe_id: int,
                     current_user: UserBase = Depends(get_current_user),
                     db: AsyncSession = Depends(get_db)):

    from app.db.crud import quit_tribe_
    return await quit_tribe_(db, current_user, tribe_id)


