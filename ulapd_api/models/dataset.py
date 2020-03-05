import datetime
from ulapd_api.extensions import db


class Dataset(db.Model):
    __tablename__ = 'dataset'
    dataset_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    title = db.Column(db.String, nullable=False)
    version = db.Column(db.String)
    url = db.Column(db.String)
    description = db.Column(db.String)
    licence_name = db.Column(db.String)
    state = db.Column(db.String, default='active')
    type = db.Column(db.String, default='dataset')
    private = db.Column(db.Boolean, default=False)
    external = db.Column(db.Boolean, default=False)
    metadata_created = db.Column(db.DateTime(timezone=False), default=datetime.datetime.utcnow)

    def __init__(self, dataset_data):
        self.name = dataset_data['name']
        self.title = dataset_data['title']
        self.version = dataset_data['version']
        self.url = dataset_data['url']
        self.description = dataset_data['description']
        self.licence_name = dataset_data['licence_id']
        self.state = dataset_data['state']
        self.type = dataset_data['type']
        self.private = dataset_data['private']
        self.external = dataset_data['external']

    @staticmethod
    def get_all(external=False):
        return Dataset.query.filter_by(external=external).all()

    @staticmethod
    def get_dataset_by_id(dataset_id):
        return Dataset.query.filter_by(dataset_id=dataset_id).first()

    @staticmethod
    def get_dataset_by_name(name):
        return Dataset.query.filter_by(name=name).first()

    @staticmethod
    def get_dataset_by_licence_name(licence_name):
        return Dataset.query.filter_by(licence_name=licence_name).first()

    def as_dict(self):
        return {
            'dataset_id': self.dataset_id,
            'name': self.name,
            'title': self.title,
            'version': self.version,
            'url': self.url,
            'description': self.description,
            'licence_id': self.licence_name,
            'state': self.state,
            'type': self.type,
            'private': self.private,
            'metadata_created': self.metadata_created,
            'external': self.external
        }
