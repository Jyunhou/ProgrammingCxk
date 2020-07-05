import json

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from esports.models import Team
from .views import api


class WebPageTestCase(TestCase):
    """测试各页面正常访问"""

    def get(self, view_name: str):
        """基础测试方法，测试视图对应的URL访问时，返回状态码小于400"""
        self.assertLess(
            Client().get(
                reverse(view_name)
            ).status_code, 400
        )

    def test_index(self):
        self.get('index')

    def test_login(self):
        self.get('login')

    def test_register(self):
        self.get('register')

    def test_user_detail(self):
        self.get('user-detail')

    def test_player_list(self):
        self.get('player-list')

    def test_team_add(self):
        self.get('team-add')

    def test_team_list(self):
        self.get('team-list')

    def test_msg_list(self):
        self.get('msg-list')


"""测试各API"""


class UtilTestCase(TestCase):
    def test_str_validate(self):
        self.assertTrue(api.str_validate('yonghuming'))
        self.assertTrue(api.str_validate('_username'))
        self.assertTrue(api.str_validate('_user321'))
        self.assertTrue(api.str_validate('123'))
        self.assertFalse(api.str_validate('中文用户名'))

    def test_password_validate(self):
        self.assertFalse(api.password_validate('1234qwer', '1234qwert')[0])
        self.assertFalse(api.password_validate('中文密码', '中文密码')[0])
        self.assertFalse(api.password_validate('abc', 'abc')[0])
        self.assertFalse(api.password_validate('12345678', '12345678')[0])
        self.assertTrue(api.password_validate('1234qwer', '1234qwer')[0])


class ApiTester(TestCase):
    def api_success(self, view_name: str, param: dict):
        """基础API测试方法，测试视图对应的API访问时，返回代码为0，即为通过"""
        data = json.loads(Client().post(
            reverse(view_name), param
        ).content)
        self.assertEqual(data['code'], 0)

    def api_fail(self, view_name: str, param: dict):
        """基础API测试方法，测试视图对应的API访问时，返回代码非0，即为通过"""
        data = json.loads(Client().post(
            reverse(view_name), param
        ).content)
        self.assertNotEqual(data['code'], 0)

    def auth_success(self, view_name: str, param: dict, username: str, password: str):
        """登录状态的成功测试"""
        client = Client()
        client.login(username=username, password=password)
        data = json.loads(client.post(
            reverse(view_name), param
        ).content)
        self.assertEqual(data['code'], 0)

    def auth_fail(self, view_name: str, param: dict, username: str, password: str):
        """登录状态的失败测试"""
        client = Client()
        client.login(username=username, password=password)
        response = client.post(reverse(view_name), param)
        if response.status_code != 403:
            data = json.loads(response.content)
            self.assertNotEqual(data['code'], 0)


