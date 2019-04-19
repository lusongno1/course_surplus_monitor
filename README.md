# 国科大教务选课系统课程余量监测python脚本

## 初衷:
果壳同学都知道，在国科大选课，很多课还没找到就被抢光了。所以，有一个想法，可以写一个python自动选课的脚本，到了时间自动秒选课程。可是，谁能冒这个风险呢？万一出bug了呢？所以，建议选课还是自己手动去选。
每到选课时间中午12:00一过，很多想选的课程几秒钟就满了，导致没选上。在接下来的日子里，很有可能有一些人因为某一些原因退课，这时候就可以捡漏。但是，没有人有时间，动不动就会上系统看一下有没有漏捡，所以一个基本的想法就是写一段python脚本实现自动监控，当有课程余量时，想办法通知你，当然，也可以使用脚本自动选上别人退下的课程，这有个风险是，有可能程序把你原来选的课整得乱糟糟。所以，我个人不建议把选课权交给程序的。

## 目标：

1、登录国科大教务系统
2、进入选课系统
3、从学期课表当中去提取相关课程的已选和限选数据
4、当课程有余量的时候，将课程相关信息通过Email的形式发送到指定邮箱。

## 代码：

```python
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 09:48:55 2018

@author: LuSong
"""
#国科大自动选课监控脚本

from __future__ import print_function
import re
import time
import json
import requests
from bs4 import BeautifulSoup
#from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import codecs
#from imp import reload
#import sys
#reload(sys) 

with open("./private.txt") as f:
    courses = []
    for i, line in enumerate(f):
        if i < 3: continue
        courses.append(line.strip())#strip去掉换行

with codecs.open(r'./private.txt', "r", 'utf-8') as f:
    username = password = None
    for i, line in enumerate(f):
        if i == 0:
            line = bytes(line.encode('utf-8'))#utf-8编码后，转为字节类型
            if line[:3] == codecs.BOM_UTF8:#容错机制
                line = line[3:]
            username = line.decode('utf-8').strip()
        elif i == 1:
            password = line.strip()
        elif i == 2:
            mailto_list = line.strip().split()#split 按空格读入不同的邮箱
        else:
            break
                
#mailto_list = ["lusongno1@qq.com","taoo152805@126.com"]  #目标邮箱，只有这里改成你自己的邮箱

#mail_host = "smtp.163.com"    
#mail_user = "lusongcool@163.com"  
#mail_pass = "pw"  #163邮箱smtp生成的密码
#
#mail_host = "smtp.126.com"    
#mail_user = "lusongcool@126.com"  
#mail_pass = "pw"  #163邮箱smtp生成的密码

#mail_host='smtp.qq.com'    
#mail_pass = 'pw'
#mail_user='lusongno1@qq.com'  

#mail_host='smtp.qq.com'    
#mail_pass = 'pw'
#mail_user='985009425@qq.com' 

#mail_host='smtp.cstnet.cn'    
#mail_pass = 'pw'
#mail_user='lusong17@mails.ucas.ac.cn'

mail_host='mail.cstnet.cn'    
mail_pass = 'password'这里改成自己发送邮件的邮箱和密码
mail_user='lusong17@mails.ucas.ac.cn'

#mail_host='smtp.qq.com'    
#mail_pass = 'pw'
#mail_user='1349155637@qq.com' 

def send_mail(to_list, sub, content):
    me = "LogServer"+"<"+mail_user+">"
    msg = MIMEText(content, _subtype='plain', _charset='utf-8')
    msg['Subject'] = sub    
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
 #       server=smtplib.SMTP(mail_host, 25) 
        server=smtplib.SMTP_SSL(mail_host, 465) 
        server.login(mail_user, mail_pass)
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        return True
    except (Exception) as e:
        print(str(e))
        return False
#变量的初始化
session = None
headers = None
jwxk_html = None


flag = send_mail(mailto_list,'发送测试','可以发送邮件，开始监控……')
if flag:
    print('可以发送邮件，监控中：\n')
else:
    print('不能发送邮件，请检查！\n')

count = 0

while flag:
    #登录系统
    session = requests.session()
    login_url = 'http://onestop.ucas.ac.cn/Ajax/Login/0'#提交信息地址，这个地址不需要验证码
    headers=  {
                'Host': 'onestop.ucas.ac.cn',
                "Connection": "keep-alive",
                'Referer': 'http://onestop.ucas.ac.cn/home/index',
                'X-Requested-With': 'XMLHttpRequest',
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36",
            }
    post_data = {
                "username": username,
                "password": password,
                "remember": 'checked',
            }
    html = session.post(login_url, data=post_data, headers=headers).text
    res = json.loads(html)#登录地址是一回事，提交数据地址是一回事，返回的地址是一回事，这里打开返回的地址
    html = session.get(res['msg']).text
    print('登录系统成功……')
    
    #利用Identity进入选课系统
    #打开选课系统
    
    #获取Identity
    url = "http://sep.ucas.ac.cn/portal/site/226/821"
    r = session.get(url, headers=headers)
    #f = open('r.html','w+',encoding='utf-8')
    #f.write(r.text)
    #f.close
    
    code = re.findall(r'"http://jwxk.ucas.ac.cn/login\?Identity=(.*)"', r.text)[0]
    #打开选课系统
    url = "http://jwxk.ucas.ac.cn/login?Identity=" + code
    headers['Host'] = "jwxk.ucas.ac.cn"
    r = session.get(url, headers=headers)
    temp = r.text
    print('切换至课余量界面……')
    #f = open('temp.html','w+',encoding='utf-8')
    #f.write(temp)
    #f.close
    
    
    #url = 'http://jwxk.ucas.ac.cn/courseManage/main'
    #r = session.get(url, headers=headers)
    #jwxk_html = r.text
    #f = open('jwxk_html.html','w+',encoding='utf-8')
    #f.write(jwxk_html)
    #f.close
    
    
    count = count + 1


    print('第'+str(count)+'次尝试监控……')
    url = 'http://jwxk.ucas.ac.cn/course/termSchedule'
#    headers['Host'] = "onestop.ucas.ac.cn"
    r = session.get(url, headers=headers)
    jwxk_html = r.text
#    f = open('termSchedule.html','w+',encoding='utf-8')
#    f.write(jwxk_html)
#    f.close
    
    
    soup=BeautifulSoup(jwxk_html,'lxml')
 #   print(soup.prettify())
#    f = open('soupprettify.html','w+',encoding='utf-8')
#    f.write(soup.prettify())
#    f.close
    
    soup = soup.table
    
 #   courses = ['23MGB003H-21']#这里改成你要监控的课程编号们
    for course in courses:
 #       course = re.compile(course)
        course_ind = soup.find_all(target='_blank',string=course)
        #course_ind = soup.find_all(string=course)
        course_info = course_ind[0].parent.parent
        infomation = course_info.find_all('td')
        
        lim_num = int(infomation[6].string)
        num = int(infomation[7].string)
        item = infomation[2].string
        course_left = lim_num-num
        
        if course_left > 0:
         #   flag = send_mail(mailto_list,'nihao','haoya')
            flag = send_mail(mailto_list,item+'课程可选',course_info.text +'\n\n'+ '余量为：'+str(course_left))     
            if flag:
                print('有课余量，发送成功！'+item+'余量为：'+str(course_left))
  #              time.sleep(180)
                courses.remove(course)
            else:
                print('发送课余量邮件失败！')
        else:
            print(item+'课程的余量为：'+str(course_left))
        time.sleep(1)
    time.sleep(600)
  


#html = jwxk_html
#regular = r'<label for="id_([\S]+)">' + course[0][0][:2] + r'-'
#institute_id = re.findall(regular, html)[0]
#url = 'http://jwxk.ucas.ac.cn' + \
#              re.findall(r'<form id="regfrm2" name="regfrm2" action="([\S]+)" \S*class=', html)[0]
#post_data = {'deptIds': institute_id, 'sb': '0'}
#
#html = session.post(url, data=post_data, headers=headers).text


```
其中的国科大教务系统账号密码、接收邮件邮箱、需要监控的课程编号从private.txt文件读入。
其中，private.txt文本的第一行和第二行表示系统账号密码，第三行表示接收邮件信息的邮箱，若有多个接收邮箱，中间用空格隔开，后面每一行是所要监控的课程编码，每行一个。例：

