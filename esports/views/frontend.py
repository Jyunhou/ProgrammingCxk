from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import render, redirect

from esports.models import Person, Team as TeamModel, TeamApplication, PersonDataRecord
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

        in_app: bool = False
        if request.user.is_authenticated:
            in_app = TeamApplication.objects.filter(
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


class Player:
    @staticmethod
    def detail(request, person_id: int):
        person = Person.objects.filter(id=person_id).first()

        if person is None:
            raise Http404()

        can_manage_info = False
        if request.user.person.type == Person.PERSON_TYPE_PLAYER:
            if request.user.person == person:
                can_manage_info = True
        elif request.user.person.type == Person.PERSON_TYPE_COACH:
            if request.user.person.team == person.team:
                can_manage_info = True
        elif request.user.person.type == Person.PERSON_TYPE_MANAGER:
            if request.user.person.team == person.team:
                can_manage_info = True

        return render(request, 'player/detail.html', {
            'player': person,
            'data': person.persondata,
            'can_manage_info': can_manage_info,
        })

    @staticmethod
    def list(request):
        return render(request, 'player/list.html')

    @staticmethod
    def record_list(request, player_id: int):
        player: Person = Person.objects.filter(id=player_id).first()

        if player is None:
            raise Http404()
        if player.type != Person.PERSON_TYPE_PLAYER:
            raise Http404()

        return render(request, 'player/record/list.html', {
            'player': player,
        })

    @staticmethod
    def add_record(request, player_id: int):
        player: Person = Person.objects.filter(id=player_id).first()

        if not player:
            raise Http404()

        return render(request, 'player/record/add.html', {
            'player': player,
        })

    @staticmethod
    def change_record(request, record_id: int):
        record: PersonDataRecord = PersonDataRecord.objects.filter(id=record_id).first()

        if not record:
            raise Http404()

        return render(request, 'player/record/change.html', {
            'record': record,
        })


class Message:
    @staticmethod
    @authenticated_required
    def list(request):
        return render(request, 'msg/list.html')
