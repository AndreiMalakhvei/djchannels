import json
from datetime import datetime
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache
from channels.generic.websocket import WebsocketConsumer
import hashlib
from chat.tasks import messages_to_db
from mysite.settings import BASE_DIR
from chat.models import User, Room, RoomMember
from django.db.models import Q
from chat.firebase.fire import FireBase

import pyrebase

firebase_db = FireBase()

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

        # send to front dict with number of unread messages for each room
        missed_messages = firebase_db.get_unread(self.fire_id)

        async_to_sync(self.channel_layer.send)(
            self.channel_name, {"type": "chat.missed",
                                "missed_messages": missed_messages}        )

        #  check if entered room and user (as room member) exist in RealTimeDB
        firebase_db.check_room_in_rtdb(self.room_name, self.fire_id)

        # Make DB record that the user is member of the room
        if not RoomMember.objects.filter(Q(member_id=self.userid) & Q(inroom_id__exact=self.room_name)).exists():
            new_rec = RoomMember(inroom_id=self.room_name,
                        member_id=self.userid)
            new_rec.save()

        # delete unread messages for the chat while entering the chat
        firebase_db.delete_unread_room_enter_leave(self.room_name, self.fire_id)

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

        # delete unread messages for the chat while leaving the chat
        firebase_db.delete_unread_room_enter_leave(self.room_name, self.fire_id)


    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        marked = text_data_json.get("mark", 0)
        if marked:
            if marked == "invite":
                invited_ids = [x["value"] for x in text_data_json["data"]]
                for x in invited_ids:

                    firebase_db.fire_db.child('main').child('invitations').child("user_%s" % x).update({self.room_name: self.fire_id})


                async_to_sync(self.channel_layer.group_send)(
                    self.service_group, {
                        "type": "chat.invite",
                        "ids": invited_ids,
                        "author": self.userid,
                        "chat": self.room_name
                    })
            elif marked == "invite_decline":
                firebase_db.delete_invitation(self.fire_id, text_data_json['data']['author'],
                                              text_data_json['data']['chat'])
            elif marked == "invite_accept":
                firebase_db.delete_invitation(self.fire_id, text_data_json['data']['author'],
                                              text_data_json['data']['chat'])
            elif marked == "leave_chat":
                RoomMember.objects.filter(Q(member_id=self.userid) & Q(inroom_id__exact=text_data_json['chat'])).delete()
                print()
                firebase_db.fire_db.child('main').child('unread').child(text_data_json['chat']).remove(self.fire_id)
                print()

        else:

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

            users_notify = firebase_db.fire_db.child('main').child('unread').child(self.room_name).get().val()
            if users_notify:
                for x in users_notify:
                    if x != self.fire_id:
                        if users_notify[x]:
                            users_notify[x].append(hash_store)
                        else:
                            users_notify[x] = [hash_store, ]
                firebase_db.fire_db.child('main').child('unread').child(self.room_name).set(users_notify)

            # Send message to room group
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, forward_to_front)

            # Send message to service group
            async_to_sync(self.channel_layer.group_send)(
                self.service_group, {
                    "type": "chat.service",
                    "notifications": users_notify,
                    "author": self.fire_id,
                    "chat": self.room_name
                })

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
                                                    "chat": event['chat'],
                                                    "quantity": quantity
                                                    }))
                    break

    def chat_missed(self, event):
        self.send(text_data=json.dumps({"mark": 'missed',
                                        "missed": event['missed_messages']}))

    def chat_invite(self, event):
        if event['author'] != self.userid:
            for x in event['ids']:
                if x == self.userid:
                    data = {"chat": event['chat'], "author": event['author']}
                    self.send(text_data=json.dumps({"mark": 'invite',
                                                    "data": data
                                                    }))
                    break
