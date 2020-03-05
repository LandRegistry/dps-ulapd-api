import unittest
from ulapd_api.main import app
from ulapd_api.exceptions import ApplicationError
from unittest.mock import patch


@patch('ulapd_api.views.v1.licence.service')
class TestActivity(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.headers = {'Accept': 'application/json',
                        'Content-Type': 'application/json'}

    def test_create_licence(self, mock_service):
        expected_response = {'dataset_licence_id': 1, 'licence_id': 'ccod'}
        mock_service.create_licence.return_value = expected_response

        response = self.app.post('/v1/licence', json={"licence_id": "ccod"}, headers=self.headers)

        self.assertEqual(201, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, expected_response)

    def test_add_activity_error(self, mock_service):
        mock_service.create_licence.side_effect = ApplicationError('some error', 500)

        response = self.app.post('/v1/licence', json={"licence_id": "ccod"}, headers=self.headers)

        self.assertEqual(500, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'error': 'Failed to create licence ccod - error: some error'})
