import datetime
from ulapd_api.extensions import db


class UserDetails(db.Model):
    __tablename__ = 'user_details'
    user_details_id = db.Column(db.Integer, primary_key=True)
    user_type_id = db.Column(db.Integer, nullable=False)
    ldap_id = db.Column(db.String, nullable=False)
    api_key = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=True)
    title = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    contactable = db.Column(db.Boolean, nullable=False)
    telephone_number = db.Column(db.String, nullable=False)
    address_line_1 = db.Column(db.String, nullable=False)
    address_line_2 = db.Column(db.String)
    city = db.Column(db.String, nullable=False)
    county = db.Column(db.String)
    postcode = db.Column(db.String, nullable=True)
    country = db.Column(db.String)
    country_of_incorporation = db.Column(db.String)
    organisation_name = db.Column(db.String)
    organisation_type = db.Column(db.String)
    registration_number = db.Column(db.String)
    date_added = db.Column(db.DateTime(timezone=False), default=datetime.datetime.now)

    def __init__(self, user_details):
        self.user_type_id = user_details['user_type_id']
        self.ldap_id = user_details['ldap_id']
        self.api_key = user_details['api_key']
        self.email = user_details['email']
        self.title = user_details['title']
        self.first_name = user_details['first_name']
        self.last_name = user_details['last_name']
        self.contactable = user_details['contactable']
        self.telephone_number = user_details['telephone_number']
        self.address_line_1 = user_details['address_line_1']
        self.address_line_2 = user_details['address_line_2']
        self.city = user_details['city']
        self.county = user_details.get('county', None)
        self.postcode = user_details['postcode']
        self.country = user_details.get('country', None)
        self.country_of_incorporation = user_details.get('country_of_incorporation', None)
        self.organisation_name = user_details.get('organisation_name', None)
        self.organisation_type = user_details.get('organisation_type', None)
        self.registration_number = user_details.get('registration_number', None)

    @staticmethod
    def get_user_details_all():
        return UserDetails.query.all()

    @staticmethod
    def get_user_details_by_id(user_details_id):
        return UserDetails.query.filter_by(user_details_id=user_details_id).first()

    @staticmethod
    def get_user_details_by_ldap_id(ldap_id):
        return UserDetails.query.filter_by(ldap_id=ldap_id).first()

    @staticmethod
    def get_user_details_by_api_key(api_key):
        return UserDetails.query.filter_by(api_key=api_key).first()

    @staticmethod
    def get_user_details_by_email(email):
        return UserDetails.query.filter_by(email=email).first()

    def as_dict(self):
        return {
            'user_details_id': self.user_details_id,
            'user_type_id': self.user_type_id,
            'ldap_id': self.ldap_id,
            'api_key': self.api_key,
            'email': self.email,
            'title': self.title,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'contactable': self.contactable,
            'telephone_number': self.telephone_number,
            'address_line_1': self.address_line_1,
            'address_line_2': self.address_line_2,
            'city': self.city,
            'county': self.county,
            'postcode': self.postcode,
            'country': self.country,
            'country_of_incorporation': self.country_of_incorporation,
            'organisation_name': self.organisation_name,
            'organisation_type': self.organisation_type,
            'registration_number': self.registration_number,
            'date_added': str(self.date_added)
        }