```
lusongcool@163.com
password
taoo152805@126.com lusongcool@163.com 1349155637@qq.com
23MGB003H-21
09MGX005H
23MGB003H-01
23MGB003H-03
23MGB003H-04
23MGB003H-06
23MGB003H-07
23MGB003H-10
23MGB003H-11
23MGB003H-12
23MGB003H-16
23MGB003H-17
23MGB003H-22
23MGB003H-23
23MGB003H-26
```

> 很多人喜欢模块化的编程，将程序写成面向对象的形式，以多以函数和类的形式呈现，那也是可以的。但个人觉得，刚开始还是按顺序理下来好，程序也容易读懂和迁移。

## 步骤：

1、打开登录界面http://onestop.ucas.ac.cn/home/index
2、输入错误的账号信息，按F12调出浏览器的开发者工具，点击登录提交数据
3、编写python代码，拷贝相关信息，进行post、get两次发送请求，登录教务系统。（一定的曲折性）
	（1）通过错误的账号登录，获取post所需要的相关信息进行post获得Identity。
	（2）利用获得的Identity和正确账号登录获取的相关信息，进行get登录教务系统。
4、从appStore页面向过渡页面http://sep.ucas.ac.cn/portal/site/226/821发送get请求，从返回的页面中利用正则表达获取Identity（和前面那个不一样）。

> 之所以有这一步的操作是因为，观察发现转向选课系统通知公告页面所发送的请求中，来自的页面Referer并不是appStore页面，如下：
![这里写图片描述](http://img.blog.csdn.net/20180222153921885?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvbHVzb25nbm8x/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70)
所以尝试性地向这个中间页面发送了get请求，返回的页面中含有我们下一步发送get请求所需要的Identity。

5、利用获得的Identity得到通过get方法进入选课系统所需要的发送请求的目标地址。
6、修改header的host，一步一步通过get方法，进入学期课表页面。
7、利用Beautifulsoup提取相关信息，判断是否发送邮件，动作……

## 遇到的难点解析
1、登录教务系统时，后面通过get向一个含秘钥的地址提交请求，这个地址的获取需要通过错误的账号密码登录抓包获取。
2、一直无法正确地通过get请求获取学期课表页面。问题出在了使用get方式时url中含无规律变动的一个Identity，而这个Identity一直无法正确获取，因为浏览器没抓到302重定向之前的一个交互信息，而这个里面含有get所需要的key。最后，利用向重定向之前的一个网页请求，获得了一个容易重定向且浏览器没抓到的一个网页，用正则从里面提取了一个Identity。
3、程序写完后，在本地Win10机子上可以用，但是放到腾讯云Windows Server虚拟主机上就一直连接不上163邮箱系统（发送邮件用），后来换成了QQ邮箱系统，就可以用了。


## 知识补充：
1、Request URL:提交请求的目标地址
2、Referer:从哪个页面发送出请求
3、Location:发生跳转，跳转向的界面
4、发送请求时，会话保持若host发生改变，headers要更新host。
5、跳转的前后界面可以视作统一处理，因为跳转前后会话信息没有发生改变。
6、Form Data：提交的账号密码等信息。



