# app\main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 导入各个子路由
# from app.api.v1 import