# 这是一个示例 Python 脚本。
import json
#
import re

import mu2 as mu
import LiteDb
import mydb as db



# 按 ⌃R 执行或将其替换为您的代码。
# 按 双击 ⇧ 在所有地方搜索类、文件、工具窗口、操作和设置。


def input_db():
    #https://github.com/Mondayfirst/XXQG_TiKu/blob/main/%E9%A2%98%E5%BA%93_%E6%8E%92%E5%BA%8F%E7%89%88.json
    #把挑战题库文件导入数据库
    dict_file = open("/Users/zeffect/Downloads/XXQG_TiKu-main/tiku.json")
    dict_d =json.loads(dict_file.read())
    for i in dict_d.items():
        title = i[0]
        print("正在导入："+title)
        right_answer = [i[1]]
        db.addQuestion("单选题", title, json.dumps(right_answer, ensure_ascii=False))

def input_day_question():
    #从网上找到的一份每日答题的JSON，导入数据库
    #感谢https://github.com/dundunnp/hamibot-auto_xuexiqiangguo/issues/133
    json_file = open("/Users/zeffect/Downloads/questions.json")
    dict_d = json.loads(json_file.read())
    for i in dict_d:
        title = i["body"] #题目
        print(title)
        _type_int = i["questionDisplay"] #1单选，2多选，4填空
        _type = ""
        right_answer = []
        j1 = 1
        answer_list = i["answers"]
        for j in i["correct"]:
            option = j["value"]
            answer_id =j["answerId"]
            if _type_int == 1:
                right_answer.append(findStrInOption(answer_list, answer_id))
                _type = "单选题"
            elif _type_int == 2:
                right_answer.append(findStrInOption(answer_list, answer_id))
                _type = "多选题"
            elif _type_int == 4:
                _type = "填空题"
                right_answer.append(option)
            j1 += 1
        print(right_answer)
        print("-----------")
        db.addQuestion(_type, title, json.dumps(right_answer, ensure_ascii=False))

def findStrInOption(answer_list,answerid):
    for i in answer_list:
        if i["answerId"] == answerid:
            return i["content"]
    return ""
def print_hi(name):
    # 在下面的代码行中使用断点来调试脚本。
    print(f'Hi, {name}')  # 按 ⌘F8 切换断点。

def rightCode():
    print("正式程序！")
    mu.init()
    # 启动应用
    if mu.startXuexi():
        need_do = mu.getScroe()
        if need_do[9] == 5:
            for i in range(2):
                mu.fourFight()
        if need_do[10] == 2:
            mu.twoFight()
        if need_do[2] == 5: #234得过分今天就不答了。
            mu.dayQuestion()
        if need_do[3] == 5:
            mu.weekQuesion()
        if need_do[4] == 10:
            mu.specialty_question()
        if need_do[8] == 6:
            mu.challenge_question()
        if need_do[7] > 0:
            mu.click_local()
        if need_do[0] > 0:
            mu.readArticle(need_do[0]/2, need_do[6] > 0, need_do[5] > 0)
        if need_do[1] > 0:
            mu.watchVide(need_do[1])

    # 程序结束

import datetime
import time
import easyocr
import uiautomator2 as u2

def debugCode():
    mu.init()
    # mu.test()
    # while True:
    #     mu.getTipStr()
    mu.startXuexi()
    mu.fourFight()
    # mu.twoFight()
    # mu.dayQuestion()
    # mu.weekQuesion()
    # mu.specialty_question()
    # mu.challenge_question()
    # mu.click_local()
    # mu.readArticle(2, 1, 1)
    # mu.watchVide(1)


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
   # rightCode()
    debugCode()


