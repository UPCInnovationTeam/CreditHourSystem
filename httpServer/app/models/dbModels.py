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
    #活动
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