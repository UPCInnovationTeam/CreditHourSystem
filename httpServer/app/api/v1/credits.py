from warnings import deprecated
from zoneinfo import reset_tzpath

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.credit import CreditHours
from app.schemas.user import UserBase
from app.core.security import get_current_user, get_user
from app.db.crud import set_credit as crud_set_credit, update_user
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
@deprecated("此接口仅为内部使用，请勿调用！")
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

# 学时交易
@router.post("/trade")
async def trade_credit(trade_credit: CreditHours,
                       target_user_id: str,
                     current_user: UserBase = Depends(get_current_user),
                     db: AsyncSession = Depends(get_db)):
    # 获取目标用户信息
    target_user: UserBase = await get_user(db, target_user_id)
    target_user_dict = target_user.model_dump()
    trade_credit_dict = trade_credit.model_dump()
    # 获取当前用户学时信息
    current_user_dict = current_user.model_dump()
    # 检查当前用户学时是否足够
    for key, value in trade_credit_dict.items():
        if current_user_dict["creditHours"].get(key, 0) < value:
            return {"success": False, "message": f"学时不足，无法交易 {key}"}
    # 扣除当前用户学时
    for key, value in trade_credit_dict.items():
        current_user_dict["creditHours"][key] -= value
    # 增加目标用户学时
    for key, value in trade_credit_dict.items():
        target_user_dict["creditHours"][key] = target_user_dict["creditHours"].get(key, 0) + value
    # 更新数据库
    # 字典转为pydantic模型
    current_user: UserBase = UserBase(**current_user_dict)
    target_user: UserBase = UserBase(**target_user_dict)
    await update_user(db, target_user.uid, target_user)
    await update_user(db, current_user.uid, current_user)

    return {"success": True}



# 学时赠送
@router.post("/gift")
async def gift_credit():
    pass

# 学时抽奖

