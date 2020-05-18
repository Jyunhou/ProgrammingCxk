from django.shortcuts import render, redirect

from utils.tools import authenticated_required


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
