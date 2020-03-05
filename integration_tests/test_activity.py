import unittest
import json
import requests
import traceback
from os import path
from flask import current_app, g
from ulapd_api.main import app
from ulapd_api.services import user_service as service
from integration_tests.utilities import helpers


class TestActivity(unittest.TestCase):

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
            self.activity_id_1 = helpers.insert_user_activity(self.user_details_id, 'CCOD_COU_2019_09.zip', 'ccod')
            self.activity_id_2 = helpers.insert_user_activity(self.user_details_id, 'CCOD_COU_2019_10.zip', 'ccod')
            self.activity_id_list = [self.activity_id_1, self.activity_id_2]

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

    def test_get_activity(self):
        url = '{}/activities/{}'.format(self.URL_ULAPD_PREFIX, self.user_details_id)
        response = self.client.get(url, headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()

        for results in response_body:
            self.assertIn(results['activity_id'], self.activity_id_list)
            if results['activity_id'] == self.activity_id_1:
                self.assertEqual(results['file'], 'CCOD_COU_2019_09.zip')
            else:
                self.assertEqual(results['file'], 'CCOD_COU_2019_10.zip')

    def test_add_activity(self):
        activity_data = {
            'dataset_id': 'ccod',
            'user_details_id': self.user_details_id,
            'activity_type': 'download',
            'ip_address': 'some.ip.address',
            'api': False,
            'file': 'CCOD_COU_2019_09.zip'
        }
        url = '{}/activities'.format(self.URL_ULAPD_PREFIX)
        response = self.client.post(url, data=json.dumps(activity_data), headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()

        self.assertIn('activity_id', response_body)
