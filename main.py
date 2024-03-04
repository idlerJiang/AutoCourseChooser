import json
import tkinter

import pandas as pd
import html5lib
import ttkbootstrap as ttk

from bs4 import BeautifulSoup
from selenium import webdriver
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from info import *

global MAIN_URL, LOGIN_URL, TERM_DISPLAY_URL, TERM_SELECT_URL, QUERY_COURSE_URL, RETURN_COURSE_URL, RANK_URL
global CONFIG

MAIN_URL = "http://xk.shu.edu.cn"
TERM_DISPLAY_URL = "http://xk.autoisp.shu.edu.cn/Home/TermIndex"
TERM_SELECT_URL = "http://xk.autoisp.shu.edu.cn/Home/TermSelect"
QUERY_COURSE_URL = "http://xk.autoisp.shu.edu.cn/CourseSelectionStudent/QueryCourseCheck"
RETURN_COURSE_URL = "http://xk.autoisp.shu.edu.cn/CourseReturnStudent/CourseReturn"
RANK_URL = "http://xk.autoisp.shu.edu.cn/StudentQuery/QueryEnrollRank"


# 1 = Log+, 2 = Warning+, 3 = Error

def get_login_URL(session_requests):
    global MAIN_URL, LOGIN_URL
    data = session_requests.post(MAIN_URL)
    LOGIN_URL = "https://oauth.shu.edu.cn/login/" + data.text.split("action=\"/login/")[1].split("\"")[0]
    log("loginURL = " + LOGIN_URL)


def load_json():
    global CONFIG
    try:
        with open('config.json', 'r') as file:
            CONFIG = json.load(file)
    except Exception as e:
        CONFIG = {}
        error("Error While Load JSON: " + str(e))


def save_json():
    global CONFIG
    try:
        with open('config.json', 'w') as file:
            json.dump(CONFIG, file)
    except Exception as e:
        error("Error While Save JSON: " + str(e))


def login(session_requests):
    global TERM_DISPLAY_URL

    session_requests.cookies["ASP.NET_SessionId"] = CONFIG["sessionID"]
    data = session_requests.post("http://xk.shu.edu.cn/")
    # print(data.text)
    if data.text.find("安全退出") != -1:
        log("Login By JSON Config")
        return
    else:
        warn("Login By JSON Config Failed")

    options = webdriver.EdgeOptions()
    # options.add_argument('headless')
    driver = webdriver.Edge(options=options)
    # 打开网页并填写表单
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, timeout=3)
    wait.until(lambda d: driver.find_element(By.ID, "username").is_displayed())
    driver.find_element(By.ID, "username").send_keys("??????")
    driver.find_element(By.ID, "password").send_keys("??????")
    driver.find_element(By.ID, "submit-button").click()
    if driver.find_element(By.NAME, "rowterm"):
        log("Login by Username and Password")
    else:
        error("Login by Username and Password Failed")
        exit(0)
    SessionId = driver.get_cookie("ASP.NET_SessionId")["value"]
    CONFIG["sessionID"] = SessionId
    session_requests.cookies["ASP.NET_SessionId"] = SessionId
    log("SessionId = " + SessionId)
    # 关闭浏览器
    driver.close()
    driver.quit()


def window_choose_term(term_rows):
    choice = 0

    def button_choose_term(param):
        nonlocal choice
        window.destroy()
        choice = param

    window = ttk.Window(themename='lumen')
    window.title("请选择选课学期")
    window.geometry('%dx%d+%d+%d' % (400, 400, 100, 100))  # %dx%d宽度x 高度+横向偏移量(距左边)+纵向偏移量(距上边)
    ttk.Label(window, text="请选择选课学期", font=('黑体', 20)).place(anchor="center", x=200, y=50)
    count = 1
    for term_row in term_rows:
        term_name = term_row.find('td').get_text(strip=True)
        term_value = term_row.get('value')
        ttk.Button(window, text=term_name, command=lambda: button_choose_term(term_value)
                   ).place(anchor="center", x=200, y=25 + count * 100)
    window.mainloop()
    return choice


def select_term(session_requests):
    global TERM_DISPLAY_URL, TERM_SELECT_URL
    data = session_requests.post(TERM_DISPLAY_URL)
    html_data = data.text
    soup = BeautifulSoup(html_data, 'html.parser')
    term_rows = soup.find_all('tr', attrs={'name': 'rowterm'})
    term_value = 0
    for term_row in term_rows:
        term_name = term_row.find('td').get_text(strip=True)
        term_value = term_row.get('value')
        log("学期: " + term_name + ", 代码: " + term_value)
    if len(term_rows) != 1:
        print(term_rows)
        term_value = window_choose_term(term_rows)
    log("Choose TermID " + str(term_value))
    data = session_requests.post(TERM_SELECT_URL, data={"termId": term_value}, headers=dict(referer=TERM_SELECT_URL))
    print(data.text)


