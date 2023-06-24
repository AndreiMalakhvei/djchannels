from chat.firedb.credentials import FIRE_CONFIG
import pyrebase


class FireBase:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(FireBase, cls).__new__(cls)
            cls.instance.create_connection_to_db()
            cls.instance.name = "FireBase"
        return cls.instance

    def create_connection_to_db(self) -> None:
        self.cred = FIRE_CONFIG
        self.firebase = pyrebase.initialize_app(self.cred)
        self.fire_db = self.firebase.database()

    def get_unread(self, user: str):
        users_unread = {}
        all_records = self.fire_db.child('main').child('unread').get().val()
        if all_records:
            for room, record in all_records.items():
                if user in record.keys():
                    val = 0 if not record[user] else len(record[user])
                    users_unread.update({room: val})
        return users_unread

    def check_room_in_rtdb(self, room: str, user: str) -> None:
        room_exists = self.fire_db.child('main').child('unread').child(room).get().val()
        if not room_exists:
            self.fire_db.child('main').child('unread').update({room: None})
            self.fire_db.child('main').child('unread').child(room).update({user: 0})
        else:
            user_record = self.fire_db.child('main').child('unread').child(room).child(user).get().val()

            if not user_record:
                self.fire_db.child('main').child('unread').child(room).update({user: 0})

    def delete_unread_room_enter_leave(self, room: str, user: str) -> None:
        users_unread_messages = self.fire_db.child('main').child('unread').child(room).child(user).get().val()
        if users_unread_messages:
            self.fire_db.child('main').child('unread').child(room).child(user).set(0)

    def delete_invitation(self, invited: str, invitor: int, chat: str):
        self.fire_db.child('main').child('invitations').child(invited).child(chat).remove("user_%s" % invitor)
