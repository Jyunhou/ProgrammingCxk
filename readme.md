# 编程两年半的电竞管理系统

## 部署

安装依赖包

```shell
pip install -r requirements.txt
```

初始化数据库（默认使用sqlite3，位于/db.sqlite3）

```shell
python manage.py migrate
```

运行

```shell
python manage.py runserver
```

访问[127.0.0.1:8000](http://127.0.0.1:8000/)
