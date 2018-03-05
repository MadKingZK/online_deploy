#-*- coding: UTF-8 -*-

from django.shortcuts import render_to_response,render
from django.template.context import RequestContext
from django.http.response import HttpResponse, HttpResponseRedirect
from django.core  import serializers
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from autodeploy.models import *
from tools.osexec import *
from utils import mp_render
from tools.ssh2 import ssh2
from tools.logtool import LogDump
import os,json


import time
import online_deploy.views
ssh1=1
ssh1 = ssh2('192.168.1.1', 22, 'eng')
#ssh2 = ssh2('', 22, '')
#logdump = LogDump('222')
logdir='/tmp/deplog/'
def check_login(func):
    def wrapper(request,*args,**kwargs):
        if not request.COOKIES.get('username'):
            return HttpResponseRedirect(reverse('login',))
        return func(request,*args,**kwargs)
    return wrapper

def check_ssh2_conn(func):
    def wapper(*args, **kwargs):
        res1 = ssh1.handler('pwd')
        #res2 = ssh2.handler('pwd')
        print '--_____-------___------>>>>',res1
        #print '--_____-------___------>>>>',res2
        if res1['status']==0:
            pass
        else:
            ssh1.ssh_conn()
        #if res2['status'] == 0:
        #    pass
        #else:
        #    ssh2.ssh_conn()
        return func(*args, **kwargs)
    return wapper


@check_login
def stgdep(request):
    environments = Environment.objects.all()
    for en in environments:
        #environment status 0 is 空闲， 1 is 使用中
        if en.status == 0:
            en.user = ' '
            en.usetime = ' '
            en.hstatus = '空闲'
            en.handle = '领用'
        if en.status == 1:
            try:
                task = Task.objects.filter(environment=en,status=0).order_by('-createtime').distinct()[0]
                en.user = task.nick
                en.usetime = task.createtime
                en.hstatus = '使用中'
                if request.COOKIES.get('username') == task.creator:
                    en.handle = '关闭'
            except Exception as e:
                print(e)

        en.save()
    return mp_render(request,'stg_dep.html',{'environments':environments})

@check_ssh2_conn
@check_login
def closestg(request,eid):
    environment = Environment.objects.get(pk=eid)
    environment.status = 0
    environment.save()
    return HttpResponseRedirect(reverse('autodeploy:stg_dep',))


@check_ssh2_conn
@check_login
def getTask(request,id):
    try:
        id = int(id)
    except Exception as e:
        print(e)
    return mp_render(request,'get_task.html',{'environment_id':id})

@check_ssh2_conn
@check_login
def ajxgetproj(request,id):
    environment = Environment.objects.get(pk=id)
    projects = Project.objects.filter(environment=environment).exclude(container=None)
    projects = serializers.serialize('json', projects)
    return HttpResponse(projects)

@check_ssh2_conn
@check_login
def postTask(request):
    environment_id = request.POST.get('environment_id')
    proj = request.POST.get('project')
    gitbranch = request.POST.get('gitbranch')
    comment = request.POST.get('content')
    #创建task
    creator = request.COOKIES.get('username','未知用户')
    nick = request.COOKIES.get('nick','')
    createtime = int(time.time())
    task = Task(creator=creator,nick=nick,createtime=createtime,gitbranch=gitbranch,
                comment=comment,status=0,project_id=proj,environment_id=environment_id)
    task.save()
    #更新Environment状态字段status
    environment = Environment.objects.get(pk=environment_id)
    environment.status = 1
    environment.save()

    return HttpResponseRedirect(reverse('autodeploy:get_dep_result',args=(task.id,)))

@check_ssh2_conn
@check_login
def getDepResult(request,id):
    task = Task.objects.get(pk=id)
    environment = task.environment
    project = task.project
    hosts = project.hosts.all()
    return mp_render(request,'stg_dep_results.html',
                    {'environment':environment,'project':project,'hosts':hosts,'tid':task.id,'gitbranch':task.gitbranch})


