from zoneinfo import reset_tzpath

from fastapi import APIRouter, Depends
from app.schemas.credit import CreditHours
from app.schemas.user import UserBase
from app.core.security import get_current_user

router = APIRouter(prefix="/credit", tags=["学分管理"])

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

@router.post("/", response_model=CreditHours)
async def set_credit(credit: CreditHours, current_user: UserBase = Depends(get_current_user)):
     """
     设置学时函数，需要token认证
     :param credit: 待设置的学时
     :param current_user: 用户的全部信息，通过解析token获得
     :return: 是否成功
     """
     current_user.creditHours = credit.model_dump() # 将模型转为字典
     # TODO: 设置学时，保存到数据库
     return {"success": True}


