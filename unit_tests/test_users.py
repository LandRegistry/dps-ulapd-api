import unittest
from ulapd_api.main import app
from ulapd_api.exceptions import ApplicationError
from unittest.mock import patch


@patch('ulapd_api.views.v1.users.service')
class TestActivity(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.headers = {'Accept': 'application/json',
                        'Content-Type': 'application/json'}

    def test_get_users(self, mock_service):
        mock_service.get_all_users.return_value = [{'foo': 'bar'}, {'foo2': 'bar2'}]

        response = self.app.get('/v1/users', headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, [{'foo': 'bar'}, {'foo2': 'bar2'}])

    def test_get_users_error(self, mock_service):
        mock_service.get_all_users.side_effect = ApplicationError('some error', 500)

        response = self.app.get('/v1/users', headers=self.headers)

        self.assertEqual(500, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'error': 'Failed to get all users - error: some error'})

    def test_get_user_by_key(self, mock_service):
        mock_service.get_user_by_key.return_value = {'foo': 'bar'}

        response = self.app.get('/v1/users/user_details_id/1', headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'foo': 'bar'})

    def test_get_user_by_key_error(self, mock_service):
        mock_service.get_user_by_key.side_effect = ApplicationError('invalid key', 500)

        response = self.app.get('/v1/users/invalid_key/1', headers=self.headers)

        self.assertEqual(500, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'error': 'Failed to get user: 1 by key: invalid_key - error: invalid key'})

    def test_get_user_licences(self, mock_service):
        mock_service.get_user_licences.return_value = [{'licence_id': 'ccod'}, {'licence_id': 'ocod'}]

        response = self.app.get('/v1/users/licence/1', headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, [{'licence_id': 'ccod'}, {'licence_id': 'ocod'}])

    def test_get_user_licences_error(self, mock_service):
        mock_service.get_user_licences.side_effect = ApplicationError('some error', 500)

        response = self.app.get('/v1/users/licence/1', headers=self.headers)

        self.assertEqual(500, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'error': 'Failed to get user licences - error: some error'})

    def test_get_agreed_licence(self, mock_service):
        mock_service.get_licence_agreement.return_value = {'licence_id': 'ccod', 'agreed': True}

        response = self.app.get('/v1/users/licence/1/ccod', headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'licence_id': 'ccod', 'agreed': True})

    def test_get_agreed_licence_error(self, mock_service):
        mock_service.get_licence_agreement.side_effect = ApplicationError('some error', 500)

        response = self.app.get('/v1/users/licence/1/ccod', headers=self.headers)

        self.assertEqual(500, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'error': 'Failed to get agreed licence - error: some error'})

    def test_add_user_licence(self, mock_service):
        mock_service.manage_licence_agreement.return_value = {'licence_id': 'ccod', 'user_terms_link_id': 123}

        response = self.app.post('/v1/users/licence', json={"user_details_id": 1, "licence_id": "ccod"},
                                 headers=self.headers)

        self.assertEqual(201, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'licence_id': 'ccod', 'user_terms_link_id': 123})

    def test_add_user_licence_error(self, mock_service):
        mock_service.manage_licence_agreement.side_effect = ApplicationError('some error', 500)

        response = self.app.post('/v1/users/licence', json={"user_details_id": 1, "licence_id": "ccod"},
                                 headers=self.headers)

        self.assertEqual(500, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'error': 'Failed to add agreed licence - error: some error'})

    def test_add_multi_user_licence(self, mock_service):
        mock_service.manage_multi_licence_agreement.return_value = {'licences': ['ccod'], 'user_terms_link_id': 123}

        response = self.app.post('/v1/users/licence', json={"user_details_id": 1, "licences": ["ccod"]},
                                 headers=self.headers)

        self.assertEqual(201, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'licences': ['ccod'], 'user_terms_link_id': 123})

    def test_add_multi_user_licence_error(self, mock_service):
        mock_service.manage_multi_licence_agreement.side_effect = ApplicationError('some error', 500)

        response = self.app.post('/v1/users/licence', json={"user_details_id": 1, "licences": ["ccod"]},
                                 headers=self.headers)

        self.assertEqual(500, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'error': 'Failed to add agreed licence - error: some error'})

    def test_get_user_dataset_activity(self, mock_service):
        mock_service.get_dataset_activity.return_value = {'licence_id': 'ccod', 'foo': 'bar'}

        response = self.app.get('/v1/users/dataset-activity/1', headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'licence_id': 'ccod', 'foo': 'bar'})

    def test_get_user_dataset_activity_error(self, mock_service):
        mock_service.get_dataset_activity.side_effect = ApplicationError('some error', 500)

        response = self.app.get('/v1/users/dataset-activity/1', headers=self.headers)

        self.assertEqual(500, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'error': 'Failed to get dataset activity some error'})

    def test_create_user(self, mock_service):
        user_data = {"first_name": "foo", "last_name": "bar"}
        mock_service.create_new_user.return_value = user_data

        response = self.app.post('/v1/users', json=user_data, headers=self.headers)

        self.assertEqual(201, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, user_data)

    def test_create_user_error(self, mock_service):
        mock_service.create_new_user.side_effect = ApplicationError('some error', 500)

        response = self.app.post('/v1/users', json={"first_name": "foo", "last_name": "bar"}, headers=self.headers)

        self.assertEqual(500, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'error': 'Failed to create new user - error: some error'})

    def test_update_user_contact_preference(self, mock_service):
        user_data = {"user_id": 1, "contactable": True}
        mock_service.update_contact_preference.return_value = user_data

        response = self.app.patch('/v1/users/contact_preference', json=user_data, headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, user_data)

    def test_update_user_contact_preference_error(self, mock_service):
        mock_service.update_contact_preference.side_effect = ApplicationError('some error', 500)

        response = self.app.patch('/v1/users/contact_preference', json={"user_id": 1, "contactable": True},
                                  headers=self.headers)

        self.assertEqual(500, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'error': 'Failed to update user preference - error: some error'})

    def test_delete_user(self, mock_service):
        mock_service.delete_user.return_value = {'user_details_id': 1, 'message': 'deleted'}

        response = self.app.delete('/v1/users/1', headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'user_details_id': 1, 'message': 'deleted'})

    def test_delete_user_error(self, mock_service):
        mock_service.delete_user.side_effect = ApplicationError('some error', 500)

        response = self.app.delete('/v1/users/1', headers=self.headers)

        self.assertEqual(500, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'error': 'Failed to delete user - error: some error'})

    def test_update_api_key(self, mock_service):
        mock_service.update_api_key.return_value = {'foo': 'bar'}

        response = self.app.post('/v1/users/1/update_api_key', headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'foo': 'bar'})

    def test_update_api_key_error(self, mock_service):
        mock_service.update_api_key.side_effect = ApplicationError('some error', 500)

        response = self.app.post('/v1/users/1/update_api_key', headers=self.headers)

        self.assertEqual(500, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, {'error': 'Failed to update API key for user: 1 - error: some error'})
