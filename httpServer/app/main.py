# app\main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from app.api.v1.routes import api_v1_router

from app.models.dbModels import User
from app.db.database import engine, Base
from app.core.config import tags_metadata

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield
    await engine.dispose()



app = FastAPI(
    title="学时管理系统",
    description="学时管理系统",
    version="0.1.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
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