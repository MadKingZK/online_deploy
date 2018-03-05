#-*- coding: UTF-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Host(models.Model):
    ip = models.CharField(max_length=50)
    hostname = models.CharField(max_length=60)
    def __unicode__(self):
        return self.hostname

class Environment(models.Model):
    shortname = models.CharField(max_length=50)
    boot = models.CharField(max_length=50)
    name = models.CharField(max_length=60)
    status = models.IntegerField() #status 0 空闲；1 占用
    base_path = models.CharField(max_length=50)
    shellnm1 = models.CharField(max_length=30)
    shellnm2 = models.CharField(max_length=30)
    def __unicode__(self):
        return self.shortname

class Project(models.Model):
    shortname = models.CharField(max_length=50)
    name = models.CharField(max_length=60)
    realpath = models.CharField(max_length=50,null=True)
    servicename = models.CharField(max_length=15)
    container = models.CharField(max_length=10)
    environment = models.ForeignKey(Environment)
    hosts = models.ManyToManyField(Host)
    tcpport = models.IntegerField()
    dockerport = models.IntegerField(null=True)
    url = models.CharField(max_length=50, null=True)
    def __unicode__(self):
        return self.shortname

class Task(models.Model):
    creator = models.CharField(max_length=60)
    nick = models.CharField(max_length=15)
    createtime = models.IntegerField()
    gitbranch = models.CharField(max_length=50)
    comment = models.CharField(max_length=500)
    status = models.IntegerField() #status 0 任务进行中；1 任务成功结束 ； 2 任务失败
    project = models.ForeignKey('Project')
    environment = models.ForeignKey('Environment')
    def __unicode__(self):
        return self.creator

class Log(models.Model):
    content = models.CharField(max_length=1000)
    createtime = models.IntegerField()
    task = models.ForeignKey(Task)
    host = models.ForeignKey(Host,null=True)
    def __unicode__(self):
        return self.content

class MailCode(models.Model):
    email = models.CharField(max_length=50)
    mail_code = models.CharField(max_length=16)
    createtime = models.IntegerField(null=True)
    updatetime = models.IntegerField(null=True)
    def __unicode__(self):
        return self.email