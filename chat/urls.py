# chat/urls.py
from django.urls import path

from chat.views import RoomCreateView, RoomListView, ChatHistoryView, UserListView, GetUnread, GetInvitations


urlpatterns = [
    path("createroom/", RoomCreateView.as_view(), name="roomcreate"),
    path("roomslist/", RoomListView.as_view(), name="roomlist"),
    path("chathistory/", ChatHistoryView.as_view(), name="chathistory"),
    path("userslist/", UserListView.as_view(), name="userslist"),
    path("unread/", GetUnread.as_view(), name="uread"),
    path("getinvitations/", GetInvitations.as_view(), name="getinvitations"),

]
