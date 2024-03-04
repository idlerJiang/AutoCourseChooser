import os
import re
import webbrowser
from time import sleep

import requests
from lxml import html
from bs4 import BeautifulSoup
import pandas as pd

# 登录

login_url = "https://oauth.shu.edu.cn/login/eyJ0aW1lc3RhbXAiOjE2OTIxNzM4NjExMjk3ODQ5NTcsInJlc3BvbnNlVHlwZSI6ImNvZGUiLCJjbGllbnRJZCI6InlSUUxKZlVzeDMyNmZTZUtOVUN0b29LdyIsInNjb3BlIjoiIiwicmVkaXJlY3RVcmkiOiJodHRwOi8veGsuYXV0b2lzcC5zaHUuZWR1LmNuL3Bhc3Nwb3J0L3JldHVybiIsInN0YXRlIjoiIn0="
term_select_url = "http://xk.autoisp.shu.edu.cn/Home/TermSelect"
class_select_url = "http://xk.autoisp.shu.edu.cn/CourseSelectionStudent/CourseSelectionSave"
class_return_url = "http://xk.autoisp.shu.edu.cn/CourseReturnStudent/CourseReturnSave"
class_search_url = "http://xk.autoisp.shu.edu.cn/StudentQuery/QueryCourseList"
schedule_url = "http://xk.autoisp.shu.edu.cn/StudentQuery/QueryCourseTablePrint"
user_data = {
    "username": "21122793",
    "password": "??????"
}


def login(session_requests):
    try:
        return session_requests.post(login_url, data=user_data, headers=dict(referer=login_url))
    except Exception as e:
        print("101 出现错误：", e)
        return None


def chooseTerm(session_requests, result):
    try:
        print("----- 请选择选课学期 -----")
        # 提取学期名称和值
        html_data = result.text
        soup = BeautifulSoup(html_data, 'html.parser')
        term_rows = soup.find_all('tr', attrs={'name': 'rowterm'})
        for term_row in term_rows:
            term_name = term_row.find('td').get_text(strip=True)
            term_value = term_row.get('value')
            print("学期:", term_name, end='\t')
            print("代码:", term_value)
        print("请输入学期代码：", end=' ')
        term = input()
        term_data = {"termId": term}
        result = session_requests.post(term_select_url, data=term_data, headers=dict(referer=term_select_url))
        if result.text.find("选课学期不存在或未开启选课") != -1:
            print("选课学期不存在！")
            return False
        else:
            print("选课学期选择成功！")
            return True
    except Exception as e:
        print("201 出现错误：", e)
        return False

def showMenu():
    print("-----------")
    print("1 = 查询课程并选课")
    print("2 = 课程号+教师号选课")
    print("3 = 查询课表")
    print("4 = 课程号退课")
    print("9 = 自动选课")
    print("输入其他以退出")

