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
from django.conf.urls import url,include
from django.contrib import admin
from autodeploy import urls as auto_urls
import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', views.login, name='login'),
    url(r'^home/$', views.loginHandle, name='home'),
    url(r'^changepass/$', views.changepass, name='changepass'),
    url(r'^changepass_handle/$', views.changepassHandle, name='changepass_handle'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^gotochpass/$', views.gotochpass, name='gotochpass'),
    url(r'^getvalicode/$', views.getvalicode, name='getvalicode'),
    url(r'^chpass/$', views.chpass, name='chpass'),
    url(r'^chpass_handle/$', views.chpassHandle,name='chpass_handle'),

    url(r'^autodeploy/',include(auto_urls,namespace='autodeploy'))
]