@check_login
@check_ssh2_conn
def ajxStartDep(request,id):

    task = Task.objects.get(pk=id)
    project = task.project
    environment = task.environment
    base_path = environment.base_path
    hosts = project.hosts.all()
    log = Log(task=task)

    project_dir = '%s%s'%(base_path,project.shortname)
    #ssh = get_ssh_conn(environment.shortname)
    ssh=ssh1
    print '===============>>>> \n',project_dir

    file_exi=ssh.file_exists(project_dir)
    print file_exi
    if not file_exi[0]:
    #clone 项目
        commandstr = 'echo "项目不存在,正在克隆... \n" >> %s%s.log' %(logdir,id)
        ssh.custom_handle(commandstr)
        print('----------------->>>>>>>>>>clone')
        log.createtime = int(time.time())
        addr = 'huoqiu'
        if project.shortname.find('dream') >= 0:
            addr = 'dream'
        if project.shortname.find('captain') >= 0:
            addr = 'captain'
        if str(environment)[:-2].strip() == 'docker':
            commandstr = 'git clone git@git.huoqiu.net:%s/%s.git %s' % (addr, project.shortname,project_dir)
        else:
            commandstr = 'git clone git+ssh://git@git.huoqiu.net:9522/%s/%s.git %s' % (addr, project.shortname,project_dir)
        print(commandstr)
        res = ssh.custom_handle(commandstr)

        if res[0]:
            content = '项目目录不存在，clone项目成功！'
            commandstr = 'echo "clone项目成功！\n" >> %s%s.log' % (logdir,id)
            ssh.custom_handle(commandstr)
            log.content = content
            log.save()
        else:
            content = '项目目录不存在，clone项目失败！%s' %res[1]
            commandstr = 'echo "clone项目失败！\n" >> %s%s.log' % (logdir,id)
            ssh.custom_handle(commandstr)
            log.content = content
            log.save()
            return HttpResponse(res[1])

    else:
        commandstr = 'echo "检查项目存在... \n" >> %s%s.log' % (logdir,id)
        print commandstr
        #ssh.custom_handle(commandstr)

    commandstr = 'echo "开始操作分支. \n" >> %s%s.log' % (logdir,id)
    ssh.custom_handle(commandstr)

    commandstr = 'echo "cd %s && git pull \n" >> %s%s.log' % (project_dir, logdir, id)
    ssh.custom_handle(commandstr)

    commandstr = 'echo "更新代码如下,如无内容则无代码更新... \n" >> %s%s.log' % (logdir,id)
    ssh.custom_handle(commandstr)
    ssh.custom_handle("cd %s && git pull >> %s%s.log" % (project_dir, logdir, id))
    res = ssh.custom_handle("cd %s && git checkout %s >> %s.log" % (project_dir, task.gitbranch, id))

    if not res[0]:
        log.createtime = int(time.time())
        content = '分支不存在,请检查分支!'
        print content
        commandstr = 'echo "分支不存在,请检查分支!\n" >> %s%s.log' % (logdir, id)
        ssh.custom_handle(commandstr)
        log.content = content
        log.save()
        return HttpResponse(content+res[1])

    #编译项目
    log = Log(task=task)
    log.createtime = int(time.time())
    scriptname = '%s%s'%(base_path,environment.shellnm1)
    #if project.realpath:
    #    project_dir = '%s%s'%(base_path,project.realpath)
    print '=============>',project_dir
    print('sh -x %s %s %s %s'% (scriptname,project_dir,task.gitbranch,environment.shortname))
    commandstr = 'echo "sh -x %s %s %s %s" >> %s%s.log' %(scriptname,project_dir,task.gitbranch,environment.shortname,logdir, id)
    ssh.custom_handle(commandstr)

    res = ssh.auto_deploy('sh %s %s %s %s | while read line; do echo $line; echo $line >> %s%s.log ;done' % (scriptname,project_dir,task.gitbranch,environment.shortname,logdir, id))
    print('------------>>>> %s',res)

    if res[0]:
        content = '项目编译成功'
        commandstr = 'echo "项目编译成功!\n" >> %s%s.log' % (logdir, id)
        ssh.custom_handle(commandstr)
        log.content = content
        log.save()
        return HttpResponse(0)
    else:
        content = '项目编译失败:%s'%res[1]
        commandstr = 'echo "项目编译失败!:%s\n" >> %s%s.log' % (res[1],logdir, id)
        ssh.custom_handle(commandstr)
        log.content = content
        log.save()
        return HttpResponse(res[1])


