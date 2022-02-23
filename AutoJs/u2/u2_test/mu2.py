import json
import random
import string

import uiautomator2 as u2
import time
import sys
import datetime
import mydb as db
import easyocr

d = u2.connect()
_reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)  #
_today = time.strftime("%Y-%m-%d", time.localtime())  # 今天的日期，用于匹配今天的文章
_readTime = 70  # 阅读文章的时间
_randomReadTitle = ["推荐", "要闻", "新思想", "综合"]
_commentText = ["支持党，支持国家！", "为实现中华民族伟大复兴而不懈奋斗！", "不忘初心，牢记使命", "为实现中华民族伟大复兴而不懈奋斗！"]  # 评论内容，可自行修改，大于5个字便计分
_lastComment = ""
_shareCount = 0.0
_commentCount = 0.0

import easyocr


def init():
    log("正在初始化……")
    db.init()
    # d.healthcheck()
    # reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)  # this needs to run only once to load the model into memory
    # d.show_float_window()


def log(txt):
    print(txt)
    if isinstance(txt,str):
        d.toast.show(str(txt), 0.5)
    return


# 用于输出调试日志
def debug(txt):
    print(txt)
    if isinstance(txt,str):
        d.toast.show(str(txt), 0.5)
    return


def waitForGone(uiobj, des="指定名称"):
    # 等待一个元素不存在
    while uiobj.exists:
        time.sleep(1)
        log("存在《" + des + "》元素，正在等待元素隐藏，请等待！")
    return uiobj


def waitFor(uiobj, des="指定名称"):
    # 等待一个元素出现
    while not uiobj.exists:
        time.sleep(1)
        log("未找到《" + des + "》元素，请等待！")
    return uiobj


def startXuexi():
    log("点击Home键，延时2秒！")
    d.press("home")
    time.sleep(2)
    log("启动学习强国！延时5秒，请等待！")
    d.app_start("cn.xuexi.android")
    # 一定要进入主页页面，否则不往下执行
    while not d(resourceId="cn.xuexi.android:id/comm_head_xuexi_mine").exists():
        time.sleep(1)
        d(resourceId="cn.xuexi.android:id/parentPanel").child(resourceId="android:id/button2").click_exists()
        if (d(resourceId="cn.xuexi.android:id/login_pwd_input_bg").exists()):
            return False
        d(text="暂不更新").click_exists()  # 更新按钮存在即关闭
        log("延时1秒，继续查找，直到找到我的")
    return True


def click_local():
    # 本地频道
    my_lable = d(resourceId="cn.xuexi.android:id/comm_head_xuexi_mine")
    while not my_lable.exists():
        debug("不在主页,先等待看，可以手动进入主页……")
        time.sleep(1)
    d(resourceId="cn.xuexi.android:id/home_bottom_tab_button_work").click()
    d.sleep(1)
    refresh_view = d.xpath(
        '//*[@resource-id="cn.xuexi.android:id/view_pager"]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[2]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.ImageView[1]')
    waitForGone(refresh_view)
    debug("正在查找本地频道%……")
    tab_view = d.xpath(
        '//*[@resource-id="cn.xuexi.android:id/view_pager"]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]/android.view.ViewGroup[1]').all()[
        0]
    while not d(text="新思想").exists:  # 如果找不到新思想，一般是滑动到了后面，这里滑动查找
        debug("正在滑动查找本地频道……")
        tab_view.swipe("right")
    zh_parent = d.xpath('//*[@text="新思想"]').all()[0].parent()
    tab_group = zh_parent.parent()
    tab_childs = tab_group.elem.getchildren()
    xsx_index = -1
    for i in range(len(tab_childs)):
        if tab_childs[i] == zh_parent.elem:
            xsx_index = i
    if xsx_index != -1:
        local_parent = d.xpath(d.xpath('//*[@text="新思想"]').all()[
                                   0].parent().parent().get_xpath() + "/android.widget.LinearLayout[" + str(
            xsx_index + 2) + "]").all()[0]
        local_view = d.xpath(local_parent.get_xpath() + "/android.widget.TextView[1]").all()[0]
        location_name = local_view.text
        local_view.click()
        print("本地城市：" + location_name)
        waitForGone(refresh_view)
        while not d(text=location_name + "卫视").exists:
            debug("正在滑动查找" + location_name + "卫视，时间较长，请等待……")
            if not d(text=location_name + "学习平台"):
                d(className="android.widget.ListView", scrollable=True).scroll.to(
                    className="android.support.v7.widget.RecyclerView", scrollable=True)
            d(className="android.widget.ListView", scrollable=True).child(
                className="android.support.v7.widget.RecyclerView", scrollable=True).scroll.horiz.to(
                text=location_name + "卫视")
            d.sleep(1)
        d(text=location_name + "卫视").click()
        waitFor(d(text="中央广播电视总台"), "看电视")
        debug("进入广播界面，放30秒")
        for i in range(30):
            time.sleep(1)
            if i % 5 == 0:
                debug("正在播放广播……还剩" + str(30 - i) + "秒")
        d.press("back")
        d.sleep(1)


def to_scroe():
    waitFor(d(resourceId="cn.xuexi.android:id/ll_comm_head_score"), "积分按钮").click()
    waitFor(d(text="登录"), "积分页面")
    return True


