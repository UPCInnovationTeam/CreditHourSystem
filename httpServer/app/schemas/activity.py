from pydantic import BaseModel
from typing import List,Optional
class ActivityBase(BaseModel):
    """
    id/注册时间/报名开始，截至时间/活动开始，结束时间/限制报名人数/当前报名人数/报名者id/活动标题/
    内容/发布者/活动图片地址/活动院校/限制条件（年纪/部落/学院）
    """
    uid : str
    registerTime : str
    registrationStratTime : str
    registrationEndTime : str
    activityStratTime : str
    activityEndTime : str
    maxParticipants :int
    currentParticipants : int
    participantsIDs : list[str]
    title : str
    content : str
    publisher : str
    imageUrl : str
    college : str
    #限制条件（年纪，学院，部落）
    gradeRestrictions : list[str]
    collegeRestrictions : list[str]
    tribeRestrictions : list[str]
    status: str # 未开始、签到、签退、已结束

    creditClass: str    # 思想成长、创新创业、文体发展、社会实践与志愿服务、工作履历与技能培训
    creditHours: int

    class Config:
        orm_mode = True
        from_attributes = True

class ActivityCreate(ActivityBase):

    class Config:
        orm_mode = True
class ActivityUpdate(ActivityBase):

    class Config:
        orm_mode = True