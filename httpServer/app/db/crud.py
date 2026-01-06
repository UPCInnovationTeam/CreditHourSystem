from typing import Any, Coroutine, Sequence
from warnings import deprecated

from PIL.ImageChops import offset
from fastapi import HTTPException
from sqlalchemy import select, Row, RowMapping, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.coercions import expect

from app.models.dbModels import User
from app.schemas.user import UserBase,UserCreate,UserLogin
from datetime import datetime
from app.dependencies.tools import hash_password
import logging
from app.models.dbModels import Activity,Tribe
from app.schemas.activity import ActivityCreate, ActivityUpdate, ActivityBase
from app.schemas.tribe import TribeCreate,TribeBase,TribeUpdate

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def some_function():
    # 在函数内部导入，避免循环导入
    from app.api.v1.tribes import update_tribe
    # 使用 update_tribe


async def create_user(db: AsyncSession, user: UserCreate):
    """
    创建新用户并写入数据库
    :param user:
    :param db:数据库会话对象
    user:用户创建信息
    :return:创建成功的用户信息
    """
    # logger.info(f"密码：{user.password}")
    user.password = hash_password(user.password)
    # logger.info(f"哈希后的密码：{user.password}")
    user.identity = "使用者"
    user.registerTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #初始化
    user.tribeId = []
    user.activityId = {}
    user.creditHours = {"mentalGrowth": 0, "innovation": 0, "culturalSports": 0, "socialPractice": 0, "skill": 0}

    del user.email
    del user.code
    db_user = User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return UserBase(**user.model_dump())

async def get_user(db: AsyncSession, uid: str) -> UserBase:
    """
    根据UID获取用户
    :param db: get_db()依赖注入
    :param uid: 用户的UID
    :return: 返回用户信息(pydantic模型)
    """
    # logger.info(f"获取用户信息，UID：{uid}")
    # 获取现有的用户ORM对象
    result = await db.execute(select(User).where(User.uid == uid))  # type: ignore
    db_user = result.scalar_one_or_none()

    if db_user is None:
        logger.warning(f"用户不存在，UID：{uid}")
        raise ValueError("用户不存在")


    return UserBase.model_validate(db_user)


async def get_user_by_name(db: AsyncSession, name: str) -> UserBase:
    """
    根据姓名获取用户信息
    :param db: 数据库会话对象
    :param name: 用户姓名
    :return: 匹配的用户信息
    """
    logger.info(f"根据姓名获取用户信息，姓名：{name}")

    # 使用正确的查询语法
    result = await db.execute(select(User).where( User.name == name))
    db_user = result.scalar_one_or_none()

    if db_user is None:
        logger.warning(f"用户不存在，姓名：{name}")
        raise ValueError("用户不存在")

    return UserBase.model_validate(db_user)


async def get_user_password(db: AsyncSession, uid: str) -> str:
    """
    根据UID获取用户密码
    :param db: get_db()依赖注入
    :param uid: 用户的UID
    :return: 返回用户信息(pydantic模型)
    """
    # 获取现有的用户ORM对象
    result = await db.execute(select(User).where(User.uid == uid))  # type: ignore
    db_user = result.scalar_one_or_none()

    if db_user is None:
        raise ValueError("用户不存在")

    return db_user.password


async def update_user(db: AsyncSession, uid: str, user: UserBase) -> UserBase:
    """
    更新用户信息（任意）
    :param user:
    :param uid:
    :param db: 数据库会话对象
    :uid:用户id
    :user:更新后用户信息
    :return:更新后用户信息
    异常:
    ValueError:如果用户不存在
    """
    # 获取现有的用户ORM对象
    result = await db.execute(select(User).where(User.uid == uid))  # type: ignore
    db_user = result.scalar_one_or_none()

    if db_user is None:
        raise ValueError("用户不存在")

    # 将Pydantic模型转换为字典并更新ORM对象
    update_data = user.model_dump(exclude_unset=True)
    #确保值更新实际的字段，避免将None写入数据库
    logger.info(f"更新用户信息：{update_data}")
    for key, value in update_data.items():
        setattr(db_user, key, value)

    # 提交更改到数据库
    await db.commit()
    await db.refresh(db_user)

    # 返回更新后的用户信息（Pydantic模型）
    return UserBase.model_validate(db_user)


async def delete_user(db: AsyncSession, uid: str) -> bool:
    """
    根据UID删除用户
    :param db: 数据库会话对象
    :param uid: 用户的UID
    :return: 删除是否成功
    """
    logger.info(f"删除用户，UID：{uid}")

    # 获取现有的用户ORM对象
    result = await db.execute(select(User).where(User.uid == uid))
    db_user = result.scalar_one_or_none()

    if db_user is None:
        logger.warning(f"用户不存在，UID：{uid}")
        raise ValueError("用户不存在")

    # 从数据库中删除用户
    await db.delete(db_user)
    await db.commit()

    logger.info(f"用户已成功删除，UID：{uid}")
    return True


async def login(db: AsyncSession, user: UserLogin) -> str:
    """
       用户登录验证，同时记录活跃数据
       :param db: 数据库会话
       :param user: 登录信息
       :return: 登录成功的用户密码
       """
    # 验证用户是否存在
    password = await get_user_password(db, user.uid)

    # 记录用户活跃数据
    await record_user_login_activity(db, user.uid)

    return password

@deprecated("已经弃用")
async def set_credit(db: AsyncSession, uid: str, credit: dict) :
    """
    set_credit已弃用，请使用update_user代替
    设置用户学分
    :param db:
    :param uid:
    :param credit:包含学时类别及其数值的新积分数据
    :return:一个包含消息与跟新后学分详情的字典
    """
    user = await get_user(db, uid)
    user.creditHours = credit
    user_ = User(**user.model_dump())
    await db.commit()
    await db.refresh(user_)
    return {"message": "修改成功", "data": user.model_dump()["creditHours"]}

async def create_activity(db: AsyncSession, activity: ActivityCreate):
    """
    创建石光活动，并写入数据库
    :param db:
    :param activity: 活动信息
    :return:
    """
    last_activity = await get_last_activity(db)
    activity.uid = int(last_activity.uid) + 1 if last_activity else 1
    db_activity = Activity(**activity.model_dump())
    db.add(db_activity)
    await db.commit()
    await db.refresh(db_activity)
    return {"id": db_activity.uid, "message": "创建成功"}

async def get_activity(db: AsyncSession, activity_id: int) -> Activity:
    """
    根据活动id获取活动具体信息
    :param db:
    :param activity_id: 活动id
    :return: 活动信息
    """
    result = await db.execute(select(Activity).where(Activity.uid == activity_id))  # type: ignore
    result = result.scalar_one_or_none()
    return result

async def get_last_activity(db: AsyncSession) -> ActivityBase:
    """
    获取Activity表的最后一行数据（按uid排序）
    """
    result = await db.execute(
        select(Activity).order_by(Activity.uid.desc()).limit(1)
    )
    result = result.scalar_one_or_none()
    return result

async def get_20_activities_ids(db: AsyncSession, position: int = 0):
    """
    获取Activity表的20行数据（按uid排序）
    return:活动列表（按uid降序排列）
    """
    result = await db.execute(
        select(Activity.uid).order_by(Activity.uid.desc()).limit(20).offset(position)
    )
    return result.scalars().all()

async def join_activity_(db: AsyncSession, user: UserBase, activity_id: int):
    """
    加入活动
    """
    if activity_id in user.activityId.keys():
        return {"message": "已加入"}
    # 检查限制条件
    activity_info = ActivityBase.model_validate(await get_activity(db, activity_id))    # 先获取活动信息
    if activity_info.gradeRestrictions and user.grade not in activity_info.gradeRestrictions:
        return {"message": "年级不符合要求"}
    if activity_info.collegeRestrictions and user.college not in activity_info.collegeRestrictions:
        return {"message": "学院不符合要求"}
    if activity_info.tribeRestrictions:
        for i in user.tribeId:
            if i in activity_info.tribeRestrictions:
                break
        else:
            return {"message": "部落不符合要求"}
    user.activityId[activity_id] = 0    # 0 为未开始，1 为签到成功，2 为签退成功
    await update_user(db, user.uid, user)
    # 更新活动成员id
    activity = await get_activity(db, activity_id)
    activity: ActivityBase = ActivityBase.model_validate(activity)
    activity.participantsIDs = activity.participantsIDs + [user.uid]
    return await update_activity(db, activity_id, activity)
    return {"message": "加入成功"}

async def check_in_activity(db: AsyncSession, uid: str, activity_id: int):
    """
        处理用户活动签到功能

        :param db: 数据库会话对象
        :param uid: 用户唯一标识符
        :param activity_id: 活动唯一标识符
        :return: 包含签到结果信息的字典
        """

    # 获取用户信息并转换为UserBase模型
    user = await get_user(db, uid)
    user: UserBase = UserBase.model_validate(user)
    # 检查用户是否已加入该活动
    if activity_id not in user.activityId.keys():
        logger.info(f"{uid}未加入{activity_id}活动,用户的活动列表:{user.activityId.keys()}")
        return {"message": "未加入"}
    # 检查用户是否已经签到
    if user.activityId[activity_id] == 1:
        logger.info(f"{uid}已签到{activity_id}活动")
        return {"message": "已签到"}
    # 如果用户已加入但未签到，则执行签到操作
    if user.activityId[activity_id] == 0:
        user.activityId[activity_id] = 1
        await update_user(db, user.uid, user)
        logger.info(f"{uid}签到{activity_id}活动")
        return {"message": "签到成功"}
    # 其他情况返回签到失败
    else:
        return {"message": "签到失败"}

async def check_out_activity(db: AsyncSession, uid: str, activity_id: int):
    """
        处理用户活动签退功能，并根据活动类型增加相应的学分

        :param db: 数据库会话对象
        :param uid: 用户唯一标识符
        :param activity_id: 活动唯一标识符
        :return: 包含签退结果信息的字典
        """

    # 获取用户信息并转换为UserBase模型
    user = await get_user(db, uid)
    user: UserBase = UserBase.model_validate(user)

    # 检查用户是否已加入该活动
    if activity_id not in user.activityId.keys():
        return {"message": "未加入"}

    # 检查用户是否已经签退
    if user.activityId[activity_id] == 2:
        return {"message": "已签退"}

    # 如果用户已签到但未签退，则执行签退操作
    if user.activityId[activity_id] == 1:
        activity = await get_activity(db, activity_id)
        activity: ActivityBase = ActivityBase.model_validate(activity)
        # user.creditHours[activity.creditClass] += activity.creditHours
        # 根据活动类别给用户增加相应类型的学分

        if activity.creditClass == "思想成长":
            user.creditHours["mentalGrowth"] += activity.creditHours
        elif activity.creditClass == "创新创业":
            user.creditHours["innovation"] += activity.creditHours
        elif activity.creditClass == "文体发展":
            user.creditHours["culturalSports"] += activity.creditHours
        elif activity.creditClass == "社会实践与志愿服务":
            user.creditHours["socialPractice"] += activity.creditHours
        elif activity.creditClass == "工作履历与技能培训":
            user.creditHours["skill"] += activity.creditHours
        else:
            return {"message": "签退失败"}
        user.activityId[activity_id] = 2
        await update_user(db, user.uid, user)
        return {"message": "签退成功"}
    else:
        return {"message": "签退失败"}

async def update_activity(db: AsyncSession, activity_id: int,
                          activity: ActivityBase):
    # 获取现有活动
    activity_ori = await get_activity(db, activity_id)
    if activity_ori is None:
        return {"message": "活动不存在"}
    update_data = activity.model_dump()
    for key, value in update_data.items():
        setattr(activity_ori, key, value)
    # 提交更改到数据库
    await db.commit()
    await db.refresh(activity_ori)

    return {"message": "更新成功"}



