from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from datetime import datetime


class Room(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Message(models.Model):
    hash = models.CharField(max_length=32)
    text = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timest = models.IntegerField()
    created = models.DateTimeField
    inroom = models.ForeignKey(Room, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.author} : {self.text}'

    def save(self, *args, **kwargs):
        self.created = datetime.fromtimestamp(int(self.timest))
        super().save(*args, **kwargs)


class RoomMember(models.Model):
    inroom = models.ForeignKey(Room, on_delete=models.CASCADE)
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f' in Room {self.inroom} member: {self.member}'



