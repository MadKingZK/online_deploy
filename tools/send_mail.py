#-*- coding:utf-8 -*-
import smtplib
from email.mime.text import MIMEText
from email.header import Header

sender = ''
subject = 'LDAP秘钥更改验证'
smtpserver = 'smtp.exmail.qq.com'
smtpuser = ''
smtppass = ''

def sendmail(receiver,mailcode):
    content='''<div style="width:680px;padding:0 10px;margin:0 auto;padding-top:70px;">
                <div style="line-height:1.5;font-size:14px;margin-bottom:25px;color:#4d4d4d;">
                    <strong style="display:block;margin-bottom:15px;">
                        亲爱的%s：
                        <span style="color:#f60;font-size: 16px;"></span>您好！
                    </strong>

                    <strong style="display:block;margin-bottom:15px;text-indent:35px">
                        您正在修改LDAP服务用户密码，请在验证码输入框中输入：
                        <br><span style="color:#f60;font-size: 24px;padding-left:35px;">%s</span></br>
                    </strong>
                </div>

                <div style="margin-bottom:30px;">
                    <small style="display:block;margin-bottom:20px;font-size:12px;">
                        <p style="color:#747474;">
                            注意：此操作可能会修改您的gitlab、部署平台等密码，如非本人操作，请尽快告知运维人员。
                            <br>（任何人不应向你索取此验证码，请勿泄漏！)
                        </p>
                    </small>
                </div>
            </div>'''%(receiver[0].split('@')[0],mailcode)
    msg = MIMEText(content,'html','utf-8')#中文需参数‘utf-8'，单字节字符不需要
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = '<%s>' % sender
    msg['To'] = ";".join(receiver)
    try:
        smtp = smtplib.SMTP()
        smtp.connect(smtpserver)
        smtp.login(smtpuser, smtppass)
        smtp.sendmail(sender, receiver, msg.as_string())
        smtp.quit()
    except Exception as e:
        print(e)

if __name__ == '__main__':
    sendmail([''],'')