async def set_activity_status(db: AsyncSession,
                              activity_id: int,
                              status: str):
    activity = await get_activity(db, activity_id)
    activity: ActivityBase = ActivityBase.model_validate(activity)
    activity.status = status
    return await update_activity(db, activity_id, activity)


async def search_activity_tribe(db: AsyncSession, keyword: str):
    """
    根据关键词模糊搜索活动、部落
    :param db: 通过Depends获取的数据库
    :param keyword: 可以是uid或title或content
    :return: dict {"activity":list[str],"tribe":list[str]}
    """
    # 搜索活动
    activity_result = await db.execute(
        select(Activity.uid).filter(
            or_(
                # Activity.uid.contains(keyword),
                Activity.title.contains(keyword),
                Activity.content.contains(keyword)
            )
        )
    )
    activities = list(activity_result.scalars().all())

    # 搜索部落
    tribe_result = await db.execute(
        select(Tribe.uid).filter(
            or_(
                # Tribe.uid.contains(keyword),
                Tribe.name.contains(keyword),
                Tribe.college.contains(keyword)
            )
        )
    )
    tribes = list(tribe_result.scalars().all())

    return {"activity": activities, "tribe": tribes}

async def create_tribe(db: AsyncSession, tribe: TribeCreate):
    """
    创建部落，并写入数据库
    :param db:
    :param tribe: 部落信息
    :return:
    """
    result = await db.execute(select(Tribe).order_by(Tribe.uid.desc()).limit(1))
    last_tribe = result.scalar_one_or_none()
    tribe.uid = int(last_tribe.uid) + 1 if last_tribe else 1
    db_tribe = Tribe(**tribe.model_dump())
    db.add(db_tribe)
    await db.commit()
    await db.refresh(db_tribe)
    return {"id": db_tribe.uid, "message": "部落注册成功"}


async def get_tribe(db: AsyncSession, tribe_id: int) -> Tribe:
    """
    根根据活动id获取活动具体信息
    :param db:
    :param tribe_id: 活动id
    :return: 活动信息
    """


    tribe_id = int(tribe_id)
    result = await db.execute(select(Tribe).where(Tribe.uid == tribe_id))  # type: ignore
    result = result.scalar_one_or_none()

    if result is None:
        raise HTTPException(status_code=404, detail="部落不存在")
    return result

async def get_tribe_by_user(db: AsyncSession, username: str):
    """
    根据用户名成员查询对应部落
    """
    result = await db.execute(select(Tribe).where(
        or_(Tribe.members.contains(username))))
    result = result.scalar_one_or_none()
    return result


async def set_tribe_status(db: AsyncSession,
                           tribe_id: int,
                           status: str):
    """
    更新部落状态
    :param db:
    :param tribe_id:部落ID
    :param status:
    :return:更新后部落信息
    """
    tribe = await get_tribe(db, tribe_id)
    if not tribe:
        raise HTTPException(status_code=404, detail="部落不存在")
    tribe.status = status
    await db.commit()
    await db.refresh(tribe)
    return tribe


async def update_tribe_member_count(db: AsyncSession, tribe_id: int, new_member_count: int):
    """
    更新部落成员数量
    """
    tribe = await get_tribe(db, tribe_id)
    if not tribe:
        return {"message": "部落不存在"}

    tribe.memberNum = new_member_count
    await db.commit()
    await db.refresh(tribe)
    return {"message": "成员数量更新成功", "memberNum": tribe.memberNum}


async def join_tribe_(db: AsyncSession, user: UserBase, tribe_id: int):
    """
    加入部落
    """
    if tribe_id in user.tribeId:
        return {"message": "已加入"}

    result = await db.execute(
        select(Tribe).where(Tribe.uid == int(tribe_id)) # type: ignore
    )
    tribe = result.scalar_one_or_none()

    if not tribe:
        return {"message": "部落不存在"}

    current_members = tribe.members if tribe.members else []
    if user.name in current_members:
        return {"message": "用户已经在部落里面"}

    # 更新用户
    user.tribeId.append(tribe_id)
    await update_user(db, user.uid, user)

    #构建新的成员列表
    new_members = current_members + [user.name]
    tribe.members = new_members
    tribe.memberNum = len(new_members)

    await update_tribe_member_count(db, tribe_id, len(new_members))

    return {"message": "加入成功", "memberNum": len(new_members)}

