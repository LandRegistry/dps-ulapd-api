import datetime
from ulapd_api.extensions import db


class Contact(db.Model):
    __tablename__ = 'contact'
    contact_id = db.Column(db.Integer, primary_key=True)
    user_details_id = db.Column(db.Integer, db.ForeignKey('user_details.user_details_id'), nullable=False)
    contact_type = db.Column(db.String, nullable=False)
    date_added = db.Column(db.DateTime(timezone=False), default=datetime.datetime.now)

    def __init__(self, contact):
        self.user_details_id = contact['user_details_id']
        self.contact_type = contact['contact_type']

    @staticmethod
    def get_contact_preference_by_id(contact_id):
        return Contact.query.filter_by(contact_id=contact_id).first()

    @staticmethod
    def get_contact_preferences_for_user(user_details_id):
        return Contact.query.filter_by(user_details_id=user_details_id).all()

    @staticmethod
    def delete_contact_preferences_for_user(user_details_id):
        return Contact.query.filter_by(user_details_id=user_details_id).delete()

    @staticmethod
    def delete_contact_preferences_by_id(contact_id):
        return Contact.query.filter_by(contact_id=contact_id).delete()

    def as_dict(self):
        return {
            'contact_id': self.contact_id,
            'user_details_id': self.user_details_id,
            'contact_type': self.contact_type,
            'date_added': self.date_added
        }
