# app\main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from app.api.v1.routes import api_v1_router

tags_metadata = [
    {"name": "用户管理","description": "用户管理相关接口",},
    {"name": "学时管理","description": "学时管理相关接口",},
    {"name": "认证管理","description": "认证管理相关接口",},
]

app = FastAPI(
    title="学时管理系统",
    description="学时管理系统",
    version="0.1.0",
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router,prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Hello World"}