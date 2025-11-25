from datetime import datetime,timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# 配置
SECRET_KEY = "67Nx2DpY0uYp2riM9_CFSK0fhrVtDg2KGRStmHv_TeM"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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
def get_current_user(token: str = Depends(oauth2_scheme)): # 使用oauth2_scheme依赖项获取token
    credentials_exception = HTTPException(  # 异常自动被处理为401错误并返回给客户端
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"}, # 添加WWW-Authenticate头
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # 解码token
        username:str = payload.get("sub")   # 获取用户名, payload是解码后的数据, sub是payload中的字段
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # TODO: 从数据库中获取用户信息

