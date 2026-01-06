from pyecharts.charts import Pie
from pyecharts import options as opts

import requests
import json

class Student:
    def __init__(self,uid,name,identity,grade,major,class_,college,
                 tribeId,activityId,creditHours,lottery_streak):
        self.uid = uid
        self.name = name
        self.identity = identity
        self.grade = grade
        self.major = major
        self.class_ = class_
        self.college = college
        self.tribeId = tribeId
        self.activityId = activityId
        self.creditHours = creditHours
        self.lottery_streak = lottery_streak
    def get_college(self):
        return self.college


def make_authenticated_request(token,
                               api_path="",
                               parameters: dict[str, str] = None,
                               request_body = None,
                               method="POST",
                               url= "http://127.0.0.1:8000",
                               ):
    print("=============>>>")
    url = f"{url}{api_path}"
    # 请求头，包含认证token
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"  # 替换为实际的token
    }

    if parameters:
        # 处理查询参数 - 修复URL参数拼接
        separator = "&" if "?" in url else "?"
        for key, value in parameters.items():
            url += f"{separator}{key}={value}"
            separator = "&"
    print(f"请求的url为{url}")

    # 请求体JSON数据
    data = request_body

    try:
        response = None
        if method == "POST":
            # 发送POST请求
            response = requests.post(url, headers=headers, data=json.dumps(data))
        elif method == "GET":
            # 发送GET请求
            response = requests.get(url, headers=headers)

        # 检查响应状态
        if response.status_code == 200:
            print("请求成功")
            print("响应内容:", response.json())
            print("=============<<<")
            return response.json()
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print("错误信息:", response.text)
            print("=============<<<")

    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {e}")
        print("=============<<<")

if __name__ == "__main__":
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyNTA5MDUwMjAyIiwiZXhwIjoxNzY3NzE5MTExfQ.kwe_PnBjPkWBv5Wh_GpjQWWC__4b_LMonbPN5xsfLP8"
    r = make_authenticated_request(token,
                               api_path=f"/api/v1/record/daily-active-users-list",
                               method="GET",)
    students = []
    for i in r["active_users"]:
        tmp = make_authenticated_request(token,
                                         parameters={"uid":i},
                                         api_path=f"/api/v1/user/search",
                                         method="GET")
        tmp_student_object = Student(**tmp)
        # print(tmp_student_object.get_college())
        students.append(tmp_student_object)
    colleges = {}
    for i in students:
        if i.get_college() in colleges:
            colleges[i.get_college()] += 1
        else:
            colleges[i.get_college()] = 1
    # print(colleges)
    # 模拟数据
    colleges = {"软件学院": 10, "经济管理学院": 20, "法学院": 30, "物理与电子学院": 40, "生命科学学院": 50}

    pie = (
        Pie()
        .add("", data_pair=list(colleges.items()), radius=["40%", "75%"])
        .set_global_opts(title_opts=opts.TitleOpts(title="使用人员分析"))
        .set_series_opts(label_opts=opts.LabelOpts(font_size=18, font_family="KaiTi"))
    )
    pie.render("pie.html")  # 生成 HTML 文件，直接打开即可