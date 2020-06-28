from datetime import date

from django.contrib import auth
from django.contrib.auth.models import User as DjangoUser
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from esports.models import Message as MsgStatus, PersonDataRecord, PersonData
from esports.models import Person as PersonModel
from esports.models import Team as TeamModel
from esports.models import TeamApplication, ReceiveMessage, SendMessage
from esports.views.frontend import manager_required
from utils.tools import json_success, json_failed, json_list, api_paging


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
        if PersonModel.objects.filter(phone=phone).exclude(id=user.person.id).exists():
            return json_failed(4, '电话号码已被使用')
        user.person.phone = phone
        if PersonModel.objects.filter(email=email).exclude(id=user.person.id).exists():
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

        if PersonModel.objects.filter(phone=phone).exists():
            return json_failed(4, '电话号码已被使用')

        if PersonModel.objects.filter(email=email).exists():
            return json_failed(4, '电子邮箱已被使用')

        else:
            user: DjangoUser = DjangoUser.objects.create_user(
                username=username,
                password=password,
            )
            user.save()
            person: PersonModel = PersonModel.objects.create(
                user=user,
                name=nickname,
                gender=gender,
                phone=phone,
                email=email,
                type=type_,
            )
            person.data = PersonData.objects.create(person=person)
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
        teams = TeamModel.objects.select_related('manager', 'coach')
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
    def member_list(request, team_id: int):
        limit: int = int(request.GET.get('limit'))

        team: TeamModel = TeamModel.objects.filter(id=team_id).first()

        member_list = []
        paged = api_paging(request, team.person_set.all(), limit)
        for member in paged['list']:
            member_list.append({
                'id': member.id,
                'name': member.name,
                'gender': '男' if member.gender else '女',
            })

        return json_list(member_list)

    @staticmethod
    def join(request):
        user_id: str = request.POST.get('userId')
        team_id: str = request.POST.get('teamId')
        desc: str = request.POST.get('desc')

        user: DjangoUser = DjangoUser.objects.filter(id=user_id).first()
        team: TeamModel = TeamModel.objects.filter(id=team_id).first()

        if user is None or team is None:
            return json_failed(1, '用户或战队不存在')
        if user.person.team is not None:
            return json_failed(2, '已经加入了战队')
        if user.person.type != PersonModel.PERSON_TYPE_PLAYER:
            return json_failed(3, '只有选手可以加入战队')
        if TeamApplication.objects.filter(
                user=user, team=team, status=TeamApplication.STATUS_PENDING).exists():
            return json_failed(4, '待批准中')

        app: TeamApplication = TeamApplication.objects.create(
            user=user,
            team=team,
            desc=desc,
        )
        button_html = '<button class="layui-btn layui-btn-xs" onclick="window.location=\'%s\'">前往处理</button>' \
                      % reverse('team-app', args=(app.id,))
        generate_message(
            '战队加入申请',
            '%s申请加入您的战队“%s”：<br>%s%s' % (user.person.name, team.name, desc, button_html),
            None, team.manager,
        )

        return json_success({})

    @staticmethod
    @manager_required
    def remove_member(request):
        member_id: str = request.POST.get('memberId')

        member: PersonModel = PersonModel.objects.filter(id=member_id).first()
        team: TeamModel = member.team

        member.team = None
        member.save()

        generate_message("战队成员变动", "你已被移除出战队“%s”。" % team.name, None, member.user)

        return json_success({})

    @staticmethod
    def application(request):
        app_id: str = request.POST.get('id')
        accept: bool = request.POST.get('accept') == 'true'

        app: TeamApplication = TeamApplication.objects.filter(id=app_id).first()
        if accept:
            app.status = TeamApplication.STATUS_ACCEPT
            app.user.person.team = app.team
            app.user.person.save()
            title = '战队加入申请已通过'
            button_html = '<button class="layui-btn layui-btn-xs" onclick="window.location=\'%s\'">查看战队</button>' \
                          % reverse('team-detail', args=(app.team.id,))
            content = '您申请加入战队“%s”已经通过。%s' % (app.team.name, button_html)
        else:
            app.status = TeamApplication.STATUS_REFUSE
            title = '战队加入申请被拒绝'
            content = '您申请加入战队“%s”已被拒绝。' % app.team.name
        app.save()
        generate_message(title, content, None, app.user)

        return json_success({})

    @staticmethod
    def exit(request):
        team_id: str = request.POST.get('teamId')

        team: TeamModel = TeamModel.objects.filter(id=team_id).first()

        if request.user.person.team != team:
            return json_failed(1, '战队错误')
        request.user.person.team = None
        request.user.person.save()

        generate_message(
            '战队成员退出',
            '%s（用户名：%s）已退出您的战队“%s”。' % (request.user.person.name, request.user.username, team.name),
            None, team.manager,
        )

        return json_success({})


def coach_chose(request):
    coach_id: str = request.POST.get('id').strip()
    coach: PersonModel = PersonModel.objects.filter(id=coach_id, type=PersonModel.PERSON_TYPE_COACH).first()
    if coach is None:
        return json_failed(1, '教练不存在')

    return json_success({
        'coachId': coach.id,
        'coachName': coach.name,
    })


