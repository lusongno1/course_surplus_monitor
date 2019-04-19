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
#mail_pass = "ls3325854"  #163邮箱smtp生成的密码
#
#mail_host = "smtp.126.com"    
#mail_user = "lusongcool@126.com"  
#mail_pass = "Ls3325854"  #163邮箱smtp生成的密码

#mail_host='smtp.qq.com'    
#mail_pass = 'ukstcgwxrqurbbjc'
#mail_user='lusongno1@qq.com'  

#mail_host='smtp.qq.com'    
#mail_pass = 'zcgzfgltccotbaih'
#mail_user='985009425@qq.com' 

#mail_host='smtp.cstnet.cn'    
#mail_pass = 'ls3325854'
#mail_user='lusong17@mails.ucas.ac.cn'

mail_host='mail.cstnet.cn'    
mail_pass = 'ls3325854'
mail_user='lusong17@mails.ucas.ac.cn'

#mail_host='smtp.qq.com'    
#mail_pass = 'dyhukxarehnjbace'
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
    time.sleep(300)
  


#html = jwxk_html
#regular = r'<label for="id_([\S]+)">' + course[0][0][:2] + r'-'
#institute_id = re.findall(regular, html)[0]
#url = 'http://jwxk.ucas.ac.cn' + \
#              re.findall(r'<form id="regfrm2" name="regfrm2" action="([\S]+)" \S*class=', html)[0]
#post_data = {'deptIds': institute_id, 'sb': '0'}
#
#html = session.post(url, data=post_data, headers=headers).text

