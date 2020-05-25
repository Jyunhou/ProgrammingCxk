from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import render, redirect

from esports.models import Person, Team as TeamModel
from utils.tools import authenticated_required


def manager_required(func):
    def wrapper(request, *args, **kwargs):
        if not (request.user.person.type == Person.PERSON_TYPE_MANAGER):
            raise PermissionDenied
        return func(request, *args, **kwargs)

    return wrapper


def index(request):
    return render(request, 'base.html')


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

        return render(request, 'team/detail.html', {
            'team': team,
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


class Message:
    @staticmethod
    @authenticated_required
    def list(request):
        pass