class Player:
    @staticmethod
    def list(request):
        persons = PersonModel.objects.filter(type=PersonModel.PERSON_TYPE_PLAYER).select_related('persondata')
        person_list = []
        for person in persons:
            person_list.append({
                'id': person.id,
                'name': person.name,
                'gender': '男' if person.gender else '女',
                'team': person.team.name if person.team is not None else '暂无',
                'win_rate': str(person.persondata.win_rate) + '%',
            })

        return json_list(person_list)

    @staticmethod
    def record_list(request, player_id: int):
        player: PersonModel = PersonModel.objects.filter(id=player_id).first()
        records = player.persondata.persondatarecord_set.all()
        record_list = []

        for record in records:
            record_list.append({
                'id': record.id,
                'win': '胜利' if record.win else '失败',
                'kill': record.kill,
                'assist': record.assist,
                'death': record.death,
                'reinforce': record.reinforce,
                'money': record.money,
                'tower': record.tower,
                'type': record.get_type_display(),
                'date': date.strftime(record.date, '%Y年%m月%d日'),
            })

        return json_list(record_list)

    @staticmethod
    def add_record(request, player_id: int):
        win: bool = request.POST.get('win', '').strip() == 'on'
        kill: str = request.POST.get('kill').strip()
        assist: str = request.POST.get('assist').strip()
        death: str = request.POST.get('death').strip()
        reinforce: str = request.POST.get('reinforce').strip()
        money: str = request.POST.get('money').strip()
        tower: str = request.POST.get('tower').strip()
        type: str = request.POST.get('type')
        date: str = request.POST.get('date')

        player: PersonModel = PersonModel.objects.filter(id=player_id).first()

        PersonDataRecord.objects.create(
            data=player.persondata,
            win=win,
            kill=kill,
            assist=assist,
            death=death,
            reinforce=reinforce,
            money=money,
            tower=tower,
            type=type,
            date=date,
        )

        Player.update_record(player.persondata)

        return json_success({})

    @staticmethod
    def change_record(request, record_id: int):
        win: bool = request.POST.get('win').strip() == 'on'
        kill: str = request.POST.get('kill').strip()
        assist: str = request.POST.get('assist').strip()
        death: str = request.POST.get('death').strip()
        reinforce: str = request.POST.get('reinforce').strip()
        money: str = request.POST.get('money').strip()
        tower: str = request.POST.get('tower').strip()
        type: str = request.POST.get('type')
        date: str = request.POST.get('date')

        record: PersonDataRecord = PersonDataRecord.objects.filter(id=record_id).first()

        record.win = win
        record.kill = kill
        record.assist = assist
        record.death = death
        record.reinforce = reinforce
        record.money = money
        record.tower = tower
        record.type = type
        record.date = date
        record.save()

        Player.update_record(record.data)

    @staticmethod
    def update_record(data: PersonData):
        data.win = 0
        data.kill = 0
        data.assist = 0
        data.death = 0
        data.reinforce = 0
        data.money = 0
        data.tower = 0
        for record in data.persondatarecord_set.all():
            data.win += record.win
            data.kill += record.kill
            data.assist += record.assist
            data.death += record.death
            data.reinforce += record.reinforce
            data.money += record.money
            data.tower += record.tower

        data.win_rate = int(float(data.win) / len(data.persondatarecord_set.all()) * 100)
        print(data.win_rate)
        data.save()


class Message:
    MAX_LAST_NUM: int = 10

    @staticmethod
    def last(request):
        if not request.user.is_authenticated:
            return json_failed(1, '未登录')

        msgs = ReceiveMessage.objects.filter(
            user=request.user,
            is_read=False,
            status=MsgStatus.STATUS_NORMAL,
        ).select_related('send_message').order_by('-datetime')[:Message.MAX_LAST_NUM]

        data = []
        for msg in msgs:
            data.append({
                'href': reverse('msg-list') + '?id=' + str(msg.id),
                'title': msg.send_message.title,
                'content': msg.send_message.content,
                'datetime': msg.send_message.datetime,
            })

        return json_success(data)

    @staticmethod
    def list(request):
        if not request.user.is_authenticated:
            return json_failed(1, '未登录')

        limit: int = int(request.GET.get('limit'))

        msgs = ReceiveMessage.objects.filter(
            user=request.user,
            status=MsgStatus.STATUS_NORMAL,
        ).select_related('send_message').order_by('-datetime')

        paged = api_paging(request, msgs, limit)

        data = []
        for msg in paged['list']:
            data.append({
                'id': msg.id,
                'title': msg.send_message.title,
                'content': msg.send_message.content,
                'datetime': msg.send_message.datetime,
                'isRead': msg.is_read,
                'type': 1,
            })

        return json_list(data)

    @staticmethod
    def read(request):
        msg_id: str = request.POST.get('id')

        msg: ReceiveMessage = ReceiveMessage.objects.filter(id=msg_id).first()
        msg.is_read = True
        msg.save()

        return json_success({})


def generate_message(title: str, content: str, from_user: DjangoUser or None, to_user: DjangoUser
                     ) -> (SendMessage, ReceiveMessage):
    send_msg: SendMessage = SendMessage.objects.create(
        title=title,
        content=content,
        user=from_user,
    )
    receive_msg: ReceiveMessage = ReceiveMessage.objects.create(
        user=to_user,
        send_message=send_msg,
    )

    return (send_msg, receive_msg)
