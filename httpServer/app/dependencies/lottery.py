import logging
import random

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud import update_user
from app.schemas.user import UserBase
from app.core.config import lottery_config, guaranteed_win_threshold
from app.db.database import get_db


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def credit_lottery(
        db: AsyncSession,
        current_user: UserBase,
        multiplier_levels = lottery_config["multiplier_levels"],
        probability_distribution = lottery_config["probability_distribution"]
) -> tuple[float,dict]:
    user_credit_dict = current_user.model_dump()
    # 检查是否触发保底机制
    current_streak = getattr(current_user, "lottery_streak", 0)
    if current_streak >= guaranteed_win_threshold - 1:
        # 触发保底
        logger.info(f"用户{current_user.uid}触发保底机制")
        selected_level = lottery_config["multiplier_levels"][-2]  # 最高等级奖励
        # 重置连抽计数器
        user_credit_dict["lottery_streak"] = 0

    else:
        # 判断是否接近保底
        weight = raise_probability(current_streak)
        logger.info(f"weight:{weight}")
        _probability_distribution = probability_distribution.copy()
        _probability_distribution[-2] *= weight
        logger.info(f"_probability_distribution:{_probability_distribution}")
        selected_level = random.choices(multiplier_levels, weights=_probability_distribution)[0]
        if selected_level != lottery_config["multiplier_levels"][-2]:
            user_credit_dict["lottery_streak"] = current_streak + 1
        else:
            user_credit_dict["lottery_streak"] = 0
    # current_user = UserBase(**user_credit_dict)
    # await update_user(db, current_user.uid, current_user)
    logger.info(f"用户的lottery_streak为{user_credit_dict['lottery_streak']}")
    return selected_level, user_credit_dict


def raise_probability(current_times: int) -> float:
    """接近保底提升概率"""
    if current_times >= guaranteed_win_threshold * 0.6:
        return 1.5
    elif current_times >= guaranteed_win_threshold * 0.3:
        return 1.2
    else:
        return 1
