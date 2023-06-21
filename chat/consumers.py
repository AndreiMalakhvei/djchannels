import json
from datetime import datetime
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache
from channels.generic.websocket import WebsocketConsumer
import hashlib
from chat.tasks import messages_to_db
from mysite.settings import BASE_DIR

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

TIMEOUT_FOR_CACHING_MESSAGES = 60 * 60

class ChatConsumer(WebsocketConsumer):

    service_group = "service"

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name
        self.userid = int(self.scope['query_string'].decode('utf-8').lstrip("user="))
        self.fire_id = "user_%s" % self.userid

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        # join service group
        async_to_sync(self.channel_layer.group_add)(
            self.service_group, self.channel_name
        )

        room_exists = fire_db.child('main').child('unread').child(self.room_name).get().val()
        if not room_exists:
            fire_db.child('main').child('unread').update({self.room_name: None})
            fire_db.child('main').child('unread').child(self.room_name).update({self.fire_id: 0})
        else:
            user_record = fire_db.child('main').child('unread').child(self.room_name).child(self.fire_id).get().val()
            if not user_record:
                fire_db.child('main').child('unread').child(self.room_name).update({self.fire_id: 0})

        # Заменить на Firebase
        # cached_data = cache.get("act_%s" % self.room_name)
        # if cached_data:
        #     cached_data.update({self.channel_name: []})
        #     cache.set("act_%s" % self.room_name, cached_data)
        # else:
        #     cache.set("act_%s" % self.room_name, {self.channel_name: []})
        #
        # print(f'changes in ACT_ROOM {self.room_name} : {cache.get("act_%s" % self.room_name)}'

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

        users_notify = fire_db.child('main').child('unread').child(self.room_name).get().val()
        if users_notify:
            for x in users_notify:
                if x != self.fire_id:
                    if users_notify[x]:
                        users_notify[x].append(hash_store)
                    else:
                        users_notify[x] = [hash_store, ]
            fire_db.child('main').child('unread').child(self.room_name).set(users_notify)


        # Заменить на Firebase
        # users_to_notify = cache.get("act_%s" % self.room_name)
        # if users_to_notify:
        #     for x in users_to_notify:
        #         if x != self.userid:
        #             users_to_notify[x].append(hash_store)
        #     cache.set("act_%s" % self.room_name, users_to_notify)
        #
        # print(f'changes in ACT_ROOM {self.room_name} : {cache.get("act_%s" % self.room_name)}'



        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, forward_to_front)

        # Send message to service group
        async_to_sync(self.channel_layer.group_send)(
            self.service_group, {
                "type": "chat.service",
                "notifications": users_notify,
                "author": self.fire_id
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
        if event['author'] != self.fire_id:
            for x in event['notifications']:
                if x == self.fire_id and event['notifications'][x]:
                    quantity = len(event['notifications'][x])
                    self.send(text_data=json.dumps({"mark": 'service',
                                                    "chat": self.room_name,
                                                    "quantity": quantity
                                                    }))
                    break


