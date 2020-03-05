import unittest
import requests
from flask import current_app
from ulapd_api.main import app
from ulapd_api.exceptions import ApplicationError
from unittest.mock import patch, MagicMock
from ulapd_api.dependencies.account_api import AccountAPI, _create_user_data, update_groups_for_ldap
from requests.exceptions import HTTPError, ConnectionError, Timeout
from common_utilities import errors


class TestDependencyAccountAPI(unittest.TestCase):

    def setUp(self):
        with app.app_context():
            self.app = app.test_client()
            self.url = current_app.config["ACCOUNT_API_URL"]
            self.version = current_app.config["ACCOUNT_API_VERSION"]
            self.timeout = current_app.config["DEFAULT_TIMEOUT"]
            self.error_msg = 'Test error message'

    # ****** get ****** #
    @patch("requests.Session.get")
    def test_get(self, mock_get):
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                mock_get.return_value.json.return_value = 'Success'
                mock_get.return_value.status_code = 200
                response = AccountAPI.get(self, '1234-567-890')
                self.assertEqual(response, 'Success')

    @patch("requests.Session.get")
    def test_get_with_timeout(self, mock_get):
        mock_get.side_effect = Timeout(self.error_msg)
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                with self.assertRaises(ApplicationError) as context:
                    AccountAPI.get(self, '1234-567-890')
                    self.assertTrue(ApplicationError in str(context.exception))
                self.assertEqual(context.exception.message,
                                 'Connection to account_api timed out: {}'.format(self.error_msg))
                self.assertEqual(context.exception.code, 'E711')
                self.assertEqual(context.exception.http_code, 500)

    @patch("requests.Session.get")
    def test_get_http_error(self, mock_get):
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                mock_get.side_effect = HTTPError(self.error_msg)

                with self.assertRaises(ApplicationError) as context:
                    AccountAPI.get(self, '1234-567-890')

                self.assertEqual(context.exception.message,
                                 'Received the following response from account_api: {}'.format(self.error_msg))
                self.assertEqual(context.exception.code, 'E709')
                self.assertEqual(context.exception.http_code, 500)

    @patch("requests.Session.get")
    def test_get_connection_error(self, mock_get):
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                mock_get.side_effect = ConnectionError(self.error_msg)

                with self.assertRaises(ApplicationError) as context:
                    AccountAPI.get(self, '1234-567-890')

                self.assertEqual(context.exception.message,
                                 'Encountered an error connecting to account_api: {}'.format(self.error_msg))
                self.assertEqual(context.exception.code, 'E710')
                self.assertEqual(context.exception.http_code, 500)

    # ****** create ****** #
    @patch("requests.Session.post")
    @patch("ulapd_api.dependencies.account_api._create_user_data")
    def test_create(self, mock_create, mock_post):
        data = {'email': 'john.doe@testmail.com'}
        mock_create.return_value = {'email': 'john.doe@testmail.com'}
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                mock_post.return_value.json.return_value = 'Success'
                mock_post.return_value.status_code = 200
                response = AccountAPI.create(self, data)
                self.assertEqual(response, 'Success')

    @patch("requests.Session.post")
    @patch("ulapd_api.dependencies.account_api._create_user_data")
    def test_create_with_timeout(self, mock_create, mock_post):
        mock_post.side_effect = Timeout(self.error_msg)
        data = {'foo': 'bar'}
        mock_create.return_value = {'foo': 'bar'}
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                with self.assertRaises(ApplicationError) as context:
                    AccountAPI.create(self, data)
                    self.assertTrue(ApplicationError in str(context.exception))
                self.assertEqual(context.exception.message,
                                 'Connection to account_api timed out: {}'.format(self.error_msg))
                self.assertEqual(context.exception.code, 'E711')
                self.assertEqual(context.exception.http_code, 500)

    @patch("requests.Session.post")
    @patch("ulapd_api.dependencies.account_api._create_user_data")
    def test_create_http_error(self, mock_create, mock_post):
        data = {'foo': 'bar'}
        mock_create.return_value = {'foo': 'bar'}
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                mock_post.side_effect = HTTPError(self.error_msg)

                with self.assertRaises(ApplicationError) as context:
                    AccountAPI.create(self, data)

                self.assertEqual(context.exception.message,
                                 'Received the following response from account_api: {}'.format(self.error_msg))
                self.assertEqual(context.exception.code, 'E709')
                self.assertEqual(context.exception.http_code, 500)

    @patch("requests.Session.post")
    @patch("ulapd_api.dependencies.account_api._create_user_data")
    def test_create_connection_error(self, mock_create, mock_post):
        data = {'foo': 'bar'}
        mock_create.return_value = {'foo': 'bar'}
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                mock_post.side_effect = ConnectionError(self.error_msg)

                with self.assertRaises(ApplicationError) as context:
                    AccountAPI.create(self, data)

                self.assertEqual(context.exception.message,
                                 'Encountered an error connecting to account_api: {}'.format(self.error_msg))
                self.assertEqual(context.exception.code, 'E710')
                self.assertEqual(context.exception.http_code, 500)

    # ****** delete ****** #
    @patch("requests.Session.delete")
    def test_delete(self, mock_delete):
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                mock_delete.return_value.text = 'Success'
                mock_delete.return_value.status_code = 200
                response = AccountAPI.delete(self, '1234-567-890')
                assert response == {'message': 'deleted'}

    @patch("requests.Session.delete")
    def test_delete_with_timeout(self, mock_delete):
        mock_delete.side_effect = Timeout(self.error_msg)
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                with self.assertRaises(ApplicationError) as context:
                    AccountAPI.delete(self, '1234-567-890')
                    self.assertTrue(ApplicationError in str(context.exception))
                self.assertEqual(context.exception.message,
                                 'Connection to account_api timed out: {}'.format(self.error_msg))
                self.assertEqual(context.exception.code, 'E711')
                self.assertEqual(context.exception.http_code, 500)

    @patch("requests.Session.delete")
    def test_delete_http_error(self, mock_delete):
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                mock_delete.side_effect = HTTPError(self.error_msg)

                with self.assertRaises(ApplicationError) as context:
                    AccountAPI.delete(self, '1234-567-890')

                self.assertEqual(context.exception.message,
                                 'Received the following response from account_api: {}'.format(self.error_msg))
                self.assertEqual(context.exception.code, 'E709')
                self.assertEqual(context.exception.http_code, 500)

    @patch("requests.Session.delete")
    def test_delete_connection_error(self, mock_delete):
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                mock_delete.side_effect = ConnectionError(self.error_msg)

                with self.assertRaises(ApplicationError) as context:
                    AccountAPI.delete(self, '1234-567-890')

                self.assertEqual(context.exception.message,
                                 'Encountered an error connecting to account_api: {}'.format(self.error_msg))
                self.assertEqual(context.exception.code, 'E710')
                self.assertEqual(context.exception.http_code, 500)

    # ****** activate ****** #
    @patch("requests.Session.post")
    def test_activate(self, mock_post):
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                mock_post.return_value.text = 'Success'
                mock_post.return_value.status_code = 200
                response = AccountAPI.activate(self, '1234-567-890')
                assert response == {'message': 'activated'}

    @patch("requests.Session.post")
    def test_activate_with_timeout(self, mock_post):
        mock_post.side_effect = Timeout(self.error_msg)
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                with self.assertRaises(ApplicationError) as context:
                    AccountAPI.activate(self, '1234-567-890')
                    self.assertTrue(ApplicationError in str(context.exception))
                self.assertEqual(context.exception.message,
                                 'Connection to account_api timed out: {}'.format(self.error_msg))
                self.assertEqual(context.exception.code, 'E711')
                self.assertEqual(context.exception.http_code, 500)

    @patch("requests.Session.post")
    def test_activate_http_error(self, mock_post):
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                mock_post.side_effect = HTTPError(self.error_msg)

                with self.assertRaises(ApplicationError) as context:
                    AccountAPI.activate(self, '1234-567-890')

                self.assertEqual(context.exception.message,
                                 'Received the following response from account_api: {}'.format(self.error_msg))
                self.assertEqual(context.exception.code, 'E709')
                self.assertEqual(context.exception.http_code, 500)

    @patch("requests.Session.post")
    def test_activate_connection_error(self, mock_post):
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                mock_post.side_effect = ConnectionError(self.error_msg)

                with self.assertRaises(ApplicationError) as context:
                    AccountAPI.activate(self, '1234-567-890')

                self.assertEqual(context.exception.message,
                                 'Encountered an error connecting to account_api: {}'.format(self.error_msg))
                self.assertEqual(context.exception.code, 'E710')
                self.assertEqual(context.exception.http_code, 500)

    # ****** acknowledge ****** #
    @patch("requests.Session.post")
    def test_acknowledge(self, mock_post):
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                mock_post.return_value.text = 'Success'
                mock_post.return_value.status_code = 200
                response = AccountAPI.acknowledge(self, '1234-567-890')
                assert response == {'message': 'acknowledged'}

    @patch("requests.Session.post")
    def test_acknowledge_with_timeout(self, mock_post):
        mock_post.side_effect = Timeout(self.error_msg)
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                with self.assertRaises(ApplicationError) as context:
                    AccountAPI.acknowledge(self, '1234-567-890')
                    self.assertTrue(ApplicationError in str(context.exception))
                self.assertEqual(context.exception.message,
                                 'Connection to account_api timed out: {}'.format(self.error_msg))
                self.assertEqual(context.exception.code, 'E711')
                self.assertEqual(context.exception.http_code, 500)

    @patch("requests.Session.post")
    def test_acknowledge_http_error(self, mock_post):
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                mock_post.side_effect = HTTPError(self.error_msg)

                with self.assertRaises(ApplicationError) as context:
                    AccountAPI.acknowledge(self, '1234-567-890')

                self.assertEqual(context.exception.message,
                                 'Received the following response from account_api: {}'.format(self.error_msg))
                self.assertEqual(context.exception.code, 'E709')
                self.assertEqual(context.exception.http_code, 500)

    @patch("requests.Session.post")
    def test_acknowledge_connection_error(self, mock_post):
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                mock_post.side_effect = ConnectionError(self.error_msg)

                with self.assertRaises(ApplicationError) as context:
                    AccountAPI.acknowledge(self, '1234-567-890')

                self.assertEqual(context.exception.message,
                                 'Encountered an error connecting to account_api: {}'.format(self.error_msg))
                self.assertEqual(context.exception.code, 'E710')
                self.assertEqual(context.exception.http_code, 500)

    # ****** handle_role *******#
    @patch("requests.Session.post")
    def test_handle_role(self, mock_post):
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                mock_post.return_value.text = 'Success'
                mock_post.return_value.status_code = 200
                response = AccountAPI.handle_role(self, {'groups': {'nps_sample': True}, 'ldap_id': '11-22'})
                assert response == {'message': 'success'}

    @patch("requests.Session.post")
    def test_handle_role_with_timeout(self, mock_post):
        mock_post.side_effect = Timeout(self.error_msg)
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                with self.assertRaises(ApplicationError) as context:
                    AccountAPI.handle_role(self, {'groups': {'nps_sample': True}, 'ldap_id': '11-22'})
                    self.assertTrue(ApplicationError in str(context.exception))
                self.assertEqual(context.exception.message,
                                 'Connection to account_api timed out: {}'.format(self.error_msg))
                self.assertEqual(context.exception.code, 'E711')
                self.assertEqual(context.exception.http_code, 500)

    @patch("requests.Session.post")
    def test_handle_role_http_error(self, mock_post):
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                mock_post.side_effect = HTTPError(self.error_msg)

                with self.assertRaises(ApplicationError) as context:
                    AccountAPI.handle_role(self, {'groups': {'nps_sample': True}, 'ldap_id': '11-22'})

                self.assertEqual(context.exception.message,
                                 'Received the following response from account_api: {}'.format(self.error_msg))
                self.assertEqual(context.exception.code, 'E709')
                self.assertEqual(context.exception.http_code, 500)

    @patch("requests.Session.post")
    def test_handle_role_connection_error(self, mock_post):
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                mock_post.side_effect = ConnectionError(self.error_msg)

                with self.assertRaises(ApplicationError) as context:
                    AccountAPI.handle_role(self, {'groups': {'nps_sample': True}, 'ldap_id': '11-22'})

                self.assertEqual(context.exception.message,
                                 'Encountered an error connecting to account_api: {}'.format(self.error_msg))
                self.assertEqual(context.exception.code, 'E710')
                self.assertEqual(context.exception.http_code, 500)

    # ******** update_groups ********* #
    @patch("requests.Session.patch")
    def test_update_groups(self, mock_patch):
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                mock_patch.return_value.text = 'Success'
                mock_patch.return_value.status_code = 200
                response = AccountAPI.update_groups(self, {'nps_sample': True}, '11-22')
                assert response == {'message': 'groups updated'}

    @patch("requests.Session.patch")
    def test_update_groups_with_timeout(self, mock_patch):
        mock_patch.side_effect = Timeout(self.error_msg)
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                with self.assertRaises(ApplicationError) as context:
                    AccountAPI.update_groups(self, {'nps_sample': True}, '11-22')
                    self.assertTrue(ApplicationError in str(context.exception))
                self.assertEqual(context.exception.message,
                                 'Connection to account_api timed out: {}'.format(self.error_msg))
                self.assertEqual(context.exception.code, 'E711')
                self.assertEqual(context.exception.http_code, 500)

    @patch("requests.Session.patch")
    def test_update_groups_http_error(self, mock_patch):
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                mock_patch.side_effect = HTTPError(self.error_msg)

                with self.assertRaises(ApplicationError) as context:
                    AccountAPI.update_groups(self, {'nps_sample': True}, '11-22')

                self.assertEqual(context.exception.message,
                                 'Received the following response from account_api: {}'.format(self.error_msg))
                self.assertEqual(context.exception.code, 'E709')
                self.assertEqual(context.exception.http_code, 500)

    @patch("requests.Session.patch")
    def test_update_groups_connection_error(self, mock_patch):
        with app.app_context() as ac:
            ac.g.trace_id = None
            ac.g.requests = requests.Session()
            with app.test_request_context():
                mock_patch.side_effect = ConnectionError(self.error_msg)

                with self.assertRaises(ApplicationError) as context:
                    AccountAPI.update_groups(self, {'nps_sample': True}, '11-22')

                self.assertEqual(context.exception.message,
                                 'Encountered an error connecting to account_api: {}'.format(self.error_msg))
                self.assertEqual(context.exception.code, 'E710')
                self.assertEqual(context.exception.http_code, 500)

    # ****** _create_user_data ****** #
    def test_create_user_data_uk(self):
        data = {
            'organisation_name': 'Company Ltd',
            'user_type': 'organisation-uk',
            'email': 'john.smith@fakemail.com',
            'first_name': 'John',
            'last_name': 'Smith'
        }
        expected_result = {
            'org_name': 'Company Ltd',
            'user_type': 'uk-organisation',
            'email': 'john.smith@fakemail.com',
            'first_name': 'John',
            'surname': 'Smith'
        }
        result = _create_user_data(data)
        self.assertDictEqual(result, expected_result)

    def test_create_user_data_overseas(self):
        data = {
            'organisation_name': 'Company Ltd',
            'user_type': 'organisation-overseas',
            'email': 'john.smith@fakemail.com',
            'first_name': 'John',
            'last_name': 'Smith'
        }
        expected_result = {
            'org_name': 'Company Ltd',
            'user_type': 'overseas-organisation',
            'email': 'john.smith@fakemail.com',
            'first_name': 'John',
            'surname': 'Smith'
        }
        result = _create_user_data(data)
        self.assertDictEqual(result, expected_result)

    def test_create_user_data_personal(self):
        data = {
            'user_type': 'personal',
            'email': 'john.smith@fakemail.com',
            'first_name': 'John',
            'last_name': 'Smith'
        }
        expected_result = {
            'user_type': 'personal',
            'email': 'john.smith@fakemail.com',
            'first_name': 'John',
            'surname': 'Smith'
        }
        result = _create_user_data(data)
        self.assertDictEqual(result, expected_result)

    # ********* update_groups_for_ldap *********** #
    @patch('ulapd_api.dependencies.account_api.AccountAPI.update_groups')
    def test_update_groups_for_ldap(self, mock_account):
        mock_account.return_value = MagicMock()
        with app.app_context() as ac:
            ac.g.trace_id = None
            update_groups_for_ldap('112-122', {'nps': True})
        mock_account.assert_called_once()

    @patch('ulapd_api.dependencies.account_api.AccountAPI')
    def test_update_groups_for_ldap_error(self, mock_account):
        error = ApplicationError(*errors.get("ulapd_api", "ACCOUNT_API_HTTP_ERROR"))
        mock_account.return_value.update_groups.side_effect = error
        with app.app_context() as ac:
            update_groups_retry = current_app.config["UPDATE_GROUPS_RETRY"]
            ac.g.trace_id = None
            update_groups_for_ldap('112-122', {'nps': True})
        self.assertEqual(mock_account.return_value.update_groups.call_count, int(update_groups_retry))

    @patch('ulapd_api.dependencies.account_api.app')
    @patch('ulapd_api.dependencies.account_api.AccountAPI')
    def test_update_groups_app_error(self, mock_account, mock_app):
        error = ('ulapd_api', 'ACCOUNT_API_HTTP_ERROR')
        mock_account.side_effect = ApplicationError(*errors.get(*error))

        update_groups_for_ldap('112-122', {'nps': True})
        mock_app.logger.error.assert_called_once()
