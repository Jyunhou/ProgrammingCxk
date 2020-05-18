from django.contrib import auth
from django.contrib.auth.models import User as DjangoUser

from utils.tools import json_success, json_failed


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
        first_name: str = request.POST.get('firstname')
        password: str = request.POST.get('password')
        repass: str = request.POST.get('repass')

        user: DjangoUser = request.user
        user.first_name = first_name
        if password != '' or repass != '':
            pwd_valid: (bool, int, str) = password_validate(password, repass)
            if not pwd_valid[0]:
                return json_failed(pwd_valid[1], pwd_valid[2])
            user.set_password(password)
        user.save()
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
        username: str = request.POST.get('username')
        first_name: str = request.POST.get('firstname')
        password: str = request.POST.get('password')
        repass: str = request.POST.get('repass')

        if not str_validate(username):
            return json_failed(2, '用户名必须由英文字母、数字、符号组成')

        pwd_valid: (bool, int, str) = password_validate(password, repass)
        if not pwd_valid[0]:
            return json_failed(pwd_valid[1], pwd_valid[2])

        if DjangoUser.objects.filter(username=username).exists():
            return json_failed(1, '用户名已存在')

        else:
            user: DjangoUser = DjangoUser.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
            )
            user.save()
            auth.login(request, user)
            return json_success({})
