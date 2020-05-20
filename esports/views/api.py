from django.contrib import auth
from django.contrib.auth.models import User as DjangoUser
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from esports.models import Person, Team as TeamModel
from esports.views.frontend import manager_required
from utils.tools import json_success, json_failed, json_list


def str_validate(string: str) -> bool:
    for ch in string:
        if ord(ch) > 0xff:
            return False
    if not string.isprintable():
        return False
    return True


def password_validate(password: str, repass: str) -> (bool, int, str):
    if password != repass:
        return (False, 1, '两次密码不一致')

    if not str_validate(password):
        return (False, 2, '密码必须由英文字母、数字、符号组成')

    if len(password) < 8:
        return (False, 3, '密码不能少于8位')

    if password.isdigit():
        return (False, 3, '密码不能全是数字')

    return (True, 0, '')


class User:
    @staticmethod
    def change(request):
        avatar: str = request.POST.get('avatar').strip()
        nickname: str = request.POST.get('nickname').strip()
        gender: str = request.POST.get('gender')
        phone: str = request.POST.get('phone')
        email: str = request.POST.get('email')
        password: str = request.POST.get('password')
        repass: str = request.POST.get('repass')

        user: DjangoUser = request.user
        user.person.avatar = avatar
        user.person.name = nickname
        user.person.gender = gender
        if Person.objects.filter(phone=phone).exclude(id=user.person.id).exists():
            return json_failed(4, '电话号码已被使用')
        user.person.phone = phone
        if Person.objects.filter(email=email).exclude(id=user.person.id).exists():
            return json_failed(4, '电子邮箱已被使用')
        user.person.email = email
        if password != '' or repass != '':
            pwd_valid: (bool, int, str) = password_validate(password, repass)
            if not pwd_valid[0]:
                return json_failed(pwd_valid[1], pwd_valid[2])
            user.set_password(password)
        user.save()
        user.person.save()
        auth.login(request, user)

        return json_success({})


class Auth:
    @staticmethod
    def login(request):
        username: str = request.POST.get('username')
        password: str = request.POST.get('password')
        user: DjangoUser = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return json_success({})
        else:
            return json_failed(1, '')

    @staticmethod
    def logout(request):
        auth.logout(request)
        return json_success({})

    @staticmethod
    def register(request):
        username: str = request.POST.get('username').strip()
        nickname: str = request.POST.get('nickname').strip()
        gender: str = request.POST.get('gender')
        phone: str = request.POST.get('phone')
        email: str = request.POST.get('email')
        type_: str = request.POST.get('type')
        password: str = request.POST.get('password')
        repass: str = request.POST.get('repass')

        if not str_validate(username):
            return json_failed(2, '用户名必须由英文字母、数字、符号组成')

        pwd_valid: (bool, int, str) = password_validate(password, repass)
        if not pwd_valid[0]:
            return json_failed(pwd_valid[1], pwd_valid[2])

        if DjangoUser.objects.filter(username=username).exists():
            return json_failed(1, '用户名已存在')

        if Person.objects.filter(phone=phone).exists():
            return json_failed(4, '电话号码已被使用')

        if Person.objects.filter(email=email).exists():
            return json_failed(4, '电子邮箱已被使用')

        else:
            user: DjangoUser = DjangoUser.objects.create_user(
                username=username,
                password=password,
            )
            user.save()
            person: Person = Person.objects.create(
                user=user,
                name=nickname,
                gender=gender,
                phone=phone,
                email=email,
                type=type_,
                data='{}',
            )
            person.save()
            auth.login(request, user)
            return json_success({})


class Team:
    @staticmethod
    @manager_required
    def add(request):
        name: str = request.POST.get('teamname').strip()
        desc: str = request.POST.get('desc').strip()
        avatar: str = request.POST.get('avatar').strip()

        if TeamModel.objects.filter(name=name).exists():
            return json_failed(1, '战队名已被使用')

        team: TeamModel = TeamModel.objects.create(
            name=name,
            desc=desc,
            manager=request.user,
        )

        if avatar != '':
            team.avatar = avatar

        team.save()

        return json_success({
            'redirect': reverse('team-detail', args=(team.id,)),
        })

    @staticmethod
    @manager_required
    def change(request):
        team_id: str = request.POST.get('id')
        name: str = request.POST.get('teamname').strip()
        desc: str = request.POST.get('desc').strip()
        avatar: str = request.POST.get('avatar').strip()
        coach: str = request.POST.get('coach', '')

        team: TeamModel = TeamModel.objects.filter(id=team_id).first()

        if request.user != team.manager:
            raise PermissionDenied
        if TeamModel.objects.filter(name=name).exclude(id=team_id).exists():
            return json_failed(1, '战队名已被使用')

        team.name = name
        team.desc = desc
        if avatar != '':
            team.avatar = avatar
        team.coach_id = coach if coach != '' else None
        team.save()

        return json_success({})

    @staticmethod
    @manager_required
    def disband(request):
        team_id: str = request.POST.get('id')

        team: TeamModel = TeamModel.objects.filter(id=team_id).first()

        if request.user != team.manager:
            raise PermissionDenied

        team.delete()

        return json_success({})

    @staticmethod
    def list(request):
        teams: TeamModel = TeamModel.objects.select_related('manager', 'coach')
        team_list = []
        for team in teams:
            team_list.append({
                'id': team.id,
                'name': team.name,
                'manager': team.manager.person.name,
                'coach': team.coach.person.name if team.coach else '暂无',
            })

        return json_list(team_list)

    @staticmethod
    def join(request):
        user_id: str = request.POST.get('id')
        # TODO 加入战队；建表：战队申请


def coach_chose(request):
    coach_id: str = request.POST.get('id').strip()
    coach: Person = Person.objects.filter(id=coach_id, type=Person.PERSON_TYPE_COACH).first()
    if coach is None:
        return json_failed(1, '教练不存在')

    return json_success({
        'coachId': coach.id,
        'coachName': coach.name,
    })
