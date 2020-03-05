import unittest
import json
import requests
import traceback
from os import path
from flask import current_app, g
from ulapd_api.main import app
from ulapd_api.services import user_service as service
from integration_tests.utilities import helpers


class TestUsers(unittest.TestCase):

    URL_ULAPD_PREFIX = '/v1'
    directory = path.dirname(__file__)
    user_data = helpers.get_json_from_file(directory, 'data/user_data.json')

    with app.app_context():
        account_url = '{}/{}'.format(current_app.config['ACCOUNT_API_URL'], current_app.config['ACCOUNT_API_VERSION'])

    def setUp(self):
        self.client = app.test_client()

        with app.app_context():
            self.headers = {'Accept': 'application/json',
                            'Content-Type': 'application/json'}

        try:
            app.logger.info('Setting up user...')
            with app.app_context() as ac:
                ac.g.trace_id = None
                ac.g.requests = requests.Session()
                self.user_details = service.create_new_user(self.user_data)
            self.user_details_id = self.user_data['user_details_id']
            self.ldap_id = self.user_data['ldap_id']
            self.api_key = self.user_data['api_key']

            self.agreement_id = helpers.insert_licence_agreement(self.user_details_id)

            app.logger.info('Done, id: {}'.format(self.user_details_id))
        except Exception:
            app.logger.error('Setup failed')
            traceback.print_exc()
            self.tearDown()

    def tearDown(self):
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()

            if self.ldap_id is None:
                app.logger.info('No ldap to teardown...')
            else:
                app.logger.info('Removing user from ldap...')
                url = '{}/users/{}'.format(self.account_url, self.ldap_id)
                g.requests.delete(url, headers=self.headers)

            if self.user_details_id is None:
                app.logger.info('No ulapd to teardown...')
            else:
                app.logger.info('Removing user from ulapd...')
                service.delete_user(self.user_details_id)

    def test_get_user(self):
        url = '{}/users/user_details_id/{}'.format(self.URL_ULAPD_PREFIX, self.user_details_id)
        response = self.client.get(url, headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()

        self.assertEqual(response_body['user_details']['user_details_id'], self.user_details_id)
        self.assertIn('user_details', response_body)
        self.assertIn('datasets', response_body)

    def test_get_user_licences(self):
        url = '{}/users/licence/{}'.format(self.URL_ULAPD_PREFIX, self.user_details_id)
        response = self.client.get(url, headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()

        self.assertEqual(response_body[0]['user_terms_link_id'], self.agreement_id)
        self.assertEqual(response_body[0]['user_details_id'], self.user_details_id)

    def test_get_user_licence(self):
        url = '{}/users/licence/{}/ccod'.format(self.URL_ULAPD_PREFIX, self.user_details_id)
        response = self.client.get(url, headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()

        self.assertEqual(response_body['valid_licence'], True)

    def test_add_user_licence(self):
        licence_data = {'user_details_id': self.user_details_id, 'licence_id': 'ocod'}
        url = '{}/users/licence'.format(self.URL_ULAPD_PREFIX)
        response = self.client.post(url, data=json.dumps(licence_data), headers=self.headers)

        self.assertEqual(201, response.status_code)
        response_body = response.get_json()

        self.assertEqual(response_body['user_details_id'], self.user_details_id)
        self.assertEqual(response_body['licence_id'], 'ocod')

        helpers.delete_user_agreement(self.user_details_id, 'ocod')

    def test_get_user_dataset_activity(self):
        helpers.insert_user_activity(self.user_details_id, 'CCOD_COU_2019_09.zip', 'ccod')
        helpers.insert_user_activity(self.user_details_id, 'CCOD_COU_2019_10.zip', 'ccod')
        url = '{}/users/dataset-activity/{}'.format(self.URL_ULAPD_PREFIX, self.user_details_id)
        response = self.client.get(url, headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()
        result = list(filter(lambda dataset: dataset['name'] == 'ccod', response_body))

        self.assertEqual(result[0]['download_history'][0]['file'], 'CCOD_COU_2019_10.zip')
        self.assertEqual(result[0]['download_history'][1]['file'], 'CCOD_COU_2019_09.zip')
        self.assertEqual(result[0]['licence_agreed'], True)

    def test_create_user(self):
        self.tearDown()
        url = '{}/users'.format(self.URL_ULAPD_PREFIX)
        response = self.client.post(url, data=json.dumps(self.user_data), headers=self.headers)

        self.assertEqual(201, response.status_code)
        response_body = response.get_json()
        self.user_details_id = response_body['user_details_id']
        self.ldap_id = response_body['ldap_id']

        self.assertEqual(response_body['user_details_id'], self.user_details_id)

    def test_update_user_contact_preference(self):
        contact_data = {'user_id': self.user_details_id, 'contactable': True, 'contact_preferences': ['email', 'text']}
        url = '{}/users/contact_preference'.format(self.URL_ULAPD_PREFIX)
        response = self.client.patch(url, data=json.dumps(contact_data), headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()

        self.assertEqual(response_body['contactable'], True)
        self.assertEqual(response_body['contact_preferences'], ['email', 'text'])

    def test_delete_user(self):
        url = '{}/users/{}'.format(self.URL_ULAPD_PREFIX, self.user_details_id)
        response = self.client.delete(url, headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()

        self.assertEqual(response_body['user_id'], str(self.user_details_id))
        self.assertEqual(response_body['message'], 'user deleted')
        self.user_details_id = None

    def test_update_api_key(self):
        url = '{}/users/{}/update_api_key'.format(self.URL_ULAPD_PREFIX, self.user_details_id)
        response = self.client.post(url, headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()

        self.assertNotEqual(response_body['api_key'], self.api_key)
