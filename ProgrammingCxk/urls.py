"""ProgrammingCxk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from esports.views import api
from esports.views import frontend
from esports.views.api import Auth as AuthApi
from esports.views.api import Team as TeamApi
from esports.views.api import User as UserApi
from esports.views.frontend import Message as MsgPage
from esports.views.frontend import Team as TeamPage
from esports.views.frontend import User as UserPage

urlpatterns = [
    # 前端页面
    path('admin/', admin.site.urls),
    path('', frontend.index, name='index'),
    path('login/', frontend.login, name='login'),
    path('register/', frontend.register, name='register'),
    # 用户
    path('user/', UserPage.detail, name='user-detail'),
    # 战队
    path('team/add/', TeamPage.add, name='team-add'),
    path('team/detail/<int:team_id>/', TeamPage.detail, name='team-detail'),
    path('team/change/<int:team_id>/', TeamPage.change, name='team-change'),
    path('team/list/', TeamPage.list, name='team-list'),
    path('team/app/<int:app_id>/', TeamPage.app, name='team-app'),
    path('team/member/detail/<int:person_id>/', TeamPage.member_detail, name='team-member'),
    # 消息
    path('msg/list/', MsgPage.list, name='msg-list'),
    # api
    # 用户
    path('api/login/', AuthApi.login, name='api-login'),
    path('api/logout/', AuthApi.logout, name='api-logout'),
    path('api/register/', AuthApi.register, name='api-register'),
    path('api/user/change/', UserApi.change, name='api-user-change'),
    # 战队
    path('api/team/add/', TeamApi.add, name='api-team-add'),
    path('api/team/change/', TeamApi.change, name='api-team-change'),
    path('api/team/disband/', TeamApi.disband, name='api-team-disband'),
    path('api/team/list/', TeamApi.list, name='api-team-list'),
    path('api/team/member/list/<int:team_id>/', TeamApi.member_list, name='api-team-member-list'),
    path('api/team/join/', TeamApi.join, name='api-team-join'),
    path('api/team/remove/', TeamApi.remove_member, name='api-team-remove'),
    path('api/team/app/', TeamApi.application, name='api-team-app'),
    path('api/team/exit/', TeamApi.exit, name='api-team-exit'),
    # 教练
    path('api/coach/chose/', api.coach_chose, name='api-coach-chose'),
    # 消息
    path('api/msg/last/', api.Message.last, name='api-msg-last'),
    path('api/msg/list/', api.Message.list, name='api-msg-list'),
    path('api/msg/read/', api.Message.read, name='api-msg-read'),
    # 智能BP
    path('bp/', frontend.bp, name='bp'),
]
