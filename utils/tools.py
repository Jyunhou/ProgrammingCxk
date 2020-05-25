import json
from datetime import datetime, date
from typing import List, Dict

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render, redirect

from ProgrammingCxk.settings import TIMEZONE

PAGE_LIMIT: int = 10


def authenticated_required(func):
    """检查登录装饰器"""

    def wrapper(request, *args, **kwargs):
        if not (request.user.is_authenticated and request.user.is_active):
            return redirect('/login/?next=' + request.get_full_path())
        return func(request, *args, **kwargs)

    return wrapper


def json_response(data: Dict) -> HttpResponse:
    """返回 json 格式"""

    class CJsonEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.astimezone(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(obj, date):
                return obj.strftime('%Y-%m-%d')
            else:
                return json.JSONEncoder.default(self, obj)

    return HttpResponse(
        json.dumps(data, cls=CJsonEncoder),
        content_type='application/json'
    )


def json_success(data: List or Dict) -> HttpResponse:
    """返回成功的响应"""
    return json_response({
        'code': 0,
        'msg': '',
        'data': data,
    })


def json_failed(errcode: int, msg: str) -> HttpResponse:
    """
    返回失败的响应
    :param errcode 错误代码
    :param msg 错误信息
    """
    return json_response({
        'code': errcode,
        'msg': msg,
        'data': {},
    })


def json_list(data: List) -> HttpResponse:
    """
    返回列表成功的响应
    :param data 列表数据
    """
    return json_response({
        'code': 0,
        'msg': '',
        'count': len(data),
        'data': data,
    })


def permission_error(request, permission: str) -> HttpResponse:
    """
    权限错误时返回错误页面
    :param request
    :param permission 需要但缺少的权限名称
    """
    return render(request, 'pass', {'permission': permission})


def base_paging(request, object_list, per_page=PAGE_LIMIT, indicator=True):
    """基础分页"""
    paginator = Paginator(object_list, per_page)
    page = request.GET.get('page') or 1
    try:
        page = paginator.page(page)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    if indicator:
        cur = page.number
        total = paginator.num_pages
        indexs = tuple(paginator.page_range[cur - 3 if cur - 3 >= 0 else 0: cur + 3 if cur + 3 <= total else total])
        if 1 not in indexs:
            indexs = ((1,) if 2 in indexs else (1, '...')) + indexs
        if total not in indexs:
            indexs = indexs + ((total,) if (total - 1) in indexs else ('...', total))
    else:
        indexs = None

    return {
        'paginator': paginator,
        'page': page,
        'indexs': indexs,
    }


def api_paging(request, object_list, per_page=PAGE_LIMIT, to_list=False):
    """API分页"""
    data = base_paging(request, object_list, per_page, False)
    if int(request.GET.get('page', 0)) > data['paginator'].num_pages:
        data_list = []
    else:
        data_list = data['page'].object_list
    return {
        'list': list(data_list) if to_list else data_list,
        'num_pages': data['paginator'].num_pages,
        'has_next': data['page'].has_next(),
    }