def getScroe():  # 有BUG，有的手机需要滑到控件，才能获取分数
    # 0 读多少文章
    # 1 看视频数量
    # 2 每日答题
    # 3 每周答题
    # 4 专项答题
    # 5 分享
    # 6 发表观点
    # 7 本地频道
    # 8 挑战答题
    # 9 四人赛
    # 10 双人对战
    need_do = []
    if to_scroe():
        d(scrollable=True).scroll.to(text="强国运动")
        # 获取积分.
        need_do.append(12 - int(get_score_from_txt(
            d.xpath('//android.widget.ListView/android.view.View[2]/android.view.View[3]').all()[0])))
        video_num_1 = get_score_from_txt(
            d.xpath('//android.widget.ListView/android.view.View[3]/android.view.View[3]').all()[0])
        video_num_2 = get_score_from_txt(
            d.xpath('//android.widget.ListView/android.view.View[4]/android.view.View[3]').all()[0])
        need_do.append(6 - int(max(video_num_1, video_num_2)))
        # #答题只要得分了，就不做了，不重复进行。
        need_do.append(5 -
                       int(get_score_from_txt(
                           d.xpath('//android.widget.ListView/android.view.View[5]/android.view.View[3]').all()[0])))
        need_do.append(5 -
                       int(get_score_from_txt(
                           d.xpath('//android.widget.ListView/android.view.View[6]/android.view.View[3]').all()[0])))
        need_do.append(10 -
                       int(get_score_from_txt(
                           d.xpath('//android.widget.ListView/android.view.View[7]/android.view.View[3]').all()[0])))
        need_do.append(1 -
                       int(get_score_from_txt(
                           d.xpath('//android.widget.ListView/android.view.View[12]/android.view.View[3]').all()[0])))
        need_do.append(1 -
                       int(get_score_from_txt(
                           d.xpath('//android.widget.ListView/android.view.View[13]/android.view.View[3]').all()[0])))
        need_do.append(1 -
                       int(get_score_from_txt(
                           d.xpath('//android.widget.ListView/android.view.View[14]/android.view.View[3]').all()[0])))
        need_do.append(6 -
                       int(get_score_from_txt(
                           d.xpath('//android.widget.ListView/android.view.View[8]/android.view.View[3]').all()[0])))
        need_do.append(5 -
                       int(get_score_from_txt(
                           d.xpath('//android.widget.ListView/android.view.View[9]/android.view.View[3]').all()[0])))
        need_do.append(2 -
                       int(get_score_from_txt(
                           d.xpath('//android.widget.ListView/android.view.View[10]/android.view.View[3]').all()[0])))
    else:
        need_do = [12, 6, 5, 5, 10, 1, 1, 1, 6, 5, 2]
    debug(need_do)
    while d(text="成长总积分").exists:
        d.press("back")
        d.sleep(0.5)
    learn_scroe = d(resourceId="cn.xuexi.android:id/user_item_name", text="学习积分")
    while learn_scroe.exists:
        d.press("back")
        d.sleep(0.5)
    return need_do


def get_score_from_txt(uis):
    # while not visable_to_user(uis):
    #     d.swipe_ext("up")
    text = uis.info.get("text")
    log("分数：" + text)
    return text[2:index_of_str(text, "分")[0]:]


def challenge_question():
    # 挑战答题，有几个特别的地方：1. 选择正确的……就是题目中相同，要从答案中选择正确的词
    waitFor(d(resourceId="cn.xuexi.android:id/comm_head_xuexi_mine"), "主页").click()
    waitFor(d(resourceId="cn.xuexi.android:id/user_item_name", text="我要答题"), "我要答题").click()
    waitFor(d.xpath('//*[@resource-id="app"]/android.view.View[1]/android.view.View[3]/android.view.View[11]'),
            "挑战答题").click()
    maxAnswer = 7
    rightNum = 0
    while True:
        waitFor(d(className='android.widget.ListView'), "选项列表")
        title = d(className='android.widget.ListView').sibling(className="android.view.View").get_text()
        log("题目：" + title)
        _result = None
        if title.startswith("选择"):
            answer_str = ""
            for el in d(className="android.widget.RadioButton"):
                option = el.sibling(className="android.view.View").get_text()
                answer_str = answer_str + "|" + option
            _result = db.hasChangeQuestion(answer_str)
        else:
            _result = db.hasChangeQuestion(title)
        inSql = len(_result[1]) > 0
        right_answer = "###"  # 代表选择A
        if inSql:
            _result_json = json.loads(_result[1][0][1])
            right_answer = _result_json[0]
        for el in d(className="android.widget.RadioButton"):
            option = el.sibling(className="android.view.View").get_text()
            if right_answer == option or right_answer == "###" or rightNum > maxAnswer:
                el.click()
                d.sleep(1)
                break
        log("延时5秒，检查是否答对！")
        d.sleep(5)
        # d(text="v5IOXn6lQWYTJeqX2eHuNcrPesmSud2JdogYyGnRNxujMT8RS7y43zxY4coWepspQkvwRDTJtCTsZ5JW+8sGvTRDzFnDeO+BcOEpP0Rte6f+HwcGxeN2dglWfgH8P0C7HkCMJOAAAAAElFTkSuQmCC")
        if d(text="v5IOXn6lQWYTJeqX2eHuNcrPesmSud2JdogYyGnRNxujMT8RS7y43zxY4coWepspQkvwRDTJtCTsZ5JW+8sGvTRDzFnDeO+BcOEpP0Rte6f+HwcGxeN2dglWfgH8P0C7HkCMJOAAAAAElFTkSuQmCC").exists:
            # 答错了
            if rightNum > maxAnswer:
                d.press("back")
                waitFor(d(text="生成分享图"), "生成分享图")
                log("已结束，返回主页")
                d.press("back")
                d.sleep(2)
                d.press("back")
                d.sleep(2)
                d.press("back")
                d.sleep(2)
                break
            if d(text="分享就能复活").exists:
                d(text="分享就能复活").click()
                d.sleep(2)
                d.press("back")
        elif d(text="生成分享图").exists:
            # 已结束
            log("已结束，返回主页")
            d.press("back")
            d.sleep(2)
            d.press("back")
            d.sleep(2)
            d.press("back")
            d.sleep(2)
            break
        else:
            rightNum += 1


