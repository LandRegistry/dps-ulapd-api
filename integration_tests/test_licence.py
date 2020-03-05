import unittest
import json
from ulapd_api.main import app
from integration_tests.utilities import helpers


class TestLicence(unittest.TestCase):

    URL_ULAPD_PREFIX = '/v1'

    def setUp(self):
        self.client = app.test_client()

        with app.app_context():
            self.headers = {'Accept': 'application/json',
                            'Content-Type': 'application/json'}

    def test_create_licence(self):
        licence = {
            'licence_id': 'integration_test',
            'status': 'active',
            'title': 'Licence for integration tests',
            'url': 'some-url',
            'last_updated': '2019-11-26',
            'created': '2019-11-26',
            'dataset_name': 'integration-test'
        }
        url = '{}/licence'.format(self.URL_ULAPD_PREFIX)
        response = self.client.post(url, data=json.dumps(licence), headers=self.headers)

        self.assertEqual(201, response.status_code)
        response_body = response.get_json()

        self.assertEqual(response_body['licence_id'], licence['licence_id'])
        helpers.delete_licence(licence['licence_id'])
