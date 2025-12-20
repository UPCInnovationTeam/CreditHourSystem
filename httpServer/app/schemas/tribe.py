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

    #Pydantic 模型配置类，开启ORM模式，允许从ORM对象中读取数据
    class Config:
        orm_mode = True

#用于创建部落时的数据验证
class TribeCreate(TribeBase):
    pass
    #没有额外的字段，直接继承父类的字段