def readArticle(count, need_comment=None, need_share=None):
    # 阅读文章
    log("---------------------------执行阅读文章程序！")
    while not d(resourceId="cn.xuexi.android:id/comm_head_xuexi_mine").exists():
        debug("不在主页，重试中……可手动进入启动页面")
        d.sleep(1)
    d(resourceId="cn.xuexi.android:id/home_bottom_tab_button_work").click_exists(3)
    d.sleep(1)
    d.xpath(
        '//*[@resource-id="cn.xuexi.android:id/view_pager"]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[2]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.ImageView[1]').wait_gone()
    # 阅读文章时，在推荐，要闻，新思想和综合随机选择
    tmpRandomTitle = _randomReadTitle[random.randint(0, len(_randomReadTitle) - 1)]
    while not d(text=tmpRandomTitle).exists:
        log("未找到关键字：" + tmpRandomTitle + ",再次随机生成中……")
        tmpRandomTitle = _randomReadTitle[random.randint(0, len(_randomReadTitle) - 1)]
    d(text=tmpRandomTitle).click_exists(3)
    d.sleep(1)
    d.xpath(
        '//*[@resource-id="cn.xuexi.android:id/view_pager"]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[2]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.ImageView[1]').wait_gone()
    tmpreadcount = 0
    upNum = 0
    while tmpreadcount < count:
        # //*[@text="筑铜墙铁壁 护国泰民安——2021“最美基层民警”群像（下）"]
        findEl = d(resourceId="cn.xuexi.android:id/general_card_title_id", className="android.widget.TextView")
        while len(findEl) == 0:
            d.swipe_ext("up")
            upNum += 1
            log("正在上滑查找……")
            if upNum > 20:
                break
            time.sleep(2)
            findEl = d(resourceId="cn.xuexi.android:id/general_card_title_id", className="android.widget.TextView")
        # 如果看过的，也要往上滑
        for el in findEl:
            titleTxt = el.get_text()
            if db.isRead(titleTxt, d.serial):  # 试一下，重复看一篇文章会不会得分!
                continue
            if tmpreadcount >= count:
                break
            log("正在阅读文章：" + titleTxt)
            while not visable_to_user(el):
                d.swipe_ext("up")
            el.click()
            time.sleep(2)
            readOneArticle(str(tmpreadcount) + "/" + str(count), need_comment, need_share)  # 阅读文章
            db.addRead(titleTxt, d.serial)
            tmpreadcount += 1
        # 接着往上滑，找
        d.swipe_ext("up")
        upNum += 1
        if upNum > 20:  # 先尝试下滑一次
            d.swipe_ext("down")
        if upNum > 30:
            log("异常结束！上滑超过30次，可能是网络原因！没有加载出文章，也有可能是滑动的原因！")
            break
        time.sleep(2)
    log("---------------------------文章阅读完成！")


# 发表观点
def sendCommond():
    log("正在发表观点……")
    tmp_in_put = d(resourceId="cn.xuexi.android:id/BOTTOM_LAYER_VIEW_ID").child(text="欢迎发表你的观点")
    while not tmp_in_put.exists:
        time.sleep(1)
        debug("未找到发表观点的按钮")
    tmp_in_put.click()
    while not d(resourceId="android:id/content").exists:
        time.sleep(1)
        debug("未进入输入观点界面")
    tmpEdit = d(resourceId="android:id/content").child(className="android.widget.EditText")
    debug("是否找到输入控件：" + str(tmpEdit.exists))
    tmpCommentTxt = _commentText[random.randint(0, len(_commentText) - 1)]
    tmpEdit.set_text(tmpCommentTxt)
    tmp_com = d(resourceId="android:id/content").child(text="发布")
    while not tmp_com.exists:
        time.sleep(1)
        debug("未找到发布按钮")
    tmp_com.click()
    if tmpEdit.exists:
        tmpEdit.clear_text()
    time.sleep(1)
    # 删除观点
    for tmpi in d.xpath('//*[@text="删除"]').all():  # 如果有删除按钮
        tmpi.click()
        time.sleep(0.5)
        d.xpath('//*[@resource-id="android:id/button1"]').click_exists(3)


def readOneArticle(progress, need_comment=None, need_share=None):  # 阅读一篇文章
    # 阅读
    for i in range(_readTime):
        time.sleep(1)
        while not d(resourceId="cn.xuexi.android:id/BOTTOM_LAYER_VIEW_ID").child(text="欢迎发表你的观点").exists:
            debug("不是阅读文章界面，请手动点击一篇文章进入……")
            d.sleep(1)
        if (i % 10 == 0):  # 10秒滑一次
            if (random.randint(0, 1) == 1):
                d.swipe_ext("up", scale=0.2)
            else:
                d.swipe_ext("down", scale=0.2)
        if i % 5 == 0:
            debug(progress + ":正在看文章，还剩" + str(_readTime - i) + "秒……")
    # 发表观点
    global _commentCount
    if (_commentCount < 2 and need_comment):  # 发表观点小于2次
        sendCommond()
        _commentCount += 1
    global _shareCount
    if (_shareCount < 2 and need_share):  # 分享次数<2，就要分享
        sharePageAndCollect()
        _shareCount = _shareCount + 1
    d.press("back")
    d.sleep(2)


# 分享加收藏
def sharePageAndCollect():
    # 分享
    log("正在分享……")
    # 这样找控件有点慢
    tmp_in_put = d(resourceId="cn.xuexi.android:id/BOTTOM_LAYER_VIEW_ID").child(text="欢迎发表你的观点")
    while not tmp_in_put.exists:
        time.sleep(1)
        debug("未找到发表观点的按钮")
    ele = tmp_in_put.sibling(className="android.widget.ImageView")
    # 收藏之后，取消收藏
    collectIcon = ele[1]
    collectIcon.click_exists(1)
    time.sleep(1)
    collectIcon.click_exists(1)
    # 分享
    shareIcon = ele[2]
    shareIcon.click_exists(1)
    time.sleep(1)
    share_to_qg = d(resourceId="cn.xuexi.android:id/pager").child(text="分享到学习强国")
    while not share_to_qg.exists:
        time.sleep(1)
        debug("未找到学习强国按钮，请等待……")
    share_to_qg.click()
    time.sleep(1)
    chose_people = d(resourceId="cn.xuexi.android:id/ui_common_base_ui_activity_toolbar").child(text="选择联系人")
    while not chose_people.exists:
        time.sleep(1)
        debug("未进入选择联系人界面，请等待……")
    debug("分享完成，正在返回……")
    d.press("back")


