import datetime
from ulapd_api.extensions import db
from sqlalchemy import desc


class UserTermsLink(db.Model):
    __tablename__ = 'user_terms_link'
    user_terms_link_id = db.Column(db.Integer, primary_key=True)
    user_details_id = db.Column(db.Integer, db.ForeignKey('user_details.user_details_id'), nullable=False)
    licence_name = db.Column(db.String, nullable=True)
    date_agreed = db.Column(db.DateTime(timezone=False), default=datetime.datetime.utcnow)

    def __init__(self, user_terms_data):
        self.user_details_id = user_terms_data['user_details_id']
        self.licence_name = user_terms_data['licence_id']

    @staticmethod
    def get_user_terms_by_user_id(user_details_id):
        return UserTermsLink.query.filter_by(user_details_id=user_details_id).all()

    @staticmethod
    def get_user_terms_by_licence_name(user_details_id, licence):
        return UserTermsLink.query.filter_by(user_details_id=user_details_id,
                                             licence_name=licence).order_by(desc(UserTermsLink.date_agreed)).first()

    @staticmethod
    def delete_user_by_user_id(user_details_id):
        return UserTermsLink.query.filter_by(user_details_id=user_details_id).delete()

    @staticmethod
    def delete_user_licence_agreement(user_details_id, licence):
        return UserTermsLink.query.filter_by(user_details_id=user_details_id,
                                             licence_name=licence).delete()

    def as_dict(self):
        return {
            'user_terms_link_id': self.user_terms_link_id,
            'user_details_id': self.user_details_id,
            'licence_id': self.licence_name,
            'date_agreed': self.date_agreed
        }
