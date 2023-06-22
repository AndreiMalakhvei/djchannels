from rest_framework.response import Response
from rest_framework import generics
from chat.models import Room, Message, RoomMember
from chat.serializers import RoomSerializer, ChatHistorySerializer, UsersSerializer
from rest_framework.views import APIView
from rest_framework.exceptions import ParseError
from django.core.cache import cache
from django.contrib.auth.models import User

# def index(request):
#     return render(request, "chat/index.html")
#
#
# def room(request, room_name):
#     return render(request, "chat/room.html", {"room_name": room_name})


class RoomCreateView(generics.CreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class RoomListView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class ChatHistoryView(APIView):
    def get(self, request):
        try:
            name = request.GET['name']
        except (KeyError, ValueError):
            raise ParseError(detail="'city' parameter is required")
        cached_messages = cache.get("chat_%s" % name)
        return Response(ChatHistorySerializer(cached_messages, many=True).data)

class UserListView(generics.ListAPIView):
    queryset = User.objects.all().filter(is_superuser=False)
    serializer_class = UsersSerializer





