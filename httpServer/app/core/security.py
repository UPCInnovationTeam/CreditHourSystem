from datetime import datetime,timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db

from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

from app.db.crud import get_user
from app.schemas.user import UserBase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login") # 创建OAuth2密码模式，tokenUrl为登录接口

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    创建访问令牌
    """
    to_encode = data.copy()
    if expires_delta:   # 判断是否设置过期时间
        expire = datetime.now() + expires_delta # 设置过期时间
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # 默认30分钟
    to_encode.update({"exp": expire})   # 更新令牌
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)   # 返回令牌

# 验证token，获取用户信息
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> UserBase: # 使用oauth2_scheme依赖项获取token
    """
    验证token，获取用户信息
    :param token: 用户token
    :param db: 数据库依赖注入
    :return: UserBase类型的数据
    """
    credentials_exception = HTTPException(  # 异常自动被处理为401错误并返回给客户端
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"}, # 添加WWW-Authenticate头
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # 解码token
        uid:str = payload.get("sub")   # 获取用户名, payload是解码后的数据, sub是payload中的字段
        if uid is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 从数据库中获取用户信息
    user = await get_user(db, uid)
    if user is None:
        raise credentials_exception
    # return {
    #     "uid": user.uid,
    #     "name": user.name,
    #     "identity": user.identity,
    #     "grade": user.grade,
    #     "major": user.major,
    #     "class_": user.class_,
    #     "college": user.college,
    #     "tribeId": user.tribeId or [],
    #     "activityId": user.activityId or [],
    #     "creditHours": user.creditHours or {}
    # }
    return user


    # 测试
    # return {"uid": uid, "name": "张三", "identity": "管理员", "grade": "2021", "major": "软件工程", "class_": "1",
    #         "college": "计算机与信息工程学院", "tribeId": [], "activityId": [], "creditHours":
    #             {"思想成长": 0, "创新创业": 0, "文体发展": 0, "社会实践与志愿服务": 0, "工作履历与技能培训": 0}}