# 看视频
def watchVide(count):
    log("---------------------------执行看视频程序！")
    while not d(resourceId="cn.xuexi.android:id/comm_head_xuexi_mine").exists(3):
        log("不在主页,先等待看，可以手动进入主页……")
        d.sleep(1)
    while not d(resourceId="cn.xuexi.android:id/home_bottom_tab_button_ding").exists(3):
        log("没找到百灵视频,该操作不执行")
        d.sleep(1)
    d(resourceId="cn.xuexi.android:id/home_bottom_tab_button_ding").click_exists(1)
    d.xpath(
        '//*[@resource-id="cn.xuexi.android:id/view_pager"]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[2]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.ImageView[1]').wait_gone()
    time.sleep(1)
    d(resourceId="cn.xuexi.android:id/tv_close").click_exists(1)  # 第一次会出现设置铃声按钮，选择关闭
    vtop = ["推荐", "党史", "竖", "炫", "窗", "藏", "靓", "秀", "熊猫", "美食", "虹"]
    clicktop = vtop[random.randint(0, len(vtop) - 1)]
    while not d(text=clicktop).exists:
        clicktop = vtop[random.randint(0, len(vtop) - 1)]
    d(text=clicktop).click_exists(1)
    d.xpath(
        '//*[@resource-id="cn.xuexi.android:id/view_pager"]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[2]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.ImageView[1]').wait_gone()
    time.sleep(1)
    listview = d(resourceId="cn.xuexi.android:id/view_pager").child(className="android.widget.ListView").child(
        className="android.widget.FrameLayout")
    listview[0].click()
    time.sleep(1)
    # 开始看视频，每隔70秒滑动一次
    tmpcount = 0
    while tmpcount < count:
        for i in range(_readTime):
            time.sleep(1)
            while not d(resourceId="cn.xuexi.android:id/rv_video_list").exists:
                debug("未在观看视频界面，请点击一个百灵小视频")
                d.sleep(1)
            if i % 5 == 0:
                log(str(tmpcount + 1) + "/" + str(count) + "---正在观看视频……还剩" + str(_readTime - i) + "秒")
        tmpcount += 1
        d.swipe_ext("up", scale=0.8)
        time.sleep(2)
    # d.press("back")
    d(resourceId="cn.xuexi.android:id/iv_back").click_exists()
    log("---------------------------看视频结束！")
    # 这里要点击一下学习的按钮


def not_scroe(dis):
    # 专项答题，有答过，但是没得分的。
    # print(d(text="重新答题").info)
    for el in dis:
        # print("-------------------")
        brs = el.sibling(className="android.view.View")
        if len(brs) != 0:
            txt = brs[0].info.get("text")
            if not txt.endswith("积分"):
                return el
    return None


# 专项答题 只答一次
def specialty_question():
    log("---------------------------开始专项答题……")
    while not d(resourceId="cn.xuexi.android:id/comm_head_xuexi_mine").exists():
        debug("不在主页,先等待看，可以手动进入主页……")
        time.sleep(1)
    d(resourceId="cn.xuexi.android:id/comm_head_xuexi_mine").click()
    want_to_answer = d(resourceId="cn.xuexi.android:id/user_item_name", text="我要答题")
    while not want_to_answer.exists:
        debug("未找到我要答题按钮，正在重试……")
        d.sleep(1)
    want_to_answer.click()
    d(text="立即答题").click_exists(2)
    txt_say_qu = d(text="专项答题")
    while not txt_say_qu.exists:
        debug("未找到专项答题……重试中")
        d.sleep(1)
    txt_say_qu.click()
    d.sleep(2)
    i = 0
    has_question = True
    while True:
        if d(text="开始答题").exists and visable_to_user(d(text="开始答题")):
            has_question = True
            d(text="开始答题").click()
            break
        elif d(text="继续答题").exists and visable_to_user(d(text="继续答题")) and not_scroe(d(text="继续答题")) is not None:
            has_question = True
            not_scroe(d(text="继续答题")).click()
            break
        elif d(text="重新答题").exists and visable_to_user(d(text="重新答题")) and not_scroe(d(text="重新答题")) is not None:
            has_question = True
            not_scroe(d(text="重新答题")).click()
            break
        elif d(text="您已经看到了我的底线").exists():
            log("没有可作答的每周答题了,退出!!!")
            has_question = False
            break
        else:
            d.swipe_ext("up")
    if has_question:
        while True:
            if d(textStartsWith="单选题").exists or d(textStartsWith="填空题").exists or d(textStartsWith="多选题").exists:
                break
            debug("未进入答题界面，可手动进入……")
            d.sleep(1)
        last_question_index = -1
        while True:
            _result = answerAGroupQuestion(last_question_index)
            d.sleep(1)
            last_question_index = _result[1]
            if _result[0]:
                d.sleep(5)
            if d(text="本次作答分数").exists or d(textMatches=".+查看解析").exists:
                break
    d.press("back")
    d.sleep(0.5)
    d.press("back")
    d.sleep(0.5)
    while d(text="答题记录").exists:
        d.press("back")
        d.sleep(0.5)
    while d(resourceId="cn.xuexi.android:id/my_header").exists:
        d.press("back")
        d.sleep(0.5)

    log("---------------------------每周答题结束，返回主页……")


def visable_to_user(uis):
    # 控件是否显示在界面上
    screen_height = d.info.get("displayHeight")
    screen_width = d.info.get("displayWidth")
    v_left = uis.info.get("bounds").get("left")
    v_top = uis.info.get("bounds").get("top")
    v_right = uis.info.get("bounds").get("right")
    v_bottom = uis.info.get("bounds").get("bottom")
    # 我发现明明查看提示只有2个像素，但是在界面上{'bottom': 1280, 'left': 546, 'right': 656, 'top': 1278}
    debug("控件信息：")
    debug(uis.info)
    debug("控件坐标：" + str(v_left) + "," + str(v_top) + "||" + str(v_right) + "," + str(v_bottom))
    debug("屏幕宽高：" + str(screen_width) + "," + str(screen_height))
    return v_bottom - v_top > 2 and v_left <= screen_width and v_top <= screen_height and v_bottom <= screen_height and v_right <= screen_width


