from pydantic import BaseModel

class TribeBase(BaseModel):
    """
    id/名称/所属学院/管理员/成员/活动内容
    """
    uid : str
    name : str
    college : str
    manager : str
    member : list[str]
    activityContent : str

    class Config:
        orm_mode = True

class TribeCreate(TribeBase):
    pass