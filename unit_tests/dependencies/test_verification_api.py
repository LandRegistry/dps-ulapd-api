import unittest
import requests
from flask import current_app
from ulapd_api.main import app
from ulapd_api.exceptions import ApplicationError
from unittest.mock import patch
from ulapd_api.dependencies.verification_api import VerificationAPI, _create_user_data
from requests.exceptions import HTTPError, ConnectionError, Timeout


class TestDependencyVerificationAPI(unittest.TestCase):

    def setUp(self):
        with app.app_context():
            self.app = app.test_client()
            self.url = current_app.config["VERIFICATION_API_URL"]
            self.version = current_app.config["VERIFICATION_API_VERSION"]
            self.timeout = current_app.config["DEFAULT_TIMEOUT"]
            self.error_msg = 'Test error message'

    # ****** create ****** #
    @patch("requests.Session.post")
    @patch("ulapd_api.dependencies.verification_api._create_user_data")
    def test_create(self, mock_create, mock_post):
        data = {'user_id': '1234'}
        mock_create.return_value = {'user_id': '1234'}
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                mock_post.return_value.json.return_value = 'Success'
                mock_post.return_value.status_code = 200
                response = VerificationAPI.create(self, data)
                self.assertEqual(response, 'Success')

    @patch("requests.Session.post")
    @patch("ulapd_api.dependencies.verification_api._create_user_data")
    def test_create_with_timeout(self, mock_create, mock_post):
        mock_post.side_effect = Timeout(self.error_msg)
        data = {'foo': 'bar'}
        mock_create.return_value = {'foo': 'bar'}
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                with self.assertRaises(ApplicationError) as context:
                    VerificationAPI.create(self, data)
                    self.assertTrue(ApplicationError in str(context.exception))
                self.assertEqual(context.exception.message,
                                 'Connection to verification_api timed out: {}'.format(self.error_msg))
                self.assertEqual(context.exception.code, 'E714')
                self.assertEqual(context.exception.http_code, 500)

    @patch("requests.Session.post")
    @patch("ulapd_api.dependencies.verification_api._create_user_data")
    def test_create_http_error(self, mock_create, mock_post):
        data = {'foo': 'bar'}
        mock_create.return_value = {'foo': 'bar'}
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                mock_post.side_effect = HTTPError(self.error_msg)

                with self.assertRaises(ApplicationError) as context:
                    VerificationAPI.create(self, data)

                self.assertEqual(context.exception.message,
                                 'Received the following response from verification_api: {}'.format(self.error_msg))
                self.assertEqual(context.exception.code, 'E712')
                self.assertEqual(context.exception.http_code, 500)

    @patch("requests.Session.post")
    @patch("ulapd_api.dependencies.verification_api._create_user_data")
    def test_create_connection_error(self, mock_create, mock_post):
        data = {'foo': 'bar'}
        mock_create.return_value = {'foo': 'bar'}
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                mock_post.side_effect = ConnectionError(self.error_msg)

                with self.assertRaises(ApplicationError) as context:
                    VerificationAPI.create(self, data)

                self.assertEqual(context.exception.message,
                                 'Encountered an error connecting to verification_api: {}'.format(self.error_msg))
                self.assertEqual(context.exception.code, 'E713')
                self.assertEqual(context.exception.http_code, 500)

    # ****** _create_user_data ****** #
    def test_create_user_data_uk(self):
        data = {
            'user_id': '1234',
            'user_type_id': '1',
            'user_details_id': '1234',
            'ldap_id': '1234-567-890',
            'organisation_name': 'Company Ltd',
            'user_type': 'organisation-uk',
            'email': 'john.smith@fakemail.com',
            'first_name': 'John',
            'last_name': 'Smith'
        }
        expected_result = {
            'user_id': '1234',
            'ldap_id': '1234-567-890',
            'status': 'Pending',
            'registration_data': {
                'organisation_name': 'Company Ltd',
                'user_type': 'organisation-uk',
                'email': 'john.smith@fakemail.com',
                'first_name': 'John',
                'last_name': 'Smith'
            }
        }
        result = _create_user_data(data)
        self.assertDictEqual(result, expected_result)

    def test_create_user_data_overseas(self):
        data = {
            'user_id': '1234',
            'user_type_id': '2',
            'user_details_id': '1234',
            'ldap_id': '1234-567-890',
            'organisation_name': 'Company Ltd',
            'user_type': 'organisation-overseas',
            'email': 'john.smith@fakemail.com',
            'first_name': 'John',
            'last_name': 'Smith'
        }
        expected_result = {
            'user_id': '1234',
            'ldap_id': '1234-567-890',
            'status': 'Approved',
            'registration_data': {
                'organisation_name': 'Company Ltd',
                'user_type': 'organisation-overseas',
                'email': 'john.smith@fakemail.com',
                'first_name': 'John',
                'last_name': 'Smith'
            }
        }
        result = _create_user_data(data)
        self.assertDictEqual(result, expected_result)

    def test_create_user_data_personal(self):
        data = {
            'user_id': '1234',
            'user_type_id': '3',
            'user_details_id': '1234',
            'ldap_id': '1234-567-890',
            'user_type': 'personal',
            'email': 'john.smith@fakemail.com',
            'first_name': 'John',
            'last_name': 'Smith'
        }
        expected_result = {
            'user_id': '1234',
            'ldap_id': '1234-567-890',
            'status': 'Approved',
            'registration_data': {
                'user_type': 'personal',
                'email': 'john.smith@fakemail.com',
                'first_name': 'John',
                'last_name': 'Smith'
            }
        }
        result = _create_user_data(data)
        self.assertDictEqual(result, expected_result)
