from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import render, redirect

from esports.models import Person, Team as TeamModel, TeamApplication
from utils.tools import authenticated_required


def manager_required(func):
    def wrapper(request, *args, **kwargs):
        if not (request.user.person.type == Person.PERSON_TYPE_MANAGER):
            raise PermissionDenied
        return func(request, *args, **kwargs)

    return wrapper


def index(request):
    return render(request, 'base.html')

def bp(request):
    return render(request, 'bp.html')


def login(request):
    if request.user.is_authenticated:
        return redirect(User.detail)
    else:
        return render(request, 'login.html')


def register(request):
    if request.user.is_authenticated:
        return redirect(index)
    else:
        return render(request, 'register.html')


class User:
    @staticmethod
    @authenticated_required
    def detail(request):
        return render(request, 'user/detail.html')


class Team:
    @staticmethod
    @authenticated_required
    @manager_required
    def add(request):
        return render(request, 'team/add.html')

    @staticmethod
    def detail(request, team_id: int):
        team: TeamModel = TeamModel.objects.filter(id=team_id).first()
        if not team:
            raise Http404()

        in_app: bool = TeamApplication.objects.filter(
            user=request.user, team=team,
            status=TeamApplication.STATUS_PENDING
        ).exists()

        return render(request, 'team/detail.html', {
            'team': team,
            'in_app': in_app,  # 正在申请加入
        })

    @staticmethod
    @authenticated_required
    @manager_required
    def change(request, team_id: int):
        team: TeamModel = TeamModel.objects.filter(id=team_id).first()
        if not team:
            raise Http404()
        if team.manager != request.user:
            raise PermissionDenied

        return render(request, 'team/change.html', {
            'team': team,
        })

    @staticmethod
    def list(request):
        return render(request, 'team/list.html')

    @staticmethod
    def app(request, app_id):
        app: TeamApplication = TeamApplication.objects.filter(id=app_id).first()

        if app is None:
            raise Http404()

        return render(request, 'team/app.html', {
            'app': app,
        })


class Message:
    @staticmethod
    @authenticated_required
    def list(request):
        return render(request, 'msg/list.html')
