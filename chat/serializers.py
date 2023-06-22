from chat.models import Room, Message, RoomMember
from rest_framework import serializers
from django.contrib.auth.models import User

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class ChatHistorySerializer(serializers.Serializer):
    item_hash = serializers.CharField()
    message = serializers.CharField()
    userid = serializers.IntegerField()
    py_timestamp = serializers.IntegerField()
    username = serializers.CharField()
    nowdate = serializers.CharField()
    nowtime = serializers.CharField()


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

