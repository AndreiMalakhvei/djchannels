# chat/urls.py
from django.urls import path

from chat.views import RoomCreateView, RoomListView, ChatHistoryView


urlpatterns = [
    path("createroom/", RoomCreateView.as_view(), name="roomcreate"),
    path("roomslist/", RoomListView.as_view(), name="roomlist"),
    path("chathistory/", ChatHistoryView.as_view() ,name="chathistory")
    # path("<str:room_name>/", views.room, name="room"),
]
