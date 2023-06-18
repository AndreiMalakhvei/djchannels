# chat/urls.py
from django.urls import path

from chat.views import RoomCreateView


urlpatterns = [
    path("createroom/", RoomCreateView.as_view(), name="roomcreate"),
    # path("<str:room_name>/", views.room, name="room"),
]