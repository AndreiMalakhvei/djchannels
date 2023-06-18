from django.shortcuts import render
from rest_framework import generics
from chat.models import Room, Message, RoomMember
from chat.serializers import RoomSerializer

# def index(request):
#     return render(request, "chat/index.html")
#
#
# def room(request, room_name):
#     return render(request, "chat/room.html", {"room_name": room_name})


class RoomCreateView(generics.CreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer




