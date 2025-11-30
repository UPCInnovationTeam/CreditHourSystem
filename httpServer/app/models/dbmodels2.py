from sqlalchemy import Column, String, JSON,Integer,DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from app.db.database import Base
from datetime import datetime


class Activity(Base):
    __tablename__ = "activities"

    uid = Column(String, primary_key=True, index=True)
    registerTime = Column(DateTime,nullable=False)
    #报名时间段，活动时间段
    registrationStratTime = Column(DateTime,nullable=False)
    registrationEndTime = Column(DateTime,nullable=False)
    activityStratTime = Column(DateTime,nullable=False)
    activityEndTime = Column(DateTime,nullable=False)
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