@check_login
@check_ssh2_conn
def ajxDistribute2Host(request,tid,hid):
    #部署项目到各台主机
    task = Task.objects.get(pk=tid)
    host = Host.objects.get(pk=hid)
    project = task.project
    base_path = task.environment.base_path
    environment=task.environment

    projpath = project.shortname
    project_dir = '%s%s'%(base_path,projpath)
    scriptname = '%s%s'%(base_path,environment.shellnm2)
    servicename = project.servicename
    #ssh = get_ssh_conn(environment.shortname)
    ssh = ssh1
    print('=-=-=-=sh -x %s %s %s %s %s %s'% (scriptname,host.hostname,project_dir,str(project.tcpport),servicename,environment.boot))
    commandstr = 'echo "sh -x %s %s %s %s %s %s \n" >> %s%s.log' % (scriptname,host.hostname,project_dir,str(project.tcpport),servicename,environment.boot,logdir, tid)
    ssh.custom_handle(commandstr)

    res = ssh.custom_handle('sh -x %s %s %s %s %s %s |  while read line; do echo $line; echo $line >> %s%s.log ;done '% (scriptname,host.hostname,project_dir,str(project.tcpport),servicename,environment.boot,logdir, tid))
    log = Log(task=task)
    log.createtime = int(time.time())
    log.host = host

    if res[0]:
        commandstr = 'echo "%s 部署完了,呵呵哒...! \n" >> %s%s.log' % (host.hostname, logdir, tid)
        ssh.custom_handle(commandstr)
        log.content = '%s deploy successful!'%host.hostname
        log.save()
        return HttpResponse(0)
    else:
        commandstr = 'echo "部署失败了,呵呵哒...!:%s\n" >> %s%s.log' % (res[1], logdir, tid)
        ssh.custom_handle(commandstr)
        log.content = "%s" % res[1]
        log.save()
        task.status = 1
        task.save()
        return HttpResponse(res[1])

@check_login
def projectli(request):
    result = []
    ens = Environment.objects.all()
    for en in ens:
        projs = Project.objects.filter(environment=en)
        for pr in projs:
            hosts = Host.objects.filter(project=pr)
            pr.hosts = hosts
        result.append([en,projs])
    return mp_render(request,'project_li.html',{'result':result})

@check_login
def taskli(request):
    creator = request.COOKIES.get('username')
    #task_list = Task.objects.filter(creator=creator).order_by('-createtime')
    task_list = Task.objects.all().order_by('-createtime')
    paginator = Paginator(task_list, 15)

    page = request.GET.get('page')
    try:
        tasks = paginator.page(page)
    except PageNotAnInteger:
        tasks = paginator.page(1)
    except EmptyPage:
        tasks = paginator.page(paginator.num_pages)
    return mp_render(request,'task_li.html',{'tasks':tasks})

@check_login
def taskDetail(request,tid):
    task = Task.objects.get(pk=tid)
    logs = Log.objects.filter(task=task)
    return mp_render(request,'task_detail.html',{'task':task,'logs':logs})

@check_ssh2_conn
def ajxGetLog(request,pid,tid,hid):
    task = Task.objects.get(pk=tid)
    project = Project.objects.get(pk=pid)
    host = Host.objects.get(pk=hid)
    base_path = task.environment.base_path
    #logdump = LogDump(task.id)
    print base_path
    #file=logdump.open()
    #logdump.dump(file,base_path)
    #logdump.close(file)
    scriptname = '%s%s'%(base_path,'get_log.sh')
    print('sh -x %s %s %s'%(scriptname,host.hostname,project.servicename))
    #file=logdump.open()
    #logdump.dump(file,'sh -x %s %s %s'%(scriptname,host.hostname,project.servicename))
    #logdump.close(file)
    ssh = get_ssh_conn(task.environment.shortname)
    res = ssh.custom_handle('sh -x %s %s %s'%(scriptname,host.hostname,project.servicename))
    if res[0]:
        try:
            if int(res[1]) > 20:
                line = int(res[1]) - 20
            if int(res[1]) == 0:
                line = 1
            print pid,hid,line
            print res
            return render(request,'logs.html',{'pid':pid,'hid':hid,'tid':tid,'line':line})

        except Exception as e:
            print(e)
            return HttpResponse(e)
    else:
        return HttpResponse(res[1])


