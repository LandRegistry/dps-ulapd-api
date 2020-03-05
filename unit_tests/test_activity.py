import unittest
from ulapd_api.main import app
from ulapd_api.exceptions import ApplicationError
from unittest.mock import patch


@patch('ulapd_api.views.v1.activity.activity_service')
class TestActivity(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.headers = {'Accept': 'application/json',
                        'Content-Type': 'application/json'}

    def test_get_activity(self, mock_service):
        mock_service.get_user_activity_list.return_value = [{'foo': 'bar'}]

        response = self.app.get('/v1/activities/1', headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, [{'foo': 'bar'}])

    def test_get_activity_error(self, mock_service):
        mock_service.get_user_activity_list.side_effect = ApplicationError('some error', 500)

        response = self.app.get('/v1/activities/1', headers=self.headers)

        self.assertEqual(500, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'error': 'Failed to get user activity: 1 - error: some error'})

    def test_add_activity(self, mock_service):
        mock_service.add_user_activity.return_value = {'foo': 'bar'}

        response = self.app.post('/v1/activities', json={"foo": "bar"}, headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'foo': 'bar'})

    def test_add_activity_error(self, mock_service):
        mock_service.add_user_activity.side_effect = ApplicationError('some error', 500)

        response = self.app.post('/v1/activities', json={"foo": "bar"}, headers=self.headers)

        self.assertEqual(500, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'error': 'Failed to add activity - error: some error'})
