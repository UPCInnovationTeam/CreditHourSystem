import logging
from warnings import deprecated
from zoneinfo import reset_tzpath

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.credit import CreditHours
from app.schemas.user import UserBase
from app.core.security import get_current_user, get_user
from app.db.crud import set_credit as crud_set_credit, update_user
from app.db.database import get_db

from fastapi import Query, HTTPException
import random
from app.db.crud import get_activity as get_activity_by_id
from app.schemas.activity import ActivityBase

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
from app.core.config import lottery_config
from app.dependencies.lottery import credit_lottery as cl
@router.post("/lottery")
async def credit_lottery(
        credit_type: str = Query(..., description="学时类型，如mentalGrowth、innovation等"),
        base_credit_value: int = Query(..., ge=1, description="投入的基础学时值"),
        current_user: UserBase = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    学时抽奖功能 - 用户自定义学时类型和基础值
    :param credit_type: 学时类型，用户自定义选择
    :param base_credit_value: 投入的基础学时值，用户自定义
    :param current_user: 当前用户
    :param db: 数据库会话
    :return: 抽奖结果和获得的学时
    """
    # 1. 检查用户是否拥有足够的基础学时
    user_credit_dict = current_user.model_dump()
    current_credit = user_credit_dict["creditHours"].get(credit_type, 0)

    if current_credit < base_credit_value:
        raise HTTPException(status_code=400,
                            detail=f"用户{credit_type}学时不足，当前拥有{current_credit}，需要{base_credit_value}")

    # 3. 执行抽奖算法
    # selected_level = random.choices(
    #     lottery_config["multiplier_levels"],
    #     weights=lottery_config["probability_distribution"]
    # )[0]
    selected_level, user_credit_dict = await cl(db, current_user)

    # 计算实际获得的学时
    actual_credit = int(base_credit_value * selected_level)

    # 4. 扣除基础学时并添加抽奖获得的学时
    user_credit_dict["creditHours"][credit_type] = current_credit - base_credit_value + actual_credit

    # 5. 更新数据库
    updated_user: UserBase = UserBase(**user_credit_dict)
    await update_user(db, current_user.uid, updated_user)

    logger.info(f""
                       f"用户{current_user.uid}抽奖成功！"
                       f"投入{base_credit_value}个{credit_type}学时，"
                       f"获得{actual_credit}个{credit_type}学时")

    # 6. 返回抽奖结果
    return {
        "success": True,
        "credit_type": credit_type,
        "base_credit": base_credit_value,
        "multiplier": selected_level,
        "actual_credit": actual_credit,
        "message": f"抽奖成功！投入{base_credit_value}个{credit_type}学时，获得{actual_credit}个{credit_type}学时"
    }

@router.get("/lottery_config", response_model=dict[str, list[float]])
async def get_lottery_config():
    return lottery_config




