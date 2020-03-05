import json
import os
import uuid

from ulapd_api.main import app
from ulapd_api.models.user_details import UserDetails
from ulapd_api.models.user_terms_link import UserTermsLink
from ulapd_api.models.activity import Activity
from ulapd_api.models.dataset import Dataset
from ulapd_api.models.licence import Licence
from ulapd_api.extensions import db


def insert_user_row(user_data):
    with app.app_context():
        user = UserDetails(user_data)
        db.session.add(user)
        db.session.commit()
        user_details_id = user.user_details_id
        db.session.close()
    return user_details_id


def insert_licence_agreement(user_details_id):
    with app.app_context():
        terms_data = {
            'user_details_id': user_details_id,
            'licence_id': 'ccod'
        }
        user_terms = UserTermsLink(terms_data)
        db.session.add(user_terms)
        db.session.commit()
        agreement_id = user_terms.user_terms_link_id
        db.session.close()
    return agreement_id


def delete_user_agreement(user_details_id, lincence_id):
    with app.app_context():
        UserTermsLink.delete_user_licence_agreement(user_details_id, lincence_id)


def insert_user_activity(user_details_id, file, dataset_id):
    with app.app_context():
        activity_data = {
            'user_details_id': user_details_id,
            'activity_type': 'download',
            'ip_address': '172.10.0.10',
            'api': False,
            'file': file,
            'dataset_id': dataset_id
        }
        activity = Activity(activity_data)
        db.session.add(activity)
        db.session.commit()
        activity_id = activity.activity_id
        db.session.close()
    return activity_id


def delete_dataset(name):
    with app.app_context():
        dataset = Dataset.get_dataset_by_name(name)
        db.session.delete(dataset)
        db.session.commit()
        db.session.close()


def get_list_from_datasets(datasets):
    dataset_list = []
    public_resources = False
    resources = False
    for rows in datasets:
        dataset_list.append(rows['name'])
        public_resources = True if 'public_resources' in rows else False
        resources = True if 'resources' in rows else False

    return dataset_list, public_resources, resources


def delete_licence(licence_name):
    with app.app_context():
        licence = Licence.get_licence_by_licence_name(licence_name)
        db.session.delete(licence)
        db.session.commit()
        db.session.close()


def get_json_from_file(directory, file_path):
    full_path = os.path.join(directory, file_path)
    with open(full_path, 'r') as file:
        raw_data = file.read()

    return json.loads(raw_data)


def make_uuid():
    return uuid.uuid4()
