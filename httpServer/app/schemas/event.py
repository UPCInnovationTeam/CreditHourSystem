from pydantic import BaseModel

class EventBase(BaseModel):
    """
    id/注册时间/报名开始时间/报名结束时间/活动开始时间/活动结束时间/
    限制报名人数/报名人数/报名人的id/活动标题/活动内容/活动发布者/
    活动管理员/活动图片地址/活动归属方/活动限制条件（年级/学院/部落）
    """
    uid  : str
    registerTime: str
    signUpStartTime: str
    signUpEndTime: str
    eventStartTime: str
    eventEndTime: str
    limitNum: int
    participantNum: int
    participantId: list[str]
    title: str
    content: str
    publisherId: str
    adminId: list[str]
    imgUrl: str
    college: str
    condition: dict[str, str] = None
    status: str


    #Pydantic 模型配置类，开启ORM模式，允许从ORM对象中读取数据
    class Config:
        orm_mode = True


