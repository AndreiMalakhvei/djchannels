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

    def get_queryset(self):
        if self.request.query_params:
            try:

                room = (self.request.query_params.get('room'))
            except (ValueError, TypeError):
                raise ParseError(detail="'user or room parameter is invalid")
            member_of_room = RoomMember.objects.filter(inroom_id__exact=room).values('member_id')
            other_users = User.objects.exclude(id__in=member_of_room).filter(is_superuser=False)

            return other_users
        return User.objects.all().filter(is_superuser=False)