async def quit_tribe_(db: AsyncSession, user: UserBase, tribe_id: int):
    """
    退出部落
    """
    #检查是否加入
    if tribe_id not in user.tribeId:
        return {"message": "未加入"}

    user.tribeId.remove(tribe_id)
    await update_user(db, user.uid, user)

    result = await db.execute(
        select(Tribe).where(Tribe.uid == int(tribe_id)) # type: ignore
    )
    tribe = result.scalar_one_or_none()

    current_members = tribe.members if tribe.members else []
    if user.name in current_members:
        current_members = [member for member in current_members if member != user.name]

    tribe.members = current_members
    tribe.memberNum = len(current_members)

    await db.commit()
    await db.refresh(tribe)

    return {"message": "退出成功"}

async def update_tribe(db: AsyncSession, tribe_id: int,
                       tribe: TribeUpdate):
    """
    更新部落信息
    """
    tribe_ori = await get_tribe(db, tribe_id)
    if tribe_ori is None:
        return {"message": "部落不存在"}
    update_data = tribe.model_dump()
    for key, value in update_data.items():
        setattr(tribe_ori, key, value)
    # 提交更改到数据库
    await db.commit()
    await db.refresh(tribe_ori)
    return {"message": "更新成功"}

from app.schemas.user import PageResponse as UserPageResponse
async def get_page_users(db: AsyncSession, page: int, page_size: int) -> UserPageResponse:
    """
    获取所有用户信息
    :param db:
    :param page: 页数
    :param page_size: 每页用户数量
    :return: PageResponse
    """
    offset = (page - 1) * page_size # 计算偏移量

    # 查询总共的用户数量
    total_result = await db.execute(select(func.count(User.uid)))
    total_users = len(total_result.scalars().all())

    # 通过偏移量获取用户列表'
    tmp = select(User).offset(offset).limit(page_size)
    result = await db.execute(tmp)
    users = result.scalars().all()

    # orm转pydantic
    user_items = [UserBase.model_validate(user) for user in users]

    # 构造PageResponse
    return UserPageResponse(
        items=user_items,
        total=total_users,
        page=page,
        size=page_size,
    )


from sqlalchemy import select, func
from datetime import date
from app.models.dbModels import DailyStatsSummary, User,DailyActiveUserStats


async def record_user_login_activity(db: AsyncSession, user_id: str, platform: str = 'web'):
    """
    记录用户登录活跃数据
    :param db: 数据库会话
    :param user_id: 用户ID
    :param platform: 平台标识
    :return: 是否成功记录
    """
    today_str = date.today().strftime("%Y-%m-%d")

    # 检查今天是否已记录该用户的活跃数据
    result = await db.execute(
        select(DailyActiveUserStats).where(
            DailyActiveUserStats.user_id == user_id,
            DailyActiveUserStats.stat_date == today_str,
            DailyActiveUserStats.platform == platform
        )
    )
    existing_record = result.scalar_one_or_none()

    if not existing_record:
        # 创建新的活跃记录
        activity_record = DailyActiveUserStats(
            stat_date=today_str,
            user_id=user_id,
            platform=platform
        )
        db.add(activity_record)
        await db.commit()
        await db.refresh(activity_record)
        return True

    return False  # 今天已记录过该用户活跃数据


async def get_daily_active_users_count(db: AsyncSession, target_date: str = None) -> int:
    """
    获取指定日期的日活跃用户数
    :param db: 数据库会话
    :param target_date: 目标日期，格式：YYYY-MM-DD，默认为今天
    :return: 日活跃用户数
    """
    if target_date is None:
        target_date = date.today().strftime("%Y-%m-%d")

    result = await db.execute(
        select(func.count(DailyActiveUserStats.user_id.distinct()))
        .where(DailyActiveUserStats.stat_date == target_date)
    )
    return result.scalar_one_or_none() or 0


