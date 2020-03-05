import unittest
from ulapd_api.main import app
from ulapd_api.exceptions import ApplicationError
from unittest.mock import patch


@patch('ulapd_api.views.v1.datasets.dataset_service')
class TestDatasets(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.headers = {'Accept': 'application/json',
                        'Content-Type': 'application/json'}

    def test_get_datasets(self, mock_service):
        mock_service.get_datasets.return_value = [{'foo': 'bar'}]

        response = self.app.get('/v1/datasets', headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, [{'foo': 'bar'}])

    def test_get_datasets_error(self, mock_service):
        mock_service.get_datasets.side_effect = ApplicationError('some error', 500)

        response = self.app.get('/v1/datasets', headers=self.headers)

        self.assertEqual(500, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'error': 'Failed to get datasets - error: some error'})

    def test_create_dataset(self, mock_service):
        mock_service.create_dataset.return_value = [{'foo': 'bar'}]

        response = self.app.post('/v1/datasets', json={"name": "aaaa"}, headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, [{'foo': 'bar'}])

    def test_create_dataset_error(self, mock_service):
        mock_service.create_dataset.side_effect = ApplicationError('some error', 500)

        response = self.app.post('/v1/datasets', json={"name": "aaaa"}, headers=self.headers)

        self.assertEqual(500, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'error': 'Failed to create dataset: aaaa - error: some error'})

    def test_get_dataset_by_name(self, mock_service):
        mock_service.get_dataset_by_name.return_value = [{'foo': 'bar'}]

        response = self.app.get('/v1/datasets/test', headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, [{'foo': 'bar'}])

    def test_get_dataset_by_name_error(self, mock_service):
        mock_service.get_dataset_by_name.side_effect = ApplicationError('some error', 500)

        response = self.app.get('/v1/datasets/test', headers=self.headers)

        self.assertEqual(500, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'error': 'Failed to get dataset: test - error: some error'})

    def test_get_dataset_history(self, mock_service):
        mock_service.get_dataset_history.return_value = [{'foo': 'bar'}]

        response = self.app.get('/v1/datasets/test/history', headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, [{'foo': 'bar'}])

    def test_get_dataset_history_error(self, mock_service):
        mock_service.get_dataset_history.side_effect = ApplicationError('some error', 500)

        response = self.app.get('/v1/datasets/test/history', headers=self.headers)

        self.assertEqual(500, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'error': 'Failed to get dataset: test history - error: some error'})

    def test_get_download_link(self, mock_service):
        mock_service.get_download_link.return_value = 'a_link'

        response = self.app.get('/v1/datasets/download/test/file_name.zip', headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'link': 'a_link'})

    def test_get_download_link_with_date(self, mock_service):
        mock_service.get_download_link.return_value = 'a_link'

        response = self.app.get('/v1/datasets/download/history/test/file_name.zip/2019-09', headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'link': 'a_link'})

    def test_get_download_link_error(self, mock_service):
        mock_service.get_download_link.side_effect = ApplicationError('some error', 500)

        response = self.app.get('/v1/datasets/download/test/file_name.zip', headers=self.headers)

        self.assertEqual(500, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'error': 'Failed to get download link for dataset: test - error: some error'})

    def test_historical_cache(self, mock_service):
        mock_service.update_historical_cache.return_value = 'ok'

        response = self.app.put('/v1/datasets/historical_cache', headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, 'ok')

    def test_historical_cache_error(self, mock_service):
        mock_service.update_historical_cache.side_effect = ApplicationError('some error', 500)

        response = self.app.put('/v1/datasets/historical_cache', headers=self.headers)

        self.assertEqual(500, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'error': 'Failed to update historical cache:  some error '})
