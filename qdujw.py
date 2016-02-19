# -*- coding: utf-8 -*-
'''
@title: 青岛大学教务爬虫
@author: Kyle
@time: 2016-1-30
@update: 2016-2-19
'''

from PIL import Image
import io
import re
import getpass
import requests
import pytesseract
from bs4 import BeautifulSoup


class qdujw:
    def __init__(self):
        self.userid = 0
        self.s = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36'
        }

    # 教务登录
    def login(self):
        global sid, passwd
        loginurl = 'http://jw.qdu.edu.cn/academic/j_acegi_security_check'
        codeurl = 'http://jw.qdu.edu.cn/academic/getCaptcha.do'

        # 验证码
        code = self.s.get(codeurl, headers=self.headers, stream=True)
        img = Image.open(io.BytesIO(code.content))

        # 降噪
        threshold = 140
        table = []
        for i in range(256):
            if i < threshold:
                table.append(0)
            else:
                table.append(1)

        # 将彩色图像转换为灰度图像
        imgry = img.convert('L')

        # 讲图像中噪声去除
        out = imgry.point(table, '1')

        codetext = pytesseract.image_to_string(out, config='digits')

        # 去除空格，将.替换为0
        codetext = codetext.replace(' ', '')
        codetext = codetext.replace('.', '0')

        # 登录
        postdata = {
            'j_username': sid,
            'j_password': passwd,
            'j_captcha': codetext
        }
        self.s.post(loginurl, postdata)

    # 判断是否登录成功
    def pd(self):
        testurl = 'http://jw.qdu.edu.cn/academic/showHeader.do'
        userurl = 'http://jw.qdu.edu.cn/academic/showPersonalInfo.do'

        userpage = self.s.get(userurl).content

        if re.search(b'\d{12}', userpage):
            user = re.findall(
                b'<span>(.*?)\((.*?)\)</span>', self.s.get(testurl).content, re.S)
            for u in user:
                print
                print '你好！' + u[0] + '，欢迎登录！'
            userid = re.findall(b'.*?userid=(.*?)"', userpage, re.S)
            for i in userid:
                self.userid = self.userid * 10 + int(i)
            return 0
        else:
            print '登录中，请稍等......'
            return 1

    # 查询成绩
    def scores(self):
        print '======= 成绩查询 ========'
        print
        year = raw_input('请输入查询学年: ')
        term = raw_input('春季学期输入[1],秋季学期输入[2]: ')
        scoresurl = 'http://jw.qdu.edu.cn/academic/manager/score/studentOwnScore.do'

        # 字符串计算  eval()
        postdata = {
            'year': eval(year + '-' + '1980'),
            'term': term,
            'para': '0'
        }
        scorespage = self.s.post(scoresurl, postdata).content
        aa = '<td>' + year + \
            '[\s\S]*?<td>[\s\S]*?<td>(.*?)[\s].*?</td>[\s\S]*?</td>[\s\S]*?<td>(.*?)[\s].*?</td>[\s\S]*?</td>[\s\S]*?</td>[\s\S]*?</td>[\s\S]*?</td>[\s\S]*?</td>[\s\S]*?</td>'

        # str转types  .encode(encoding="utf-8")
        scores = re.findall(aa.encode(encoding="utf-8"), scorespage, re.S)
        print
        print '======= 考试成绩 ========'
        for s in scores:
            print
            print s[0] + ' : ' + s[1]

    # 查询课表
    def kebiao(self):
        print '======= 课表查询 ========'
        print
        year = raw_input('请输入查询学年: ')
        term = raw_input('春季学期输入[1],秋季学期输入[2]: ')
        kburl = 'http://jw.qdu.edu.cn/academic/manager/coursearrange/showTimetable.do'
        get = {
            'id': self.userid,
            'yearid': eval(year + '-' + '1980'),
            'termid': term,
            'timetableType': 'STUDENT',
            'sectionType': 'COMBINE'
        }

        kebiao = BeautifulSoup(self.s.get(kburl, params=get).content, "lxml")
        for kk in kebiao.find_all("td", class_="center"):
            print kk.get_text()

    # 教务通知
    def news(self):
        newsurl = 'http://jw.qdu.edu.cn/homepage/infoArticleList.do;jsessionid=E06A6E2B5FA3F797FAB8FA5F6331AC92?columnId=358'
        news = BeautifulSoup(requests.get(newsurl).content, "lxml")
        for tt in news.find_all(href=re.compile("articleId")):
            print tt.get_text(strip=True)
            print tt.get('href')
            print


jw = qdujw()
print '======== 教务通知 ========'
jw.news()
print

print '======== 登录教务系统 ========'

# 学号和密码
print '请输入学号和密码'
sid = raw_input('学号：')
passwd = getpass.getpass('密码：')

jw.login()

# 判断是否登录成功，失败则继续登录
while jw.pd():
    jw.login()

while 1:
    print
    print '======== 青岛大学教务系统 ========'
    print
    print '[1]查询成绩'
    print '[2]查询课表'
    print '[3]退出'
    print
    choice = raw_input('请选择: ')
    print
    if choice == '1':
        jw.scores()
    elif choice == '2':
        jw.kebiao()
    elif choice == '3':
        exit()
