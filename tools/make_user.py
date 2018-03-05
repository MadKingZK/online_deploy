#coding=utf-8


import random
import smtplib
from email.mime.text import MIMEText
from email.header import Header

def makepass():
    salt = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    codestr = ''
    for i in range(0,8):
        codestr = '%s%s' % (codestr,random.choice(salt))
    return codestr

def mkldif(filename=None):
    if not filename:
        filename = "user.txt"
    outfile = "users.ldif"
    f1 = open(filename)
    f2 = open(outfile,'w')
    for line in f1:
        line = line.strip()
        l = line.split('\t')
        password = makepass()
        password = '111111'
        content = '''dn: cn=%s,ou=users,dc=huoqiu,dc=cn
cn: %s
mail: %s
objectclass: inetOrgPerson
objectclass: top
sn: %s
userpassword: %s

''' %(l[0],l[0],l[2],l[1],password)
        f2.write(content)
        mailcontent = '''
                         <strong>如果您不需要在stg环境发布代码，请忽略该邮件</strong><br>
                         stg的web版发布系统已经可用<br>
                         请用以下账号信息登录，登录后点击右上角的美女头像，重置密码！<br>
                         您的用户名是: %s<br>您的密码是: %s<br>
                         <a href='http://deploy.stg.huoqiu.net'>http://115.28.107.76</a><br/>
                         发布流程： 点击我要发布-选择发布平台->创建发布任务->发布完成->测试->关闭发布平台<br/>
                         <font color=red>注意：发布完成测试完毕后，请在我要发布页面点击关闭按钮，否则将影响后面人的使用</font>''' %(l[0],password)

        #if l[0] == 'zangkuo':
        #    sendemail(l[2],mailcontent)
        sendemail(l[2],mailcontent)
        print '------sendmail to %s----------' %l[2]

    f1.close()
    f2.close()

def sendemail(address,content):
    sender = ''
    receiver = address
    subject = 'deploy.stg.huoqiu.net账号信息'
    smtpserver = 'smtp.exmail.qq.com'
    username = ''
    password = ''
    msg = MIMEText(content,'html','utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = '<>'

    smtp = smtplib.SMTP()
    smtp.connect(smtpserver)
    smtp.login(username, password)
    smtp.sendmail(sender, receiver, msg.as_string())
    smtp.quit()
if __name__ == "__main__":
    mkldif()