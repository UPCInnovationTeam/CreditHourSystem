from sqlalchemy import Column, String, JSON,Integer,DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from app.db.database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    uid = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    identity = Column(String)
    grade = Column(String)
    major = Column(String)
    class_ = Column(String)
    college = Column(String)
    tribeId = Column(ARRAY(String), nullable=True)
    activityId = Column(JSON, nullable=True)
    creditHours = Column(JSON, nullable=True)
    password = Column(String)
    registerTime = Column(String)
    """
    用户uid，姓名，身份，年级，专业，班级，学院，
    所属部落ID列表，参与活动ID列表
    获得学分小时数，密码，注册时间
    """

class Activity(Base):
    __tablename__ = "activities"

    uid = Column(String, primary_key=True, index=True)
    registerTime = Column(String,nullable=False)
    #报名时间段，活动时间段
    registrationStratTime = Column(String,nullable=False)
    registrationEndTime = Column(String,nullable=False)
    activityStratTime = Column(String,nullable=False)
    activityEndTime = Column(String,nullable=False)
    #人数限制，当前报名人数，报名人id
    maxParticipants = Column(Integer,nullable=False)
    currentParticipants = Column(Integer,nullable=False)
    participantsIDs = Column(ARRAY(Integer),nullable=False)
    #活动基本信息
    title = Column(String,nullable=False)
    content = Column(String,nullable=False)
    publisher = Column(String,nullable=False)
    imageUrl = Column(String,nullable=False)
    college = Column(String,nullable=False)
    #限制条件（年纪，学院，部落）
    gradeRestrictions = Column(ARRAY(String),default=[])
    collegeRestrictions = Column(ARRAY(String),default=[])
    tribeRestrictions = Column(ARRAY(String),default=[])
    status = Column(String)
    #学时
    creditClass = Column(String)
    creditHours = Column(Integer)

class Tribe(Base):
    __tablename__ = "tribe"
    uid = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    college = Column(String, index=True)
    manager = Column(ARRAY(String), default=[])
    members = Column(ARRAY(String), default=[])
    activityID = Column(ARRAY(String), default=[])
    """
    部落名称，所属学院
    部落管理者列表，部落成员列表，部落关联活动ID列表
    """