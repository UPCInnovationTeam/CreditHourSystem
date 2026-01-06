from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db import crud
from typing import List, Dict, Any
from datetime import date, timedelta

router = APIRouter(prefix="/record", tags=["日活统计"])


@router.get("/daily-active-users", summary="获取指定日期的日活跃用户数")
async def get_daily_active_users(
        target_date: str = None,
        db: AsyncSession = Depends(get_db)
):
    """
    获取指定日期的日活跃用户数
    - target_date: 目标日期，格式：YYYY-MM-DD，默认为今天
    """
    try:
        count = await crud.get_daily_active_users_count(db, target_date)
        current_date = target_date if target_date else date.today().strftime("%Y-%m-%d")
        return {
            "stat_date": current_date,
            "dau_count": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取日活跃用户数失败: {str(e)}")


@router.get("/daily-active-users-list", summary="获取指定日期的活跃用户列表")
async def get_daily_active_users_list(
        target_date: str = None,
        db: AsyncSession = Depends(get_db)
):
    """
    获取指定日期的活跃用户列表
    - target_date: 目标日期，格式：YYYY-MM-DD，默认为今天
    """
    try:
        user_list = await crud.get_daily_active_users_list(db, target_date)
        current_date = target_date if target_date else date.today().strftime("%Y-%m-%d")
        return {
            "stat_date": current_date,
            "active_users": user_list,
            "count": len(user_list)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取活跃用户列表失败: {str(e)}")


@router.get("/daily-stats", summary="获取指定日期的详细活跃统计")
async def get_daily_stats(
        target_date: str = None,
        db: AsyncSession = Depends(get_db)
):
    """
    获取指定日期的详细活跃统计信息
    - target_date: 目标日期，格式：YYYY-MM-DD，默认为今天
    """
    try:
        stats = await crud.get_daily_active_users_stats(db, target_date)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取详细活跃统计失败: {str(e)}")


@router.get("/recent-daily-stats", summary="获取最近几天的日活跃统计")
async def get_recent_daily_stats(
        days: int = 7,
        db: AsyncSession = Depends(get_db)
):
    """
    获取最近几天的日活跃统计
    - days: 天数，默认7天，最大30天
    """
    if days > 30:
        days = 30  # 限制最大查询天数
    try:
        stats_list = await crud.get_recent_daily_stats(db, days)
        return {
            "days": days,
            "stats_list": stats_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取最近日活跃统计失败: {str(e)}")


@router.get("/daily-summary", summary="获取日活汇总数据")
async def get_daily_summary(
        target_date: str = None,
        db: AsyncSession = Depends(get_db)
):
    """
    获取日活汇总数据（从DailyStatsSummary表）
    - target_date: 目标日期，格式：YYYY-MM-DD，默认为今天
    """
    try:
        if target_date is None:
            target_date = date.today().strftime("%Y-%m-%d")

        from app.models.dbModels import DailyStatsSummary
        from sqlalchemy import select

        result = await db.execute(
            select(DailyStatsSummary).where(DailyStatsSummary.stat_date == target_date)
        )
        summary = result.scalar_one_or_none()

        if not summary:
            # 如果没有汇总数据，返回当天的统计数据
            stats = await crud.get_daily_active_users_stats(db, target_date)
            return stats

        return {
            "stat_date": summary.stat_date,
            "dau_count": summary.dau_count,
            "new_users_count": summary.new_users_count,
            "total_users_count": summary.total_users_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取日活汇总数据失败: {str(e)}")


@router.post("/update-daily-summary", summary="更新日活汇总表")
async def update_daily_summary(
        target_date: str = None,
        db: AsyncSession = Depends(get_db)
):
    """
    手动更新日活汇总表
    - target_date: 目标日期，格式：YYYY-MM-DD，默认为昨天
    """
    try:
        await crud.update_daily_stats_summary(db, target_date)
        current_date = target_date if target_date else (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        return {
            "message": "日活汇总数据更新成功",
            "stat_date": current_date
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新日活汇总数据失败: {str(e)}")
