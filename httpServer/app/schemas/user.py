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
    activityId: dict[str, int] = None   # str是活动id 0 为未开始，1 为签到成功，2 为签退成功
    creditHours: dict[str, int] = None

    class Config:
        orm_mode = True
        from_attributes = True#允许从对象属性中读取数据

class UserCreate(UserBase):
    """
    邮箱/密码/注册时间/验证码
    """
    email: str
    password: str | bytes
    registerTime: str
    code: str

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    """
    用于登录时数据验证
    学工号/密码
    """
    uid: str
    password: str

    class Config:
        orm_mode = True