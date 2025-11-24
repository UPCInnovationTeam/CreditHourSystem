from pydantic import BaseModel

class UserBase(BaseModel):
    """
    学工号/姓名/身份（分为管理员/使用者身份）/年级/专业/班级/
    归属学院/注册日期/加入部落的id/参与石光活动的id/第二课堂学时
    """
    uid: str
    name: str
    identity: str
    grade: str
    major: str
    class_: str
    college: str
    tribeId: list[str] =  None
    activityId: list[str] = None
    creditHours: dict[str, int] = None

class UserCreate(UserBase):
    """
    密码/注册时间
    """
    password: str
    registerTime: str
