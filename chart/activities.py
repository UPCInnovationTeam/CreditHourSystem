from pyecharts.charts import Pie, Line, Tab
from pyecharts import options as opts

import requests
import json

from config import url, token
from main import make_authenticated_request, Student

class Activity:
    def __init__(self,
                 uid,
                 registerTime,
                 registrationStratTime,
                 registrationEndTime,
                 activityStratTime,
                 activityEndTime,
                 maxParticipants,
                 currentParticipants,
                 participantsIDs,
                 title,
                 content,
                 publisher,
                 imageUrl,
                 college,
                 gradeRestrictions,
                 collegeRestrictions,
                 tribeRestrictions,
                 status,
                 creditClass,
                 creditHours):
        self.uid = uid
        self.registerTime = registerTime
        self.registrationStratTime = registrationStratTime
        self.registrationEndTime = registrationEndTime
        self.activityStratTime = activityStratTime
        self.activityEndTime = activityEndTime
        self.maxParticipants = maxParticipants
        self.currentParticipants = currentParticipants
        self.participantsIDs = participantsIDs
        self.title = title
        self.content = content
        self.publisher = publisher
        self.imageUrl = imageUrl
        self.college = college
        self.gradeRestrictions = gradeRestrictions
        self.collegeRestrictions = collegeRestrictions
        self.tribeRestrictions = tribeRestrictions
        self.status = status
        self.creditClass = creditClass
        self.creditHours = creditHours
    def get_title(self):
        return self.title

def analyse_activity_participation_college_distribution(id_ = 1) -> Pie:
    r = make_authenticated_request(token,
                                   parameters={"id_": id_},
                                   api_path=f"/api/v1/activity/id",
                                   method="GET", )

    r["participantsIDs"] : list[str]
    students = [make_authenticated_request(token,
                                           parameters={"uid": i},
                                           api_path=f"/api/v1/user/search",
                                           method="GET") for i in r["participantsIDs"]]
    # print(students)
    students_object = [Student(**i) for i in students]
    colleges = {}
    for i in students_object:
        if i.get_college() in colleges:
            colleges[i.get_college()] += 1
        else:
            colleges[i.get_college()] = 1

    pie = (
        Pie()
        .add("", data_pair=list(colleges.items()), radius=["40%", "75%"])
        .set_global_opts(title_opts=opts.TitleOpts(title=f"{r["title"]}参与者学院分布"))
        .set_series_opts(label_opts=opts.LabelOpts(font_size=18, font_family="KaiTi"))
    )
    return pie

def get_activities_id_list() -> list[int]:
    r : list[int]= make_authenticated_request(token,
                                   parameters= {"position" : "0"},
                                   api_path="/api/v1/activity/fetch_20",
                                   method="GET",)
    return r

if __name__ == "__main__":
    # pie = analyse_activity_participation_college_distribution()
    ls : list[Activity] = [Activity(**make_authenticated_request(token,parameters={"id_": i},
                                   api_path=f"/api/v1/activity/id",
                                   method="GET",)) for i in get_activities_id_list()]
    # 使用 Tab 组件组合图表
    tab = Tab()

    # 循环创建图表
    tabs = [analyse_activity_participation_college_distribution(i.uid) for i in ls]
    for i in range(len(tabs)):
        tab.add(tabs[i], f"{ls[i].get_title()}")

    tab.render(path = "index2.html")
    # tab.add(pie, "使用者学院分布")

     # pie.render(path = "1.html")