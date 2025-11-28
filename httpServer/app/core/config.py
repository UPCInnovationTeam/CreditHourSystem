#元数据
tags_metadata = [
    {"name": "用户管理","description": "用户管理相关接口",},
    {"name": "学时管理","description": "学时管理相关接口",},
    {"name": "认证管理","description": "认证管理相关接口",},
    {"name": "二维码","description": "二维码相关接口",}
]
# 邮箱
sender_email = "19862266073@163.com"
sender_email_pwd = "KNxM5LZHRWjZyXYW"
# token验证
SECRET_KEY = "67Nx2DpY0uYp2riM9_CFSK0fhrVtDg2KGRStmHv_TeM"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# 数据库
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost/creditHourSystem"
# 签到签退二维码链接
qrcode_url = f"http://127.0.0.1:8000/api/v1/qrcode/"
qr_window_seconds = 300  #二维码有效时间，单位秒