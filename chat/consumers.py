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

    service_group = "service"

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name
        self.userid = int(self.scope['query_string'].decode('utf-8').lstrip("user="))

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        # join service group
        async_to_sync(self.channel_layer.group_add)(
            self.service_group, self.channel_name
        )

        cached_data = cache.get("act_%s" % self.room_name)
        if cached_data:
            cached_data.update({self.userid: False})
            cache.set("act_%s" % self.room_name,cached_data)
        else:
            cache.set("act_%s" % self.room_name, {self.userid: False})

        # print(f'changes in ACT_ROOM {self.room_name} : {cache.get("act_%s" % self.room_name)}')
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )


    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
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

        users_to_notify = cache.get("act_%s" % self.room_name)

        if users_to_notify:
            for x in users_to_notify:
                if x != self.userid:
                    users_to_notify[x] = True
                else:
                    users_to_notify[x] = False
            cache.set("act_%s" % self.room_name, users_to_notify)

        # print(f'changes in ACT_ROOM {self.room_name} : {cache.get("act_%s" % self.room_name)}')



        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, forward_to_front)

        # Send message to service group
        async_to_sync(self.channel_layer.group_send)(
            self.service_group, {
                "type": "chat.service",
                "message": "Notification from service group"
            })

        # async_to_sync(self.channel_layer.group_send)(
        #     self.room_group_name, {
        #     "type": "test.def",
        #     "message": "Hi!!!!",
        # })



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
                                        "userid": userid,
                                        "mark": "chat message"
                                        }))


    def chat_service(self, event):
        self.send(text_data=json.dumps({"message": event['message'],
                                        "mark": "service"}))
        print('I WAS REACHED!!!!!!!!!!!!!!!!!')

