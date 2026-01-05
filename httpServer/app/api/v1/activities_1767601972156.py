try:
    user_to_delete = await get_user_by_uid(db, uid)
    # 可以在这里添加日志或验证逻辑
    logger.info(f"准备删除用户: {user_to_delete.uid}")
except ValueError:
    raise HTTPException(status_code=404, detail="用户不存在")