async def get_daily_active_users_list(db: AsyncSession, target_date: str = None) -> list:
    """
    获取指定日期的活跃用户列表
    :param db: 数据库会话
    :param target_date: 目标日期，格式：YYYY-MM-DD，默认为今天
    :return: 活跃用户ID列表
    """
    if target_date is None:
        target_date = date.today().strftime("%Y-%m-%d")

    result = await db.execute(
        select(DailyActiveUserStats.user_id)
        .where(DailyActiveUserStats.stat_date == target_date)
    )
    return [row[0] for row in result.all()]


async def get_daily_active_users_stats(db: AsyncSession, target_date: str = None) -> dict:
    """
    获取指定日期的详细活跃统计信息
    :param db: 数据库会话
    :param target_date: 目标日期，格式：YYYY-MM-DD，默认为今天
    :return: 包含活跃用户数、新增用户数、累计用户数的字典
    """
    if target_date is None:
        target_date = date.today().strftime("%Y-%m-%d")

    # 获取当日活跃用户数
    dau_count = await get_daily_active_users_count(db, target_date)

    # 获取当日新增用户数
    new_users_result = await db.execute(
        select(func.count(User.uid))
        .where(func.substring(User.registerTime, 1, 10) == target_date)
    )
    new_users_count = new_users_result.scalar_one_or_none() or 0

    # 获取累计用户数
    total_users_result = await db.execute(select(func.count(User.uid)))
    total_users_count = total_users_result.scalar_one_or_none() or 0

    return {
        "stat_date": target_date,
        "dau_count": dau_count,
        "new_users_count": new_users_count,
        "total_users_count": total_users_count
    }


async def get_recent_daily_stats(db: AsyncSession, days: int = 7) -> list:
    """
    获取最近几天的日活跃统计
    :param db: 数据库会话
    :param days: 天数，默认7天
    :return: 最近几天的统计列表
    """
    from datetime import timedelta

    # 计算开始日期
    start_date = (date.today() - timedelta(days=days - 1)).strftime("%Y-%m-%d")

    # 获取最近几天的活跃用户数
    result = await db.execute(
        select(
            DailyActiveUserStats.stat_date,
            func.count(DailyActiveUserStats.user_id.distinct()).label('dau_count')
        )
        .where(DailyActiveUserStats.stat_date >= start_date)
        .group_by(DailyActiveUserStats.stat_date)
        .order_by(DailyActiveUserStats.stat_date)
    )

    stats_list = []
    for row in result.all():
        stat_date = row.stat_date
        dau_count = row.dau_count

        # 获取当天新增用户数
        new_users_result = await db.execute(
            select(func.count(User.uid))
            .where(func.substring(User.registerTime, 1, 10) == stat_date)
        )
        new_users_count = new_users_result.scalar_one_or_none() or 0

        stats_list.append({
            "stat_date": stat_date,
            "dau_count": dau_count,
            "new_users_count": new_users_count
        })

    return stats_list


async def update_daily_stats_summary(db: AsyncSession, target_date: str = None):
    """
    更新日活汇总表
    :param db: 数据库会话
    :param target_date: 目标日期，格式：YYYY-MM-DD，默认为昨天
    """
    if target_date is None:
        from datetime import timedelta
        target_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    # 获取统计信息
    stats = await get_daily_active_users_stats(db, target_date)

    # 检查是否已存在该日期的汇总记录
    result = await db.execute(
        select(DailyStatsSummary).where(DailyStatsSummary.stat_date == target_date)
    )
    existing_summary = result.scalar_one_or_none()

    if existing_summary:
        # 更新现有记录
        existing_summary.dau_count = stats["dau_count"]
        existing_summary.new_users_count = stats["new_users_count"]
        existing_summary.total_users_count = stats["total_users_count"]
    else:
        # 创建新记录
        summary = DailyStatsSummary(
            stat_date=stats["stat_date"],
            dau_count=stats["dau_count"],
            new_users_count=stats["new_users_count"],
            total_users_count=stats["total_users_count"]
        )
        db.add(summary)

    await db.commit()



