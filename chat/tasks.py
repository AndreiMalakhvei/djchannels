from mysite.celery import app
from django.core.cache import cache
from chat.models import Message, Room
from django.contrib.auth.models import User


@app.task
def messages_to_db():
    rooms = Room.objects.select_related()
    for room in rooms:
        cached_messages_to_save = cache.get("chat_%s" % room.name)
        if cached_messages_to_save:
            data_to_add = []
            for message in cached_messages_to_save:
                new_item = Message(
                hash=message["item_hash"],
                text= message["message"],
                author=User.objects.get(id=message["userid"]),
                timest=message["py_timestamp"],
                inroom=room,
                )
                data_to_add.append(new_item)
            Message.objects.bulk_create(data_to_add)

