from pyecharts.charts import Pie, Line, Tab
from pyecharts import options as opts

import requests
import json

from config import url, token

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
                               _url= url,
                               ):
    print("=============>>>")
    _url = f"{_url}{api_path}"
    # 请求头，包含认证token
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"  # 替换为实际的token
    }

    if parameters:
        # 处理查询参数 - 修复URL参数拼接
        separator = "&" if "?" in _url else "?"
        for key, value in parameters.items():
            _url += f"{separator}{key}={value}"
            separator = "&"
    print(f"请求的url为{_url}")

    # 请求体JSON数据
    data = request_body

    try:
        response = None
        if method == "POST":
            # 发送POST请求
            response = requests.post(_url, headers=headers, data=json.dumps(data))
        elif method == "GET":
            # 发送GET请求
            response = requests.get(_url, headers=headers)

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

def analyze_college_distribution() -> Pie:
    r = make_authenticated_request(token,
                                   api_path=f"/api/v1/record/daily-active-users-list",
                                   method="GET", )
    students = []
    for i in r["active_users"]:
        tmp = make_authenticated_request(token,
                                         parameters={"uid": i},
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
    return pie

def analyze_recent_daily_stats_line() -> Line:
    r = make_authenticated_request(token,
                                   api_path="/api/v1/record/recent-daily-stats",
                                   method="GET")
    # print(r)
    # 模拟数据
    r["stats_list"] = [
        {'stat_date': '2026-01-06', 'dau_count': 3, 'new_users_count': 6},
        {'stat_date': '2026-01-07', 'dau_count': 2, 'new_users_count': 6},
        {'stat_date': '2026-01-08', 'dau_count': 5, 'new_users_count': 6},
        {'stat_date': '2026-01-09', 'dau_count': 8, 'new_users_count': 6},
        {'stat_date': '2026-01-10', 'dau_count': 2, 'new_users_count': 6},
        {'stat_date': '2026-01-11', 'dau_count': 10, 'new_users_count': 6},
    ]

    print(r["stats_list"])
    r["stats_list"] : list[dict]
    date_list = [i["stat_date"] for i in r["stats_list"]] # 日期
    # print(date_list)
    dau_count = [i["dau_count"] for i in r["stats_list"]] # 日活数

    line = (
        Line()
        .add_xaxis(date_list)
        .add_yaxis("", dau_count)
        .set_global_opts(
            title_opts=opts.TitleOpts(title="日活"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
            toolbox_opts=opts.ToolboxOpts(),

            yaxis_opts=opts.AxisOpts(),
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(is_show=True),
            linestyle_opts=opts.LineStyleOpts(width=2)
        )
    )
    return line


if __name__ == "__main__":
    line = analyze_recent_daily_stats_line()
    pie = analyze_college_distribution()


    # 使用 Tab 组件组合图表
    tab = Tab()
    tab.add(pie, "使用者学院分布")
    tab.add(line, "日在线人数")

    # 渲染到同一个HTML文件
    tab.render(path = "index.html")