def ajxGetLogHandle(request,pid,hid,tid,line):
    task=Task.objects.get(pk=tid)
    project = Project.objects.get(pk=pid)
    host = Host.objects.get(pk=hid)
    base_path = task.environment.base_path
    #logdump = LogDump(task.id)
    scriptname = '%s%s'%(base_path,'get_log.sh')
    ssh = get_ssh_conn(task.environment.shortname)
    print ('sh -x %s %s %s %s' % (scriptname, host.hostname, project.servicename, line))
    #file=logdump.open()
    #logdump.dump(file,'sh -x %s %s %s %s' % (scriptname, host.hostname, project.servicename, line))
    #logdump.close(file)
    res = ssh.custom_handle('sh -x %s %s %s %s'% (scriptname,host.hostname,project.servicename,line))
    print res
    if res[0] and res[1].strip():
        return HttpResponse(res[1])
    else:
        return HttpResponse(500)


def get_ssh_conn(environment_shortname):
    shortname=environment_shortname
    if shortname == 'stg':
        ssh = ssh2
    else:
        ssh = ssh1
    return ssh


@check_ssh2_conn
def alert_handle(request,tid):
    task = Task.objects.get(pk=tid)
    eid = task.environment_id
    emvironment = Environment.objects.get(pk=eid)
    shortname = emvironment.shortname
    ssh = get_ssh_conn(shortname)

    commandstr = 'grep "BUILD FAILURE" %s%s.log' %(logdir, tid)
    res = ssh.custom_handle(commandstr)
    print 'bbbbbbbbbb-------> ',res
    if res[0] == 0 and res[2] is not Null :
        alert_text = res[2]
    else:
        alert_text = '服务器提出了一个问题，请找运维寻求答案！'
    return HttpResponse(alert_text)

@check_ssh2_conn
def ajxPushLog(request,fid,line_num=1):
    #res=os.popen("cat /tmp/deplog/%s.log | wc -l"%fid)
    #real_line = res.read()
    #res.close()

    task = Task.objects.get(pk=fid)
    eid = task.environment_id
    emvironment = Environment.objects.get(pk=eid)
    #shortname = emvironment.shortname
    #ssh = get_ssh_conn(shortname)
    ssh = ssh1
    res = os.popen("cat /tmp/deplog/%s.log | wc -l" % fid)
    res = res.read()
    real_line = res
    print res
    line = ""
    line_num = int(line_num)
    read_line = int(real_line)

    if line_num <= read_line:

        real_read_num = 30 if read_line - line_num >= 30 else read_line - line_num
        for current_line in range(1, real_read_num+1):
            print("sed -n '%dp' /tmp/deplog/%s.log" % (line_num+(current_line-1), fid))
            res = os.popen("sed -n '%dp' /tmp/deplog/%s.log" % (line_num+(current_line-1), fid))
            templine = res.read()

            #res = ssh.custom_handle("sed -n '%dp' /tmp/deplog/%s.log" % (line_num+(current_line-1), fid))
            #templine = res[1]
            print templine
            line = line + templine + '<br />'
        read_num = real_read_num
        #res.close()
        if '部署完了,呵呵哒...' in line or '部署失败了,呵呵哒...' in line:
            re_dic = {"success":3,"data":line,"read_num":read_num}
        else:
            re_dic = {"success":1,"data":line,"read_num":read_num}

        re_dic = json.dumps(re_dic)
        return HttpResponse(re_dic)

    else:
        re_dic = {"success":2}
        re_dic = json.dumps(re_dic)
        return HttpResponse(re_dic)
