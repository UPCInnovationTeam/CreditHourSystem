# app/api/v1/routes.py
from fastapi import APIRouter

# 导入各个子路由
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.credits import router as credits_router
from app.api.v1.qrCode import router as qrCode_router
from app.api.v1.activities import router as activities_router
from app.api.v1.image import router as image_router
from app.api.v1.tribes import router as tribes_router

# 创建一个顶层的 APIRouter 实例
api_v1_router = APIRouter()

# 将所有子路由“包含”进来
api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(credits_router)
api_v1_router.include_router(qrCode_router)
api_v1_router.include_router(activities_router)
api_v1_router.include_router(image_router)
api_v1_router.include_router(tribes_router)