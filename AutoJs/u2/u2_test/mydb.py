from LiteDb import LiteDb

_db = LiteDb()
_db.openDb('data.db')  # 数据库

def init():
    #表是否创建
    #查询表是否存在！table_read_page
    _db.createTables("create table if not exists table_read_page(title text,device text)")
    _db.createTables("create table if not exists table_question(type text,question text,answer text)")
#这个标题有没有看过
def isRead(title,device):
    result = _db.executeSql("select count(title) from table_read_page  where title='"+title+"' and device = '"+device+"'")
    return result[1][0][0] > 0

#没看过就添加到数据库
def addRead(title,device):
    _db.executeSql("insert into table_read_page(title,device) values('"+title+"','"+device+"')")

def hasQuesion(type,left_ques):
    return _db.executeSql("select type,answer from table_question where type ='"+type+"' and question like '%"+left_ques+"%'")

def hasChangeQuestion(title):
    #指名要搜索挑战题
    return _db.executeSql(
        "select type,answer from table_question where question like '%" + title + "%'")

def hasAnswerChang(answer):
    #搜索答案在数据库里有没有
    return _db.executeSql(
        "select type,answer from table_question where answer like '%" + answer + "%'")

#添加答题到题库
def addQuestion(type,ques, answe): #都是存入的数组 ["答案1","答案2"]  挑战答题就是单选题
    _result = hasQuesion(type, ques)
    inSql = len(_result[1]) > 0
    if not inSql:
        _db.executeSql("insert into table_question(type,question,answer) values('"+type+"','"+ques+"','"+answe+"')")