class AuthTestCase(TestCase):

    def test_0(self):
        # 1 选手账户注册
        ApiTester().api_success('api-register', {
            'username': 'zs3',
            'nickname': '张三',
            'gender': '1',
            'phone': '13214684992',
            'email': '13214684992@qq.com',
            'type': '1',
            'password': 'zs0123456',
            'repass': 'zs0123456',
        })
        ApiTester().api_success('api-register', {
            'username': 'wf5',
            'nickname': '魏凡',
            'gender': '1',
            'phone': '13214684972',
            'email': '1321468399@qq.com',
            'type': '1',
            'password': 'wf0123456',
            'repass': 'wf0123456',
        })

        # 2 经理账户注册
        ApiTester().api_success('api-register', {
            'username': 'jl4',
            'nickname': '李四',
            'gender': '0',
            'phone': '13214684993',
            'email': '1321468450@qq.com',
            'type': '3',
            'password': 'ls0123456',
            'repass': 'ls0123456',
        })
        ApiTester().api_success('api-register', {
            'username': 'wb8',
            'nickname': '魏八',
            'gender': '1',
            'phone': '13214154699',
            'email': '1351465491@qq.com',
            'type': '3',
            'password': 'wb123456',
            'repass': 'wb123456',
        })
        ApiTester().api_success('api-register', {
            'username': 'wb9',
            'nickname': '魏就',
            'gender': '1',
            'phone': '13214125699',
            'email': '1357865491@qq.com',
            'type': '3',
            'password': 'wb123456',
            'repass': 'wb123456',
        })

        # 3 教练账户注册
        ApiTester().api_success('api-register', {
            'username': 'ww5',
            'nickname': '王五',
            'gender': '1',
            'phone': '13214684994',
            'email': '1321468451@qq.com',
            'type': '2',
            'password': 'ww0123456',
            'repass': 'ww0123456',
        })

        # 4 注册电话号码已被使用
        ApiTester().api_fail('api-register', {
            'username': 'lng6',
            'nickname': '龙六',
            'gender': '0',
            'phone': '13214684993',
            'email': '1321468491@qq.com',
            'type': '1',
            'password': 'lng0123456',
            'repass': 'lng0123456',
        })

        # 5 注册电子邮箱已被使用
        ApiTester().api_fail('api-register', {
            'username': 'lng6',
            'nickname': '龙六',
            'gender': '0',
            'phone': '13214684999',
            'email': '1321468451@qq.com',
            'type': '1',
            'password': 'lng0123456',
            'repass': 'lng0123456',
        })

        # 6 注册用户名必须由英文字母、数字、符号组成
        ApiTester().api_fail('api-register', {
            'username': 'lng六',
            'nickname': '龙六',
            'gender': '0',
            'phone': '13214684999',
            'email': '1321468491@qq.com',
            'type': '1',
            'password': 'lng0123456',
            'repass': 'lng0123456',
        })

        # 7 用户名已存在
        ApiTester().api_fail('api-register', {
            'username': 'ww5',
            'nickname': '龙六',
            'gender': '0',
            'phone': '13214684999',
            'email': '1321468491@qq.com',
            'type': '1',
            'password': 'lng0123456',
            'repass': 'lng0123456',
        })

        # 18 密码必须由英文字母、数字、符号组成
        ApiTester().api_fail('api-register', {
            'username': 'lng6',
            'nickname': '龙六',
            'gender': '0',
            'phone': '13214684999',
            'email': '1321468491@qq.com',
            'type': '1',
            'password': '龙0123456',
            'repass': '龙0123456',
        })

        # 19 密码不能全是数字
        ApiTester().api_fail('api-register', {
            'username': 'lng6',
            'nickname': '龙六',
            'gender': '0',
            'phone': '13214684999',
            'email': '1321468491@qq.com',
            'type': '1',
            'password': '012345645',
            'repass': '012345645',
        })

        # 20 电子邮箱格式有误
        ApiTester().api_fail('api-register', {
            'username': 'lng6',
            'nickname': '龙六',
            'gender': '0',
            'phone': '13214684999',
            'email': '132146849',
            'type': '1',
            'password': 'lng0123456',
            'repass': 'lng0123456',
        })

        # 21 密码小于八位
        ApiTester().api_fail('api-register', {
            'username': 'lng6',
            'nickname': '龙六',
            'gender': '0',
            'phone': '13214684999',
            'email': '1321468491@qq.com',
            'type': '1',
            'password': '01234',
            'repass': '01234',
        })

        # 17 用户登录
        ApiTester().api_success('api-login', {
            'username': 'wb8',
            'password': 'wb123456'
        })

        # 8 战队创建
        ApiTester().auth_success('api-team-add', {
            'teamname': 'SKI',
            'desc': '欢迎加入SKI战队',
            'avatar': '',
        }, username='jl4', password='ls0123456')
        ApiTester().auth_success('api-team-add', {
            'teamname': 'CXK',
            'desc': '欢迎来到CXK战队。',
            'avatar': '',
        }, username='wb8', password='wb123456')

        # 9 战队名已被使用
        ApiTester().auth_fail('api-team-add', {
            'teamname': 'SKI',
            'desc': '欢迎加入KI战队大家庭',
            'avatar': '',
        }, username='jl4', password='ls0123456')

        # 16 只有经理能完成战队创建
        ApiTester().auth_fail('api-team-add', {
            'teamname': 'aik',
            'desc': '欢迎来到aik战队',
            'avatar': '',
        }, username='wf5', password='wf0123456')
        ApiTester().auth_fail('api-team-add', {
            'teamname': 'aik',
            'desc': '欢迎来到aik战队',
            'avatar': '',
        }, username='ww5', password='ww0123456')

        # 10 选手申请战队
        user_id = User.objects.get(username='zs3').id
        team_id = Team.objects.get(name='SKI').id
        ApiTester().auth_success('api-team-join', {
            'userId': user_id,
            'teamId': team_id,
            'desc': '仰慕已久，申请加入SKI战队！',
        }, username='zs3', password='zs0123456')

        # 11 申请战队不存在
        user_id = User.objects.get(username='wf5').id
        ApiTester().auth_fail('api-team-join', {
            'userId': user_id,
            'teamId': 6854515,
            'desc': '仰慕已久，申请加入SKI战队！',
        }, username='wf5', password='wf0123456')

        # 12 选手已有战队重复申请
        # 经理先同意申请
        ApiTester().auth_success('api-team-app', {
            'id': 1,
            'accept': 'true',
            'desc': '仰慕已久，申请加入SKI战队！',
        }, username='jl4', password='ls0123456')
        # 重复申请
        user_id = User.objects.get(username='zs3').id
        team_id = Team.objects.get(name='CXK').id
        ApiTester().auth_fail('api-team-join', {
            'userId': user_id,
            'teamId': team_id,
            'desc': '仰慕已久，申请加入SKI战队！',
        }, username='zs3', password='zs0123456')

        # 14 未加入战队重复申请
        user_id = User.objects.get(username='wf5').id
        team_id = Team.objects.get(name='SKI').id
        ApiTester().auth_success('api-team-join', {
            'userId': user_id,
            'teamId': team_id,
            'desc': '仰慕已久，申请加入SKI战队！',
        }, username='wf5', password='wf0123456')
        # 重复即失败
        ApiTester().auth_fail('api-team-join', {
            'userId': user_id,
            'teamId': team_id,
            'desc': '仰慕已久，申请加入SKI战队！',
        }, username='wf5', password='wf0123456')

        # 15 教练不存在
        team_id = Team.objects.get(name='SKI').id
        ApiTester().auth_fail('api-team-change', {
            'id': team_id,
            'name': 'SKI',
            'desc': '仰慕已久，申请加入SKI战队！',
            'avatar': '',
            'coach': '123',
        }, username='wf5', password='wf0123456')
