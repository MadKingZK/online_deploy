#coding=utf-8
from django.shortcuts import render, redirect
from django.http.response import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate
from tools.ldaptool import LDAPTool
from tools.send_mail import sendmail
#from django.contrib.messages.tests.test_cookie import set_cookie_data
import datetime,time
from django.conf import settings
from django.template import loader, RequestContext
from random import choice
import string
from autodeploy.models import MailCode

def custom_proc(request):
    "A context processor that provides 'nickname'."
    return {
        'nick':request.COOKIES('nick')
    }

def set_cookie(response, key, value, days_expire = 7):
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60  #one year
    else:
        max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)

def login(request):
    if request.COOKIES.get('username'):
        nick = request.COOKIES.get('nick')
        return render(request,'index.html',{'nick':nick})
    else:
        return render(request,'login.html')

def loginHandle(request):
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            check_res = ldapValidate(username,password)
            if check_res:
                ldt = LDAPTool()
                userinfo = ldt.ldap_get_user(username)
                response = render(request,'index.html',{'nick':userinfo['nick']})
                set_cookie(response,'username',userinfo['username'])
                set_cookie(response,'nick',userinfo['nick'])
                set_cookie(response,'email',userinfo['email'])
                return response
            else:
                return render(request, 'login.html', {'info': '用户名或密码错误'})
        except Exception as e:
            print(e)
            return render(request,'login.html',{'info':'用户名或密码错误'})

    else: return render(request,'login.html',{'info':'用户名或密码错误'})

def logout(request):
    response = render(request,'login.html')
    try:
        response.delete_cookie('username')
        response.delete_cookie('nick')
        response.delete_cookie('email')
    except Exception as e:
        pass
    return response

def changepass(request):
        return render(request,'changepass.html')

def changepassHandle(request):
    if request.POST:
        password = request.POST.get('password')
        newpassword = request.POST.get('newpassword')
        confirmpassword = request.POST.get('confirmpassword')
        if newpassword != confirmpassword:
            return HttpResponse("<script>alert('新密码两次输入不匹配！');history.back();</script>")
        username = request.COOKIES.get('username')
        if not username:
            return HttpResponse('请登录')
        if not ldapValidate(username, password):
            return HttpResponse("<script>alert('当前密码错误！');history.back();</script>")
        else:
            l = LDAPTool()
            if l.ldap_update_pass(username,password,newpassword):
                return HttpResponse("<script>alert('密码修改成功');history.go(-2);</script>")
            else:
                return HttpResponse("靠，代码出错了！")


def ldapValidate(username,password):
    ldaptool = LDAPTool()
    if ldaptool.ldap_get(username,password):
        return True
    else:
        return False

def gotochpass(request):
    return render(request,'gotochpass.html')

def chpass(request):
    return render(request,'chpass.html')

def getvalicode(request):
    if request.POST:
        email = request.POST.get('email')
        emailldap = LDAPTool()
        if emailldap.ldap_search_mail(email):
            mailcode = ''.join([choice(string.ascii_letters+string.digits) for i in range(16)])
            timestamp = int(time.time())
            mcode,created = MailCode.objects.get_or_create(email=email)
            if created:
                mcode.mail_code = mailcode
                mcode.createtime = timestamp
                mcode.updatetime = timestamp
                mcode.save()
            else:
                updatetime = mcode.updatetime
                if timestamp - updatetime <= 86400:
                    return render(request, 'chpass.html')
                mcode.mail_code = mailcode
                mcode.updatetime = timestamp
                mcode.save()

            sendmail([email],mailcode)
            return render(request,'chpass.html')
        else:
            return HttpResponse("<script>alert('邮箱地址不对吧亲。。！！！');history.back();</script>")

def chpassHandle(request):
    if request.POST:
        username = request.POST.get('username')
        email = request.POST.get('email')
        umailcode = request.POST.get('mailcode')
        newpass = request.POST.get('newpass')
        confirmpass = request.POST.get('confirmpass')

        if username and newpass:
            email_objs = MailCode.objects.filter(email=email).order_by('-updatetime')
            timenow = int(time.time())
            if len(email_objs) > 0:
                email_obj = email_objs[0]
                updatetime = email_obj.updatetime
                if timenow - updatetime > 86400:
                    return HttpResponse("<script>alert('验证码已过期，请重新获取 ！！！');history.back();</script>")
                else:
                    emailcode = email_obj.mail_code
                    if umailcode != emailcode:
                        return HttpResponse("<script>alert('验证码错误，请检查输入与邮件中的验证码 ！！！');history.back();</script>")

            if newpass != confirmpass:
                return HttpResponse("<script>alert('新密码两次输入不匹配！');history.back();</script>")

            l = LDAPTool()
            result = l.reset_user_pass(username, newpass)
            if result[0]:
                return HttpResponse("<script>alert('修改密码成功！！！');window.location.href='http://192.168.10.212:8000';</script>")
            else:
                return HttpResponse("修改出错了，找你运维哥哥吧！！！DEBUG_RESULT："+result[1])
        return HttpResponse("<script>alert('你确定写姓名和密码了？？？你运维哥哥也帮不了你啊！！！');history.back();</script>")

