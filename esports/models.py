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
    data = models.TextField()
    team = models.ForeignKey(Team, models.SET_NULL, null=True)


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
    person = models.ForeignKey(Person, models.SET_NULL, null=True)
    datetime = models.DateTimeField(auto_now_add=True)
    status = models.SmallIntegerField(choices=Message.STATUS_CHOICES, default=1)


class ReceiveMessage(models.Model):
    person = models.ForeignKey(Person, models.CASCADE)
    send_message = models.ForeignKey(SendMessage, models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField()
    status = models.SmallIntegerField(choices=Message.STATUS_CHOICES, default=1)