def query_course(session_requests,
                 PageIndex='1', CID='', CourseName='', IsNotFull='', TeachNo='', TeachName='', Enrolls='',
                 Capacity1='', Capacity2='', CampusId='', CollegeId='', Credit='', TimeText=''):
    global QUERY_COURSE_URL
    query_option = {
        "PageIndex": PageIndex, "PageSize": "30", "FunctionString": "Query", "CID": CID, "CourseName": CourseName,
        "IsNotFull": IsNotFull, "CourseType": "B", "TeachNo": TeachNo, "TeachName": TeachName, 'Enrolls': Enrolls,
        "Capacity1": Capacity1, "Capacity2": Capacity2, "CampusId": CampusId, 'CollegeId': CollegeId, "Credit": Credit,
        "TimeText": TimeText
    }
    log("Try to Query by Using " + str(query_option))
    data = session_requests.post(QUERY_COURSE_URL, data=query_option, headers=dict(referer=QUERY_COURSE_URL))
    data = pd.read_html(data.text)
    print(data[0])


def add_course(session_requests):
    pass


def return_course(session_requests):
    pass


def show_rank(session_requests):
    pass


def change_course(session_requests):
    def add():
        pass

    def remove():
        pass

    def try_change():
        pass

    window = ttk.Window(themename='sandstone')
    window.title("SHU-ACC By摸鱼老手")
    window.geometry('%dx%d+%d+%d' % (400, 600, 100, 100))  # %dx%d宽度x 高度+横向偏移量(距左边)+纵向偏移量(距上边)
    window.resizable(False, False)
    ttk.Label(window, text="待操作课程列表", font=('黑体', 20)).place(anchor="center", x=200, y=50)

    listbox = tkinter.Listbox(window)
    listbox.place(anchor="center", x=200, y=250, width=300, height=300)

    change_course_list = []

    try:
        with open('换课.txt', 'r') as file:
            lines = file.readlines()
        for line in lines:
            line = line.split(";")
            from_course, from_teacher = line[0].split(":")
            to_course, to_teacher = line[1].split(":")
            change_course_list.append((from_course, from_teacher, to_course, to_teacher))
            listbox.insert("end", each_course[0] + "\n" + each_course[1])
    except Exception as e:
        error("Error While Load in change_course(): " + str(e))

    tkinter.Button(window, text="-", font=('黑体', 20), command=lambda: remove()) \
        .place(anchor="center", x=90, y=450, width=80, height=50)
    tkinter.Button(window, text="保存", font=('黑体', 10), command=lambda: remove()) \
        .place(anchor="center", x=200, y=450, width=100, height=50)
    tkinter.Button(window, text="+", font=('黑体', 20), command=lambda: add()) \
        .place(anchor="center", x=310, y=450, width=80, height=50)
    tkinter.Button(window, text="返回", font=('黑体', 10), command=window.destroy) \
        .place(anchor="center", x=120, y=525, width=140, height=50)
    tkinter.Button(window, text="下一步", font=('黑体', 10), command=lambda: try_change()) \
        .place(anchor="center", x=280, y=525, width=140, height=50)

    window.mainloop()


def init_menu(session_requests):
    window = ttk.Window(themename='sandstone')
    window.title("SHU-ACC By摸鱼老手")
    window.geometry('%dx%d+%d+%d' % (400, 600, 100, 100))  # %dx%d宽度x 高度+横向偏移量(距左边)+纵向偏移量(距上边)

    tkinter.Button(window, text="选课", command=lambda: add_course(session_requests), width=30, height=2).place(
        anchor="center", x=200, y=100)
    tkinter.Button(window, text="退课", command=lambda: return_course(session_requests), width=30, height=2).place(
        anchor="center", x=200, y=200)
    tkinter.Button(window, text="查看课表与排名", command=lambda: show_rank(session_requests), width=30,
                   height=2).place(anchor="center", x=200, y=300)
    tkinter.Button(window, text="自动退换课", command=lambda: change_course(session_requests), width=30,
                   height=2).place(
        anchor="center", x=200, y=400)
    tkinter.Button(window, text="退出", command=lambda: exit(0), width=30, height=2).place(anchor="center", x=200,
                                                                                           y=500)
    window.mainloop()


if __name__ == '__main__':
    session_requests = requests.session()
    get_login_URL(session_requests)
    load_json()
    # CONFIG["logLevel"] = 1
    login(session_requests)
    save_json()
    select_term(session_requests)
    query_course(session_requests, CID="00000000")
    # init_menu(session_requests)
    # change_course(None)