def weekQuesion():
    log("---------------------------开始每周答题……")
    while not d(resourceId="cn.xuexi.android:id/comm_head_xuexi_mine").exists():
        debug("不在主页,先等待看，可以手动进入主页……")
        time.sleep(1)
    d(resourceId="cn.xuexi.android:id/comm_head_xuexi_mine").click()
    want_to_answer = d(resourceId="cn.xuexi.android:id/user_item_name", text="我要答题")
    while not want_to_answer.exists:
        debug("未找到我要答题按钮，正在重试……")
        d.sleep(1)
    want_to_answer.click()
    d.sleep(1)
    d(text="立即答题").click_exists(2)
    d.sleep(1)
    txt_say_qu = d(text="每周答题")
    while not txt_say_qu.exists:
        debug("未找到每周答题……重试中")
        d.sleep(1)
    txt_say_qu.click()
    i = 0
    d.sleep(2)
    now_year = datetime.datetime.now().year
    while not d(textStartsWith=now_year).exists:
        d.sleep(1)
        debug("未进入每周界面，等一下……或者手动进入")
    has_question = True
    while i < 1:
        if d(text="未作答").exists:
            has_question = True
            debug("找到未作答的题目")
            while not visable_to_user(d(text="未作答")):
                d.swipe_ext("up")
            # d(scrollable=True).scroll.to(text="未作答")
            d(text="未作答").click()
            i += 1
            # 如果网络出错，重试几次
            d.sleep(1)
            while d(text="加载中").exists:
                d.sleep(1)
        elif d(text="您已经看到了我的底线").exists():
            log("没有可作答的每周答题了,退出!!!")
            has_question = False
            break
        else:
            d.swipe_ext("up")
    if has_question:
        # tip_lable = d(text="查看提示")
        while True:
            if d(textStartsWith="单选题").exists or d(textStartsWith="填空题").exists or d(textStartsWith="多选题").exists:
                break
            debug("未进入答题界面……，可能是网络错误，再等等，以后再想办法处理")
            d.sleep(1)
        last_question_index = -1
        while True:
            _result = answerAGroupQuestion(last_question_index)
            d.sleep(1)
            last_question_index = _result[1]
            if _result[0]:
                d.sleep(5)
            if d(text="再练一次").exists:
                d(text="返回").click()
                d.sleep(0.5)
                break
    d.press("back")
    d.sleep(0.5)
    while d(text="答题记录").exists:
        d.press("back")
        d.sleep(0.5)
    while d(resourceId="cn.xuexi.android:id/my_header").exists:
        d.press("back")
        d.sleep(0.5)
    log("---------------------------每周答题结束，返回主页……")


# import os
# import cv2

def fourFight():
    # 四人赛 随机答题，不管对错
    waitFor(d(resourceId="cn.xuexi.android:id/comm_head_xuexi_mine"), "主页").click()
    waitFor(d(resourceId="cn.xuexi.android:id/user_item_name", text="我要答题"), "我要答题").click()
    waitFor(d(text="排行榜"), "排行榜")
    d.xpath('//*[@resource-id="app"]/android.view.View[1]/android.view.View[3]/android.view.View[9]').click()
    waitFor(d(text="开始比赛"), "开始比赛").click()
    log("请手动答题！！！！！！")
    last_a_option = "-1"
    while True:
        title_re = getFightTitle(last_a_option)
        if len(title_re) != 0:
            if title_re[1]:  # 代表同一题
                continue
            if len(title_re) > 1:
                last_a_option = title_re[0]
            answer_fight(last_a_option, title_re)
            d.sleep(2)
        if d(text="继续挑战").exists:
            break
    waitFor(d(text="继续挑战"), "结束标志")
    d.press("back")
    d.sleep(1)
    d.press("back")
    d.sleep(1)
    d.press("back")
    d.sleep(1)
    d.press("back")
    d.sleep(1)


def twoFight():
    # 双人赛
    waitFor(d(resourceId="cn.xuexi.android:id/comm_head_xuexi_mine"), "主页").click()
    waitFor(d(resourceId="cn.xuexi.android:id/user_item_name", text="我要答题"), "我要答题").click()
    waitFor(d(text="排行榜"), "排行榜")
    d.xpath('//*[@resource-id="app"]/android.view.View[1]/android.view.View[3]/android.view.View[10]').click()
    waitFor(d(text="随机匹配"), "随机匹配")
    waitFor(d(text="擂主"), "本人头像")
    d.xpath('//*[@text="随机匹配"]').all()[0].parent().click()
    log("请手动答题！！！！！！")
    last_a_option = ""
    while True:
        title_re = getFightTitle(last_a_option)
        if len(title_re) != 0:
            if title_re[1]:  # 代表同一题
                continue
            if len(title_re) > 1:
                last_a_option = title_re[0]
            answer_fight(last_a_option, title_re)
            d.sleep(2)
        if d(text="继续挑战").exists:
            break
    waitFor(d(text="继续挑战"), "结束标志")
    d.press("back")
    d.sleep(1)
    d.press("back")
    d.sleep(1)
    if d(text="退出").exists:
        d(text="退出").click()
    d.sleep(1)
    d.press("back")
    d.sleep(1)
    d.press("back")
    d.sleep(1)


import easyocr
import os
import cv2
import re


def answer_fight(last_a_option, title_re):
    # 对战答题，直接在数据库里搜索选项，可能OCR的识别率会高一点
    print("-----------------------------")
    print("上一题A选项：" + last_a_option)
    md5_last = hashlib.md5(last_a_option.encode(encoding='UTF-8')).hexdigest()
    if d(text="继续挑战").exists:
        return
    while not d(className="android.widget.ListView").exists:
        d.sleep(1)
        if d(text="继续挑战").exists:
            return
    d.sleep(1)
    if d.xpath('//*[@resource-id="app"]/android.view.View[1]/android.view.View[4]/android.widget.Image[1]').exists:
        return
    list_view = d.xpath("//android.widget.ListView").all()
    if len(list_view) == 0:
        return
    index_count = list_view[0].info.get("childCount")
    need_random_click = True
    for index in range(index_count):
        if d(text="继续挑战").exists:
            return
        while not d(className="android.widget.ListView").exists:
            d.sleep(1)
            if d(text="继续挑战").exists:
                return
        child_find_list = d.xpath(
            list_view[0].get_xpath() + "/android.view.View[" + str(index + 1) + "]/android.view.View[1]").all()
        if len(child_find_list) == 0:
            continue
        child_view = child_find_list[0]
        option_img = "./screenshot/" + md5_last + str(index + 1) + ".jpg"
        option_img_file = child_view.screenshot()
        option_img_file.save(option_img)
        # d.sleep(0.5)
        option_txt = _reader.readtext(option_img, detail=0)
        if d(text="继续挑战").exists:
            break
        if len(option_txt) == 0:
            print("未识别到文字，路过")
        else:
            print("-----处理选项！")
            print(option_txt)
            option_1_txt = ""
            for o1 in option_txt:
                option_1_txt = option_1_txt + o1
            option_1_txt = dispose_title(option_1_txt)
            print("选项:" + option_1_txt)
            if len(title_re) > 2:
                right_anser = title_re[3]
                print("数据库-----------正确答案：" + right_anser)
                if right_anser in option_1_txt:
                    need_random_click = False
                    child_view.click()
                    break
            else:
                _result = db.hasAnswerChang(option_1_txt)
                inSql = len(_result[1]) > 0
                if inSql:
                    _result_json = json.loads(_result[1][0][1])
                    print("匹配答案------------正确答案：" + _result_json[0])
                    need_random_click = False
                    child_view.click()
                    break
    if need_random_click:
        print("###未搜索到正确答案，随机选择……")
        btns = d(className="android.widget.ListView").child(className="android.widget.RadioButton")
        btn_count = len(btns)
        if btn_count != 0:
            btns[random.randint(0, btn_count - 1)].click()
    return


