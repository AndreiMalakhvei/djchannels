from rest_framework.response import Response
from rest_framework import generics
from chat.models import Room, Message, RoomMember
from chat.serializers import RoomSerializer, ChatHistorySerializer, UsersSerializer
from rest_framework.views import APIView
from rest_framework.exceptions import ParseError
from django.core.cache import cache
from django.contrib.auth.models import User
from chat.consumers import get_unread

# def index(request):
#     return render(request, "chat/index.html")
#
#
# def room(request, room_name):
#     return render(request, "chat/room.html", {"room_name": room_name})


class RoomCreateView(generics.CreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def perform_create(self, serializer):
        q = serializer.save()
        new_rec = RoomMember(inroom_id=q.name,
                             member_id=q.owner_id)
        new_rec.save()


class RoomListView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def get_queryset(self):
        if self.request.query_params:
            try:
                user = (self.request.query_params.get('user'))
            except (ValueError, TypeError):
                raise ParseError(detail="'user parameter is invalid")
            user_member_of = RoomMember.objects.filter(member_id=user).values('inroom_id')
            my_rooms = Room.objects.filter(name__in=user_member_of)

            return my_rooms
        return Room.objects.all()


class ChatHistoryView(APIView):
    def get(self, request):
        try:
            name = request.GET['name']
        except (KeyError, ValueError):
            raise ParseError(detail="'city' parameter is required")
        cached_messages = cache.get("chat_%s" % name)
        return Response(ChatHistorySerializer(cached_messages, many=True).data)


class UserListView(generics.ListAPIView):
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


class GetUnread(APIView):
    def get(self, request):
        try:
           user = request.GET['user']
        except (KeyError, ValueError):
            raise ParseError(detail="USER parameters is required")
        unread = get_unread("user_%s" % user)
        cnt_missed = sum(unread.values())
        return Response({'total_missed': cnt_missed})


import pyrebase

config = {
    'apiKey': "AIzaSyCd2wvYUpRGOmCxqBRa3YtdjAte62VA0-w",
    'authDomain': "chat-60128.firebaseapp.com",
    'projectId': "chat-60128",
    'storageBucket': "chat-60128.appspot.com",
    'messagingSenderId': "122065919374",
    'appId': "1:122065919374:web:424b17a1c85dd3243c18df",
    'measurementId': "G-4VHP970CEM",
    'databaseURL': "https://chat-60128-default-rtdb.europe-west1.firebasedatabase.app/",
    "serviceAccount": "chat-60128-firebase-adminsdk-mjhg2-c740633904.json"
}

firebase = pyrebase.initialize_app(config)
fire_db = firebase.database()


class GetInvitations(APIView):
    def get(self, request):
        try:
           user = request.GET['user']
        except (KeyError, ValueError):
            raise ParseError(detail="USER parameters is required")
        to_front = []
        invitations = fire_db.child('main').child('invitations').child("user_%s" % user).get().val()
        if invitations:
            for (author, chat) in invitations.items():
                to_front.append({'chat': chat, "author": author})
        return Response(to_front)