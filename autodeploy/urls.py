"""online_deploy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
import views
urlpatterns = [
    url(r'^stgdep$', views.stgdep, name='stg_dep'),
    url(r'^closestg/(?P<eid>\d)$', views.closestg, name='close_stg'),
    url(r'^gettask/(?P<id>\d+)$', views.getTask, name='get_task'),
    url(r'^ajxgetproj/(?P<id>\d+)$', views.ajxgetproj, name='ajxgetproj'),
    url(r'^posttask$', views.postTask, name='post_task'),
    url(r'getdepresult/(?P<id>\d+)$', views.getDepResult, name='get_dep_result'),
    url(r'^ajxstartdep/(?P<id>\d+)$', views.ajxStartDep, name='ajx_start_dep'),
    url(r'^ajxpushlog/(?P<fid>\d+),(?P<line_num>\d+)$', views.ajxPushLog, name='ajx_push_log'),
    url(r'^ajxdistribute/(?P<tid>\d+),(?P<hid>\d+)$', views.ajxDistribute2Host,name='ajx_distribute_host'),
    url(r'^taskli$', views.taskli, name='task_li'),
    url(r'^projectli$', views.projectli, name='project_li'),
    url(r'^taskdetail/(?P<tid>\d+)$', views.taskDetail, name='task_detail'),
    url(r'^ajxgetlog/(?P<pid>\d+),(?P<hid>\d+),(?P<tid>\d+)$', views.ajxGetLog, name='ajx_get_log'),
    url(r'^ajxloghandle/(?P<pid>\d+),(?P<hid>\d+),(?P<tid>\d+),(?P<line>\d+)$', views.ajxGetLogHandle,name='ajx_handle_log'),
    url(r'^alert_handle/(?P<tid>\d+)$', views.alert_handle, name='alert_handle')
]


