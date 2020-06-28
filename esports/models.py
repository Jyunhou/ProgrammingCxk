from django.contrib.auth.models import User
from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=63)
    desc = models.TextField(default='')
    avatar = models.URLField(max_length=255, default='/static/images/default-team-avatar.png')
    manager = models.ForeignKey(User, models.CASCADE, related_name='manage_team_set')
    coach = models.ForeignKey(User, models.SET_NULL, related_name='teach_team_set', null=True)
    data = models.TextField()


class Person(models.Model):
    PERSON_TYPE_PLAYER = 1
    PERSON_TYPE_COACH = 2
    PERSON_TYPE_MANAGER = 3
    PERSON_TYPE_CHOICES = (
        (PERSON_TYPE_PLAYER, '选手'),
        (PERSON_TYPE_COACH, '教练'),
        (PERSON_TYPE_MANAGER, '经理'),
    )

    user = models.OneToOneField(User, models.CASCADE)
    name = models.CharField(max_length=63)
    gender = models.BooleanField()
    phone = models.IntegerField(unique=True)
    email = models.EmailField(unique=True)
    type = models.SmallIntegerField(choices=PERSON_TYPE_CHOICES)
    avatar = models.URLField(max_length=255, default='/static/images/default-person-avatar.png')
    team = models.ForeignKey(Team, models.SET_NULL, null=True)


class PersonData(models.Model):
    person = models.OneToOneField(Person, models.CASCADE, primary_key=True)
    win = models.IntegerField(default=0)
    win_rate = models.IntegerField(default=0)
    kill = models.IntegerField(default=0)
    assist = models.IntegerField(default=0)
    death = models.IntegerField(default=0)
    reinforce = models.IntegerField(default=0)
    money = models.IntegerField(default=0)
    tower = models.IntegerField(default=0)


class PersonDataRecord(models.Model):
    TYPE_QUALIFYING = 1
    TYPE_MATCH = 2
    TYPE_BIG_FIGHT = 3
    TYPE_CHOICES = (
        (TYPE_QUALIFYING, '排位赛'),
        (TYPE_MATCH, '匹配赛'),
        (TYPE_BIG_FIGHT, '大乱斗'),
    )
    data = models.ForeignKey(PersonData, models.CASCADE)
    win = models.BooleanField()
    kill = models.IntegerField()
    assist = models.IntegerField()
    death = models.IntegerField()
    reinforce = models.IntegerField()
    money = models.IntegerField()
    tower = models.IntegerField()
    type = models.IntegerField(choices=TYPE_CHOICES)
    date = models.DateField()

    class Meta:
        ordering = ['-date']


class Message:
    STATUS_NORMAL = 1
    STATUS_RETRACT = 2
    STATUS_CHOICES = (
        (STATUS_NORMAL, '正常'),
        (STATUS_RETRACT, '撤回'),
    )


class SendMessage(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    user = models.ForeignKey(User, models.SET_NULL, null=True)
    datetime = models.DateTimeField(auto_now_add=True)
    status = models.SmallIntegerField(choices=Message.STATUS_CHOICES, default=Message.STATUS_NORMAL)


class ReceiveMessage(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    send_message = models.ForeignKey(SendMessage, models.CASCADE, null=True)
    datetime = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    status = models.SmallIntegerField(choices=Message.STATUS_CHOICES, default=Message.STATUS_NORMAL)


class TeamApplication(models.Model):
    STATUS_PENDING = 0
    STATUS_REFUSE = 2
    STATUS_ACCEPT = 1
    STATUS_CHOICES = (
        (STATUS_PENDING, '待批准'),
        (STATUS_ACCEPT, '已通过'),
        (STATUS_REFUSE, '已拒绝'),
    )
    time = models.DateTimeField(auto_now_add=True)
    team = models.ForeignKey(Team, models.CASCADE)
    user = models.ForeignKey(User, models.CASCADE)
    desc = models.CharField(max_length=255)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS_PENDING)
