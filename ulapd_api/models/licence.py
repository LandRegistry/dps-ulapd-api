from ulapd_api.extensions import db


class Licence(db.Model):
    __tablename__ = 'licence'
    licence_id = db.Column(db.Integer, primary_key=True)
    licence_name = db.Column(db.String, unique=True, nullable=False)
    status = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    last_updated = db.Column(db.Date, nullable=False)
    created = db.Column(db.Date, nullable=False)
    dataset_name = db.Column(db.String, nullable=True)

    def __init__(self, licence_data):
        self.licence_name = licence_data['licence_id']
        self.status = licence_data['status']
        self.title = licence_data['title']
        self.url = licence_data['url']
        self.last_updated = licence_data['last_updated']
        self.created = licence_data['created']
        self.dataset_name = licence_data['dataset_name']

    @staticmethod
    def get_licence_by_licence_name(licence_name):
        return Licence.query.filter_by(licence_name=licence_name).first()

    @staticmethod
    def get_licences_by_dataset_name(dataset_name):
        return Licence.query.filter_by(dataset_name=dataset_name).all()

    @staticmethod
    def get_all_licences():
        return Licence.query.all()

    def as_dict(self):
        return {
            'id': self.licence_id,
            'licence_id': self.licence_name,
            'status': self.status,
            'title': self.title,
            'url': self.url,
            'last_updated': self.last_updated,
            'created': self.created,
            'dataset_name': self.dataset_name
        }
