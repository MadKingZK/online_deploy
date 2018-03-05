#-*- coding: UTF-8 -*-
from django.contrib import admin
import models
# Register your models here.

class CommentAdmin(admin.ModelAdmin):
    admin.site.register(models.Host)
    admin.site.register(models.Environment)
    admin.site.register(models.Project)
    admin.site.register(models.Task)
    admin.site.register(models.Log)

