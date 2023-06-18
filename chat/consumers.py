import json
from datetime import datetime
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache
from channels.generic.websocket import WebsocketConsumer
import hashlib
from chat.tasks import messages_to_db



TIMEOUT_FOR_CACHING_MESSAGES = 60 * 60

class ChatConsumer(WebsocketConsumer):
    connections_set = set()

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name
        self.userid = int(self.scope['query_string'].decode('utf-8').lstrip("user="))

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.connections_set.add(self.userid)
        print(f'FOR ROOM {self.room_group_name} the following users are loggedin: {self.connections_set}')

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )
        self.connections_set.discard(self.userid)
        print(f'FOR ROOM {self.room_group_name} the following users are loggedin: {self.connections_set}')
        # messages_to_db()

    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):

        channel_layer = get_channel_layer()



        text_data_json = json.loads(text_data)
        jetzt = datetime.fromtimestamp(text_data_json["jetzt"]/1000)
        py_timestamp = datetime.timestamp(jetzt)
        jetzt_to_forward = text_data_json["jetzt"]
        hashed_value = str(py_timestamp) + str(self.userid)
        message_hash = hashlib.md5(bytearray(hashed_value, 'utf-8'))
        hash_store = message_hash.hexdigest()

        message_to_cache = {
            "item_hash": hash_store,
            "message": text_data_json["message"],
            "userid": self.userid,
            "py_timestamp": py_timestamp,
            "username": text_data_json["username"],
            "nowdate": jetzt.strftime("%m/%d/%Y"),
            "nowtime": jetzt.strftime("%H:%M:%S")
        }

        if cache.get(self.room_group_name):
            existing_value = cache.get(self.room_group_name)
            existing_value.append(message_to_cache)
            cache.set(self.room_group_name, existing_value, timeout=TIMEOUT_FOR_CACHING_MESSAGES)
        else:
            cache.set(self.room_group_name, [message_to_cache, ], timeout=TIMEOUT_FOR_CACHING_MESSAGES)


        message_extra_data = {
            "type": "chat_message",
            "jetzt": jetzt_to_forward,
        }

        forward_to_front = message_to_cache | message_extra_data


        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, forward_to_front)



    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]
        username = event['username']
        nowdate = event['nowdate']
        nowtime = event['nowtime']
        jetzt = event["jetzt"]
        userid = event["userid"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message,
                                        "username": username,
                                        "nowdate": nowdate,
                                        "nowtime": nowtime,
                                        "jetzt": jetzt,
                                        "userid": userid
                                        }))
