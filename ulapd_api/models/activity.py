import datetime
from ulapd_api.extensions import db
from sqlalchemy import desc


class Activity(db.Model):
    __tablename__ = 'activity'
    activity_id = db.Column(db.Integer, primary_key=True)
    dataset_name = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.DateTime(timezone=False), default=datetime.datetime.utcnow)
    user_details_id = db.Column(db.Integer, nullable=False)
    activity_type = db.Column(db.String, nullable=False)
    ip_address = db.Column(db.String, nullable=False)
    api = db.Column(db.Boolean, nullable=False)
    file = db.Column(db.String, nullable=False)

    def __init__(self, activity_data):
        self.user_details_id = activity_data['user_details_id']
        self.dataset_name = activity_data['dataset_id']
        self.activity_type = activity_data['activity_type']
        self.ip_address = activity_data['ip_address']
        self.api = activity_data['api']
        self.file = activity_data['file']

    @staticmethod
    def get_all_activity():
        return Activity.query.all()

    @staticmethod
    def get_activity_by_id(activity_id):
        return Activity.query.filter_by(activity_id=activity_id).first()

    @staticmethod
    def get_activity_by_user_id(user_id):
        return Activity.query.filter_by(user_details_id=user_id).order_by(desc(Activity.timestamp)).all()

    @staticmethod
    def get_activity_by_type(activity_type):
        return Activity.query.filter_by(activity_type=activity_type).first()

    @staticmethod
    def delete_user_by_user_id(user_details_id):
        return Activity.query.filter_by(user_details_id=user_details_id).delete()

    @staticmethod
    def get_user_activity_by_dataset(user_details_id, dataset):
        return Activity.query.filter_by(user_details_id=user_details_id,
                                        dataset_name=dataset).order_by(desc(Activity.timestamp)).all()

    def as_dict(self):
        return {
            'activity_id': self.activity_id,
            'dataset_id': self.dataset_name,
            'timestamp': self.timestamp,
            'user_details_id': self.user_details_id,
            'activity_type': self.activity_type,
            'ip_address': self.ip_address,
            'api': self.api,
            'file': self.file
        }
