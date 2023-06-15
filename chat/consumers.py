import json
from datetime import datetime
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json["username"]
        jetzt = datetime.fromtimestamp(text_data_json["jetzt"]/1000)
        jetzt_to_forward = text_data_json["jetzt"]
        userid = text_data_json["userid"]

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_message",
                                   "message": message,
                                   "username": username,
                                   "nowdate": jetzt.strftime("%m/%d/%Y"),
                                   "nowtime": jetzt.strftime("%H:%M:%S"),
                                   "jetzt": jetzt_to_forward,
                                   "userid": userid
                                   }
        )

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