def getMaxTitle(data):
    # 获取识别率最高的语句
    max_right_percent = 0
    max_right_txt = ""
    for i in data:
        right_percent = i[2]
        tmp_value = i[1]
        if right_percent > max_right_percent and len(tmp_value) > 5:
            max_right_percent = right_percent
            max_right_txt = tmp_value
    return max_right_txt


def dispose_title(max_title):
    # 处理标题
    search = re.search("[0-9]+\.", max_title)
    if search:
        max_title = max_title.replace(search.group(), "")
    search = re.search("[0-9]+。", max_title)
    if search:
        max_title = max_title.replace(search.group(), "")
    search = re.search("[a-zA-Z]+。", max_title)
    if search:
        max_title = max_title.replace(search.group(), "")
    search = re.search("[a-zA-Z]+.", max_title)
    if search:
        max_title = max_title.replace(search.group(), "")
    search = re.search("\'", max_title)
    if search:
        max_title = max_title.replace(search.group(), "\\'")
    search = re.search("\"", max_title)
    if search:
        max_title = max_title.replace(search.group(), "\\\"")
    max_title = max_title.lstrip()
    max_title = max_title.rstrip()
    return max_title


def del_file(path):
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            del_file(c_path)
        else:
            os.remove(c_path)


import hashlib


def getFightTitle(last_a_option):
    return_data = []
    md5_last = hashlib.md5(last_a_option.encode(encoding='UTF-8')).hexdigest()
    # 对战答题 ,获取题目，数据库里没有的话，就用选项去答题
    while not d(className="android.widget.ListView").exists:
        debug("正在等待题目出现！")
        d.sleep(1)
        if d(text="继续挑战").exists:
            return []
    # 四人赛
    d.sleep(2)
    if d(text="继续挑战").exists:
        return []
    file_dir = "./screenshot/"
    if not os.path.exists(file_dir):
        os.mkdir(file_dir)
    else:
        del_file(file_dir)
    sc_file = "./screenshot/" + md5_last + "four_fight.jpg"
    list_view = d.xpath("//android.widget.ListView").all()[0]
    print("列表位置：")
    print(list_view.info)
    list_index = list_view.attrib.get("index")
    # 填空题的题目获取稍有不同 list_view的index如果靠后，证明是填空题
    list_parent = list_view.parent()
    tmp_left = list_parent.info.get("bounds").get("left")
    tmp_right = list_parent.info.get("bounds").get("right")
    tmp_top = list_parent.info.get("bounds").get("top")
    tmp_bottom = list_view.info.get("bounds").get("top")
    print("默认位置：" + str(tmp_left) + "," + str(tmp_top) + "," + str(tmp_right) + "," + str(tmp_bottom))
    # 有时候控件还没显示
    index_count = list_view.info.get("childCount")
    while index_count < 1:  # 有时候选项要出来得慢一点
        d.sleep(1)
        print("正在等待选项出现1")
        if d(text="继续挑战").exists:
            break
        index_count = d.xpath("//android.widget.ListView").all()[0].info.get("childCount")
    # 一定要识别出来一个，就算是错的，因为选项有时候出来的快，
    if d(text="继续挑战").exists:
        return []
    d.sleep(2)
    child_find_list = d.xpath(
        list_view.get_xpath() + "/android.view.View[1]/android.view.View[1]").all()
    while len(child_find_list) == 0:
        d.sleep(1)
        print("正在等待选项出现2")
        if d(text="继续挑战").exists:
            break
        child_find_list = d.xpath(
            list_view.get_xpath() + "/android.view.View[1]/android.view.View[1]").all()
    if d(text="继续挑战").exists:
        return []
    while True:
        print("正在等待识别出文字")
        child_view = child_find_list[0]
        option_img = "./screenshot/" + md5_last + "1.jpg"
        option_img_file = child_view.screenshot()
        option_img_file.save(option_img)
        print("选项A信息：")
        print(child_view.info)
        d.sleep(0.5)
        if d(text="继续挑战").exists:
            break
        option_txt = _reader.readtext(option_img, detail=0)
        print(option_txt)
        if len(option_txt) != 0:
            now_a_option = option_txt[0]
            return_data.append(now_a_option)
            if last_a_option == now_a_option:
                debug("和上一题是同一题……返回")
                return_data.append(True)
                return return_data
            else:
                return_data.append(False)
            break
    # 查找ListView前面的一个控件，如果不是来源开头的 则没有问题
    if d(text="继续挑战").exists:
        return []
    if int(list_index) > 1:
        list_view_up_view_all = d.xpath(list_parent.get_xpath() + "/android.view.View[" + list_index + "]").all()
        if len(list_view_up_view_all) == 0:
            return []
        list_view_up_view = list_view_up_view_all[0]
        title_next_txt = ""
        iv = 0
        while iv < 2:
            if d(text="继续挑战").exists:
                break
            title_next_file = "./screenshot/" + md5_last + "title_next.jpg"
            tm_im = list_view_up_view.screenshot()
            tm_im.save(title_next_file)
            _reslut = _reader.readtext(title_next_file, detail=0)
            if len(_reslut) != 0:
                title_next_txt = _reslut[0]
                debug("识别到列表前一个元素：" + title_next_txt)
                break
            iv += 1
        if d(text="继续挑战").exists:
            return []
        if title_next_txt.startswith("来源") or title_next_txt.startswith("出题"):
            tmp_bottom = list_view_up_view.info.get("bounds").get("top")
            print("修改位置：" + str(tmp_left) + "," + str(tmp_top) + "," + str(tmp_right) + "," + str(tmp_bottom))
            # 修改bottom
    d.screenshot(sc_file)
    img = cv2.imread(sc_file)
    title_file = "./screenshot/" + md5_last + "four_title.jpg"
    cv2.imwrite(title_file, img[tmp_top:tmp_bottom, tmp_left:tmp_right])
    title_txt = _reader.readtext(title_file)
    if d(text="继续挑战").exists:
        return []
    if len(title_txt) != 0:
        print("---------------识别到文字！")
        print(title_txt)
        max_title = getMaxTitle(title_txt)
        if len(max_title) != 0:
            max_title = dispose_title(max_title)
            print(max_title)
            if not max_title.startswith("选择"):
                _result = db.hasChangeQuestion(max_title)
                inSql = len(_result[1]) > 0
                if inSql:
                    _result_json = json.loads(_result[1][0][1])
                    right_answer = _result_json[0]
                    return_data.append(max_title)
                    return_data.append(right_answer)
                    print(return_data)
    return return_data


