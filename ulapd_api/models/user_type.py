import datetime
from ulapd_api.extensions import db


class UserType(db.Model):
    user_type_id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.String)
    date_added = db.Column(db.DateTime(timezone=False), default=datetime.datetime.now)

    def init(self, user_type):
        self.user_type = user_type['user_type']

    @staticmethod
    def get_user_type_by_id(user_type_id):
        return UserType.query.filter_by(user_type_id=user_type_id).first()

    @staticmethod
    def get_user_id_by_type(user_type):
        return UserType.query.filter_by(user_type=user_type).first()

    def as_dict(self):
        return {
            'user_type_id': self.user_type_id,
            'user_type': self.user_type,
            'date_added': self.date_added
        }
