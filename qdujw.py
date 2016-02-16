# -*- coding: utf-8 -*-
'''
@title: 青岛大学教务爬虫
@author: Kyle
@time: 2016-1-30
'''

from PIL import Image
import io
import re
import getpass
import requests
from bs4 import BeautifulSoup

class qdujw:
    def __init__(self):
        self.userid = 0
        self.s = requests.Session()
        self.headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64)\AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'}

    # 教务登录
    def login(self):
        loginurl = 'http://jw.qdu.edu.cn/academic/j_acegi_security_check'
        testurl = 'http://jw.qdu.edu.cn/academic/showHeader.do'
        userurl = 'http://jw.qdu.edu.cn/academic/showPersonalInfo.do'
        codeurl = 'http://jw.qdu.edu.cn/academic/getCaptcha.do'

        # 学号和密码
        print ('请输入学号和密码')
        sid = input('学号：')
        passwd = getpass.getpass('密码：')

        # 验证码
        code  = self.s.get(codeurl, headers=self.headers, stream = True)
        img = Image.open(io.BytesIO(code.content))
        img.save('code.jpg')
        codetext = input('验证码：')

        # 登录
        postdata = {'j_username':sid, 'j_password':passwd, 'j_captcha':codetext}
        self.s.post(loginurl, postdata)

        # 判断是否登录成功
        userpage = self.s.get(userurl).content
        if re.search(b'\d{12}', userpage):
            user = re.findall(b'<span>(.*?)\((.*?)\)</span>', self.s.get(testurl).content, re.S)
            for u in user:
                print
                print ('你好！' + u[0].decode('UTF-8', 'ignore') + '，欢迎登录！')
            userid = re.findall(b'.*?userid=(.*?)"', userpage, re.S)
            for i in userid:
                self.userid = self.userid*10 + int(i)
            return 1
        else:
            print ('登陆失败')
            return 0

    # 查询成绩
    def scores(self):
        print ('======= 成绩查询 ========')
        print ()
        year = input('请输入查询学年: ')
        term = input('春季学期输入[1],秋季学期输入[2]: ')
        scoresurl = 'http://jw.qdu.edu.cn/academic/manager/score/studentOwnScore.do'
        # 字符串计算  eval()
        postdata = {'year':eval(year+'-'+'1980'), 'term':term, 'para':'0'}
        scorespage = self.s.post(scoresurl, postdata).content
        aa='<td>'+year+'[\s\S]*?<td>[\s\S]*?<td>(.*?)[\s].*?</td>[\s\S]*?</td>[\s\S]*?<td>(.*?)[\s].*?</td>[\s\S]*?</td>[\s\S]*?</td>[\s\S]*?</td>[\s\S]*?</td>[\s\S]*?</td>[\s\S]*?</td>'
        # str转types  .encode(encoding="utf-8")
        scores = re.findall(aa.encode(encoding="utf-8"), scorespage, re.S)
        print ()
        print ('======= 考试成绩 ========')
        for s in scores:
            print ()
            print (s[0].decode('UTF-8', 'ignore') + ' : '  +  s[1].decode('UTF-8', 'ignore'))

    # 查询课表
    def kebiao(self):
        kburl = 'http://jw.qdu.edu.cn/academic/manager/coursearrange/showTimetable.do'
        get = {'id':self.userid, 'yearid':'35', 'termid':'2', 'timetableType':'STUDENT', 'sectionType':'COMBINE'}

        kebiao = BeautifulSoup(self.s.get(kburl, params=get).content, "lxml")
        for kk in kebiao.find_all("td", class_="center"):
            print (kk.get_text())

    # 教务通知
    def news(self):
        newsurl = 'http://jw.qdu.edu.cn/homepage/infoArticleList.do;jsessionid=E06A6E2B5FA3F797FAB8FA5F6331AC92?columnId=358'
        news = BeautifulSoup(requests.get(newsurl).content, "lxml")
        for tt in news.find_all(href=re.compile("articleId")):
            print (tt.get_text(strip=True))
            print (tt.get('href'))
            print ()


jw = qdujw()
print ('======== 教务通知 ========')
jw.news()
print ('======== 登录教务系统 ========')
if jw.login() == 1 :
    while 1 :
        print ()
        print ()
        print ('======== 青岛大学教务系统 ========')
        print ()
        print ('[1]查询成绩')
        print ('[2]查询课表')
        print ('[3]退出')
        print ()
        choice = input('请选择: ')
        if choice == '1':
            jw.scores()
        elif choice == '2':
            jw.kebiao()
        elif choice == '3':
            exit()
        print ()
        print ()
    print ()
    print ()