def dayQuestion():
    # 每日答题
    log("---------------------------开始每日答题……")
    while not d(resourceId="cn.xuexi.android:id/comm_head_xuexi_mine").exists():
        debug("不在主页,先等待看，可以手动进入主页……")
        time.sleep(1)
    d(resourceId="cn.xuexi.android:id/comm_head_xuexi_mine").click()
    want_to_answer = d(resourceId="cn.xuexi.android:id/user_item_name", text="我要答题")
    while not want_to_answer.exists:
        debug("未找到我要答题按钮，正在重试……")
        d.sleep(1)
    want_to_answer.click()
    d(text="立即答题").click_exists(2)
    txt_say_qu = d(text="每日答题")
    while not txt_say_qu.exists:
        debug("未找到每日答题……重试中")
        d.sleep(1)
    txt_say_qu.click()
    while True:
        if d(textStartsWith="单选题").exists or d(textStartsWith="填空题").exists or d(textStartsWith="多选题").exists:
            break
        debug("未进入答题界面……，可能是网络错误，再等等，以后再想办法处理")
        d.sleep(1)
    last_question_index = -1
    while True:
        _result = answerAGroupQuestion(last_question_index)
        d.sleep(1)
        last_question_index = _result[1]
        if _result[0]:
            d.sleep(5)
        if d(text="再来一组").exists:  # 一天就答一次算了
            # if not d(text="领取奖励已达今日上限").exists:
            #     d(text="再来一组").click()
            #     log("积分未达上限，再来一组！")
            #     d.sleep(1)
            # else:
            log("---------------------------每日答题结束，返回主页……")
            d(text="返回").click()
            d.sleep(0.5)
            while d(text="答题记录").exists:
                d.press("back")
                d.sleep(0.5)
            while d(resourceId="cn.xuexi.android:id/my_header").exists:
                d.press("back")
                d.sleep(0.5)
            break


def test():
    log("test!")
    # print(d.info)
    # print(d.serial)
    screen_height = d.info.get("displayHeight")
    screen_width = d.info.get("displayWidth")
    # list_view = d.xpath("//android.widget.ListView")
    # print(d.xpath(list_view.all()[0].get_xpath() + "/android.view.View[1]/android.view.View[1]").all()[0].info)
    # img = d(text="新思想").screenshot()
    # print(_reader.readtext(img))
    # print(d.xpath('//android.widget.ListView/android.view.View[5]/android.view.View[3]').all()[0].info)
    # els = d(className="android.widget.ListView").child(index=4).child()
    # for el in els:
    #     print(el.info)
    # el = d(text="发表观点")
    # d(scrollable=True).scroll.to(el)
    # text = "+9积分123456"
    # sr = re.search("\+[0-9]+积分", text)
    # print(sr)
    # print(d(textMatches=".+查看解析").exists)
    # for el in :
    #     print(el.info)


def scrollTo(uio):
    return
    # 实测没啥用，某些页面有用。
    # 滑到指定控件，这个控件一定要有text ,否则就失败
    # txt = uio.info.get("text")
    # if len(txt) == 0:
    #     return
    # d(scrollable=True).scroll.to(text=txt)


