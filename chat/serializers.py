from chat.models import Room, Message, RoomMember
from rest_framework import serializers


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