def main():
    print("开始运行")
    session_requests = requests.session()

    # 1 登录
    try:
        result = login(session_requests)
        if result.text.find("点击选择选课学期") != -1:
            print("登陆成功！")
        else:
            print("102 登陆失败，请检查代码！")
            exit(0)
    except Exception as e:
        print("103 登陆失败，请检查代码！")
        exit(0)


    # 2 选择选课学期
    try:
        while True:
            if chooseTerm(session_requests, result):
                break
    except Exception as e:
        print("202 登陆失败，请检查代码！")
        exit(0)

    while True:
        sleep(0.5)
        showMenu()
        choice = input()
        if choice == '1':
            while True:
                print("-----------")
                pageNum = 1
                try:
                    print("请输入以下内容，回车以跳过，全部回车以退出")
                    courseID = input("课程号：")
                    courseName = input("课程名：")
                    teacherID = input("教师号：")
                    teacherName = input("教师名：")
                except:
                    continue
                if courseID == "" and courseName == "" and teacherID == "" and teacherName == "":
                    break
                while True:
                    print("-----------")
                    search_option = {
                        "PageIndex": pageNum, "PageSize": "30", "FunctionString": "Query",
                        "CID": courseID, "CourseName": courseName, "IsNotFull": "false",
                        "CourseType": "B", "TeachNo": teacherID, "TeachName": teacherName,
                        'Enrolls': "", "Capacity1": "", "Capacity2": "", "CampusId": "",
                        'CollegeId': "", "Credit": "", "TimeText": ""
                    }
                    result = session_requests.post(class_search_url, data=search_option,
                                                   headers=dict(referer=class_search_url))
                    html_data = result.text
                    data = pd.read_html(html_data)
                    print(data[0])
                    print(data[0]['上课时间'])
                    try:
                        pageNum = int(input("请输入跳转页码(-1 = 退出, 0 = 选课)："))
                        if pageNum == -1:
                            break
                        elif pageNum == 0:
                            chooseID = int(input("请输入课程前的序号："))
                            chooseCourseID = data[0]["课程号"][chooseID]
                            chooseTeacherName = data[0]["教师号"][chooseID]
                            result = session_requests.post(class_select_url,
                                                           data={"cids": chooseCourseID, "tnos": chooseTeacherName})
                            if result.text.find("选课成功") != -1:
                                print("选课成功！")
                            else:
                                print("选课失败！")
                            # print(result.text)
                    except:
                        print("输入有误！")
                        pageNum = 1
                        continue

        elif choice == '2':
            while True:
                print("-----------")
                print("选课中，输入有误将会退出")
                try:
                    courseID = input("课程号：")
                    teacherID = input("教师号：")
                except:
                    print("输入有误！")
                    break
                result = session_requests.post(class_select_url, data={"cids": courseID, "tnos": teacherID})
                if result.text.find("选课成功") != -1:
                    print("选课成功！")
                else:
                    print("选课失败！")
        elif choice == '3':
            print("-----------")
            try:
                result = session_requests.get(schedule_url).text
                # print(str(result))
                with open("schedule.html", mode="w", encoding="utf-8") as file:
                    file.write(result)
                webbrowser.open_new_tab('schedule.html')
            except:
                print("出错了！")
                continue
        elif choice == '4':
            while True:
                print("-----------")
                print("退课中，输入有误将会退出")
                try:
                    courseID = input("课程号：")
                    teacherID = input("教师号：")
                except:
                    print("输入有误！")
                    break
                result = session_requests.post(class_return_url, data={"cids": courseID, "tnos": teacherID})
                if result.text.find("退课成功") != -1:
                    print("退课成功！")
                else:
                    print("退课失败！")
        elif choice == '9':
            print("----------")
            print("读取auto.txt并自动选课")
            courseID = []
            teacherID = []
            with open("auto.txt", mode="r", encoding="utf-8") as file:
                leng = int(file.readline().strip('\n'))
                print("预计读取", leng, "个课程信息")
                for i in range(leng):
                    courseID.append(file.readline().strip('\n'))
                    teacherID.append(file.readline().strip('\n'))
                    print(i, "课程号：", courseID[i], "教师号：", teacherID[i])
            try:
                n = 0
                while True:
                    for i in range(leng):
                        print("-----------")
                        search_option = {
                            "PageIndex": "1", "PageSize": "30", "FunctionString": "Query",
                            "CID": courseID[i], "CourseName": "", "IsNotFull": "false",
                            "CourseType": "B", "TeachNo": teacherID[i], "TeachName": "",
                            'Enrolls': "", "Capacity1": "", "Capacity2": "", "CampusId": "",
                            'CollegeId': "", "Credit": "", "TimeText": ""
                        }
                        result = session_requests.post(class_search_url, data=search_option,
                                                       headers=dict(referer=class_search_url))
                        html_data = result.text
                        data = pd.read_html(html_data)
                        print("课程号\t教师号\t容量\t人数", )
                        print(courseID[i], teacherID[i], ' ', data[0]["容量"][0], ' ', data[0]["人数"][0])
                        if int(data[0]["人数"][0]) < int(data[0]["容量"][0]):
                            print("人数未满，尝试选课！")
                            result = session_requests.post(class_select_url,
                                                           data={"cids": ('' + courseID[i]),
                                                                 "tnos": ('' + teacherID[i])})
                            if result.text.find("选课成功") != -1:
                                print("选课成功！已从选课列表中删除")
                                courseID.remove(courseID[i])
                                teacherID.remove(teacherID[i])
                                leng -= 1
                                if leng == 0:
                                    raise KeyboardInterrupt
                            else:
                                print("选课失败！")
                        else:
                            print("人数已满，无法选课！")
                        sleep(3)
                    n += 1
                    print("已经执行", n, "轮")
            except KeyboardInterrupt:
                print("已中断自动选课！")
            except Exception as e:
                print("发生错误：", e)


if __name__ == "__main__":
    main()
