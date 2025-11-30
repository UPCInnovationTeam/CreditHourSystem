from zoneinfo import reset_tzpath

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.credit import CreditHours
from app.schemas.user import UserBase
from app.core.security import get_current_user
from app.db.crud import set_credit as crud_set_credit
from app.db.database import get_db

router = APIRouter(prefix="/credit", tags=["学时管理"])

@router.get("/", response_model=CreditHours)
async def get_credit(current_user: UserBase = Depends(get_current_user)):
     """
     获取学时函数，需要token认证
     :param current_user: 用户的全部信息，通过解析token获得
     :return: 全部类型学时
     """
     ls = current_user.creditHours  # 获取学时字典 dict[str, int]
     tmp = CreditHours(**ls)        # 将字典转为模型
     return tmp

# @router.post("/")
async def set_credit(credit: CreditHours, current_user: UserBase,
                     db: AsyncSession = Depends(get_db)):
    """
    设置学时函数，仅为内部使用！
    :param db:
    :param credit: 待设置的学时
    :param current_user: 用户的全部信息
    :return: 是否成功
    """
    current_user.creditHours = credit.model_dump() # 将模型转为字典
    await crud_set_credit(db, current_user.uid, current_user.creditHours)
    return {"success": True}


