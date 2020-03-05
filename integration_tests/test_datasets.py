import unittest
import json
import requests
import traceback
from os import path
from ulapd_api.main import app
from ulapd_api.services import dataset_service as service
from integration_tests.utilities import helpers


class TestDatasets(unittest.TestCase):

    URL_ULAPD_PREFIX = '/v1'
    directory = path.dirname(__file__)
    dataset_data = helpers.get_json_from_file(directory, 'data/dataset_data.json')

    def setUp(self):
        self.client = app.test_client()

        with app.app_context():
            self.headers = {'Accept': 'application/json',
                            'Content-Type': 'application/json'}

        self.dataset_name = None
        self.dataset_list = []
        self.public_resources, self.resources = (False,) * 2

        try:
            app.logger.info('Getting dataset info...')
            with app.app_context() as ac:
                ac.g.trace_id = None
                ac.g.requests = requests.Session()
                self.dataset = service.get_dataset_by_name('ccod')
            self.file_name = self.dataset['resources'][0]['file_name']
            app.logger.info('Done...')
        except Exception:
            app.logger.error('Setup failed')
            traceback.print_exc()
            self.tearDown()

    def tearDown(self):
        if self.dataset_name:
            helpers.delete_dataset(self.dataset_name)

    def test_get_datasets(self):
        url = '{}/datasets'.format(self.URL_ULAPD_PREFIX)
        response = self.client.get(url, headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()

        self.dataset_list, self.public_resources, self.resources = helpers.get_list_from_datasets(response_body)
        self.assertIn('ccod', self.dataset_list)
        self.assertEqual(self.public_resources, True)
        self.assertEqual(self.resources, True)

    def test_get_datasets_external(self):
        url = '{}/datasets?external=True'.format(self.URL_ULAPD_PREFIX)
        response = self.client.get(url, headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()

        self.dataset_list, self.public_resources, self.resources = helpers.get_list_from_datasets(response_body)
        self.assertNotIn('ccod', self.dataset_list)
        self.assertEqual(self.public_resources, False)
        self.assertEqual(self.resources, False)

    def test_get_datasets_simple(self):
        url = '{}/datasets?simple=True'.format(self.URL_ULAPD_PREFIX)
        response = self.client.get(url, headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()

        self.dataset_list, self.public_resources, self.resources = helpers.get_list_from_datasets(response_body)
        self.assertIn('ccod', self.dataset_list)
        self.assertEqual(self.public_resources, False)
        self.assertEqual(self.resources, False)

    def test_create_dataset(self):
        url = '{}/datasets'.format(self.URL_ULAPD_PREFIX)
        response = self.client.post(url, data=json.dumps(self.dataset_data), headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()
        self.dataset_name = response_body['name']

        self.assertEqual(response_body['title'], self.dataset_data['title'])

    def test_get_dataset_by_name(self):
        url = '{}/datasets/{}'.format(self.URL_ULAPD_PREFIX, 'ccod')
        response = self.client.get(url, headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()

        self.assertEqual(response_body['name'], 'ccod')
        self.assertIn('public_resources', response_body)
        self.assertIn('file_size', response_body)

    def test_get_dataset_history(self):
        url = '{}/datasets/{}/history'.format(self.URL_ULAPD_PREFIX, 'ccod')
        response = self.client.get(url, headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()

        self.assertEqual(response_body['name'], 'ccod')
        self.assertIn('dataset_history', response_body)
        self.assertIn('resource_list', response_body['dataset_history'][0])

    def test_get_download_link(self):
        url = '{}/datasets/download/{}/{}'.format(self.URL_ULAPD_PREFIX, 'ccod', self.file_name)
        response = self.client.get(url, headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()

        self.assertIn('link', response_body)

    def test_historical_cache(self):
        url = '{}/datasets/historical_cache'.format(self.URL_ULAPD_PREFIX)
        response = self.client.put(url, headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()

        self.assertEqual(response_body['result'], 'ok')
