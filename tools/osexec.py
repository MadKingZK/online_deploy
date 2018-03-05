#-*- coding: UTF-8 -*-
import subprocess

def execcommand(commandstr):
    process = subprocess.Popen(commandstr,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    res = process.communicate()
    toout = res[0]
    toerr = res[1]
    exitcode = process.poll()
    result = [toout,toerr,exitcode]
    return result

def gitclone(projectname,dstdir,addr):
    commandstr = ['git','clone','git+ssh://git@git.xxxx.net:8888/%s/%s.git' %(addr,projectname),dstdir]
    result = execcommand(commandstr)
    if not result[1]:
        return 0
    else:
        return result[1]
    
