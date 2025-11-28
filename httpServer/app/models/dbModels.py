from sqlalchemy import Column, String, JSON
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
    activityId = Column(ARRAY(String), nullable=True)
    creditHours = Column(JSON, nullable=True)
    password = Column(String)
    registerTime = Column(String)