# 答一组题
def answerAGroupQuestion(_last_index):
    # 回答一组题：有特别情况：继续答题时，有可能一进入就是准备下题题。
    log("开始答题……上一题序号：" + str(_last_index))
    _type = "填空题"
    _question = ""
    # 滑动到查看提示
    index_str = ""
    step_index = 0
    total_question = -1
    while True:
        if d(textStartsWith="填空题").exists or d(textStartsWith="单选题").exists() or d(textStartsWith="多选题").exists():
            break
        debug("未找到题目，请等待，或手动进入答题界面")
        d.sleep(1)
    if d(text="确定", className="android.view.View") \
            or d(text="下一题").exists \
            or d(text="完成").exists:
        debug("一进入 就是下一题")
    elif d(textStartsWith="填空题").exists and visable_to_user(d(textStartsWith="填空题")):
        _type = "填空题"
        index_str = d(textStartsWith="填空题").sibling(className="android.view.View", index=1).get_text()
        print("序号：" + index_str)
        if len(index_str) != 0:
            indexs = index_of_str(index_str, "/")
            if len(indexs) != 0:
                intdex = indexs[0]
                step_index = int(index_str[0:intdex:])
                total_question = int(index_str[intdex + 1::])
                if step_index == _last_index:
                    return [False, step_index]
        tmpedit = d.xpath('//android.widget.EditText')  # 编辑框
        tmpspacenum = tmpedit.all()[0].parent().info.get("childCount") - 1
        _question = tmpLeftStr = d.xpath(tmpedit.parent().parent().get_xpath() + "/android.view.View[1]").get_text()
        # log(_question)
        _result = db.hasQuesion(_type, tmpLeftStr)
        inSql = len(_result[1]) > 0
        read_space_str = None
        if inSql:
            _result_json = json.loads(_result[1][0][1])
            print(_result_json)
            read_space_str = _result_json[0]
        else:
            tmptipstr = getTipStr()
            find_index = index_of_str(tmptipstr, tmpLeftStr)
            if find_index == -1:
                alphabet = 'abcdefghijklmnopqrstuvwxyz!@#$%^&*()'
                read_space_str = str(random.sample(alphabet, tmpspacenum))
            else:
                find_index = find_index[0]
            if find_index == -1:
                log("出错！！多半是视频题或不匹配")
            else:
                start_index = find_index + len(tmpLeftStr)
                read_space_str = tmptipstr[start_index:(start_index + tmpspacenum)]
        for p1 in d(className="android.widget.EditText"):
            view_count = len(p1.sibling(className="android.view.View"))
            p1.set_text(read_space_str[0:view_count:])
            d.sleep(0.5)
            read_space_str = read_space_str[view_count::]
    elif d(textStartsWith="单选题").exists() or d(textStartsWith="多选题").exists():
        if d(textStartsWith="单选题").exists() and visable_to_user(d(textStartsWith="单选题")):
            _type = "单选题"
            index_str = d(textStartsWith="单选题").sibling(className="android.view.View", index=1).get_text()
        elif d(textStartsWith="多选题").exists and visable_to_user(d(textStartsWith="多选题")):
            _type = "多选题"
            index_str = d(textStartsWith="多选题").sibling(className="android.view.View", index=1).get_text()
        print("序号：" + index_str)
        if len(index_str) != 0:
            indexs = index_of_str(index_str, "/")
            if len(indexs) != 0:
                intdex = indexs[0]
                step_index = int(index_str[0:intdex:])
                total_question = int(index_str[intdex + 1::])
                if step_index == _last_index:
                    return [False, step_index]
        _question = qTitle = d(className="android.widget.ListView").sibling(className="android.view.View")[3].get_text()
        qSpace = '         '
        _tmp_index_space = index_of_str(qTitle, qSpace)
        space_num = (len(_tmp_index_space))
        if space_num > 0:
            qTitle = qTitle[0:_tmp_index_space[0]:]
        print(_type + "--" + qTitle)
        _result = db.hasQuesion(_type, qTitle)
        insql = len(_result[1]) > 0
        tmp_list = d(className="android.widget.ListView")
        # 滑到底部
        if d(text="查看提示").exists:
            while not visable_to_user(d(text="查看提示")):
                d.swipe_ext("up")
        click_num = 0  # 点击选项的次数，如果没有选择，随便选择一个
        if insql:
            _result_json = json.loads(_result[1][0][1])
            print(_result_json)
            if len(_result_json) == 1:
                find_class_name = "android.widget.RadioButton"
            else:
                find_class_name = "android.widget.CheckBox"
            for t_ui in tmp_list.child(className=find_class_name):
                answer_str = t_ui.sibling(className="android.view.View")[1].get_text()
                if answer_str in _result_json:
                    scrollTo(t_ui)
                    t_ui.click(1)
                    click_num += 1
        else:
            # 找选项数据
            # 如果空格数==选项数 那么不用想，直接选
            list_count = tmp_list[0].info.get("childCount")
            if list_count == space_num:  # 空格数和选项数量相等，直接选择。
                for cel in tmp_list.child(className="android.widget.CheckBox"):
                    click_num += 1
                    scrollTo(cel)
                    cel.click()  # 一一选中
            else:
                tmptipstr = getTipStr()
                if space_num == 1:
                    find_class_name = "android.widget.RadioButton"
                else:
                    find_class_name = "android.widget.CheckBox"
                for t_ui in tmp_list.child(className=find_class_name):
                    answer_str = t_ui.sibling(className="android.view.View")[1].get_text()
                    if answer_str in tmptipstr:
                        scrollTo(t_ui)
                        t_ui.click(1)
                        click_num += 1
        if click_num == 0:  # 一个都没选，随便选一个
            tmp_list.child(className=find_class_name)[0].click()
    time.sleep(1)
    debug("当前第" + str(step_index) + "题，共" + str(total_question) + "题:" + _question)
    while d(text="确定", className="android.view.View") \
            or d(text="下一题").exists \
            or d(text="完成").exists:
        log("检测是否完成！")
        d.sleep(1)
        can_exit = False
        if d(textStartsWith="正确答案：").exists:
            # 记录到题库
            right_answer = d(textStartsWith="正确答案：").get_text()[len("正确答案：")::].strip().replace(" ", "")
            # db.addQuestion(_type, _question, right_answer)  #TODO 修改存储方法，答案字段最好存入文字，而不是ABCD
            can_exit = True
        if d(text="确定").exists:
            d(text="确定").click()
        elif d(text="下一题").exists:
            d(text="下一题").click()
        elif d(text="完成").exists:
            d(text="完成").click()
        if can_exit:
            break
    return [step_index == total_question, step_index]  # True是最后一题，False不是最后


def getTipStr():
    # 获取提示的字符串
    debug("准备获取提示……")
    waitFor(d(text="查看提示"), "查看提示").click()
    waitFor(d(text="提示"), "提示布局")
    d.sleep(2)
    tmptip = d.xpath('//*[@text="提示"]').all()[0]
    tip_par = tmptip.parent()
    # print(tip_par.attrib)
    tmptipstr = d.xpath(tip_par.parent().get_xpath() + "/android.view.View[2]/android.view.View[1]").get_text()
    while d(text="提示").exists:
        x = tmptip.info.get("bounds").get("left")
        y = tip_par.info.get("bounds").get("top") - 80
        d.click(x, y)
        debug("提示还未关闭，尝试关闭:" + str(x) + "," + str(y))
        d.sleep(1)
    return tmptipstr


def index_of_str(s1, s2):
    # 返回s2在s1中的序号
    res = []
    index = 0
    if s1 == "" or s2 == "":
        return -1
    split_list = s1.split(s2)
    for i in range(len(split_list) - 1):
        index += len(split_list[i])
        res.append(index)
        index += len(s2)
    return res if res else -1
