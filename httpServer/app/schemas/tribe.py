from pydantic import BaseModel

class TribeBase(BaseModel):
    """
    id/名称/所属学院/管理员/成员/活动ID
    """
    uid : str
    name : str
    college : str
    manager : list[str]
    members : list[str]
    activityID : list[str]

    class Config:
        orm_mode = True

class TribeCreate(TribeBase):
    pass