from pydantic import BaseModel

class CreditHours(BaseModel):
    # 思想成长
    mentalGrowth_conversion: int
    mentalGrowth: int
    # 创新创业
    innovation_conversion: int
    innovation: int
    # 文体发展
    culturalSports_conversion: int
    culturalSports: int
    # 社会实践与志愿服务
    socialPractice_conversion: int
    socialPractice: int
    # 工作履历与技能培训
    skill_conversion: int
    skill: int
