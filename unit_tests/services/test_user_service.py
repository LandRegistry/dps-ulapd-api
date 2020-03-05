import os
import json
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from sqlalchemy.exc import ProgrammingError
from common_utilities import errors
from ulapd_api.main import app
from ulapd_api.services import user_service as service
from ulapd_api.exceptions import ApplicationError
from unit_tests.utilities import helpers as helpers
from unit_tests.services.data import data_access_data


@patch('ulapd_api.utilities.decorators.db')
@patch('ulapd_api.services.user_service.db')
class TestUserService(unittest.TestCase):
    directory = os.path.dirname(__file__)
    user_data = json.loads(open(os.path.join(directory, 'data/user_details_data.json'), 'r').read())

    def setUp(self):
        self.app = app.test_client()
        self.error = ProgrammingError('stuff failed', 'Program', 'Error')
        self.user_type = {
            "date_added": datetime.now(),
            "user_type": "personal-uk",
            "user_type_id": 1
        }
        self.datasets = {
            'ccod': {
                'date_agreed': '2019-11-15 15:47:57.322151',
                'private': False,
                'valid_licence': True
            },
            'nps': {
                'date_agreed': None,
                'private': True,
                'valid_licence': True
            }
        }

    @patch('ulapd_api.services.user_service.UserDetails')
    @patch('ulapd_api.services.user_service._extract_rows')
    @patch('ulapd_api.services.user_service.get_user_type')
    def test_get_all_users(self, mock_type, mock_extract, mock_user, *_):
        mock_user.return_value = MagicMock()
        user_list = [helpers.generate_test_user(), helpers.generate_test_user()]
        mock_extract.return_value = user_list
        mock_type.return_value = self.user_type

        result = service.get_all_users()
        self.assertIn('user_details', result[0])
        self.assertIn('user_type', result[0])
        self.assertEqual(result[0]['user_type'], self.user_type)

    @patch('ulapd_api.services.user_service.UserDetails')
    @patch('ulapd_api.services.user_service.get_user_type')
    @patch('ulapd_api.services.user_service._build_users_datasets')
    @patch('ulapd_api.services.user_service.Contact')
    @patch('ulapd_api.services.user_service._build_contact_preferences')
    def test_get_user_by_key(self, mock_preferences, mock_contact, mock_build, mock_type, mock_user, *_):
        mock_user.get_user_details_by_id.return_value = helpers.generate_test_user()
        mock_user.get_user_details_by_email.return_value = helpers.generate_test_user()
        mock_user.get_user_details_by_api_key.return_value = helpers.generate_test_user()
        mock_user.get_user_details_by_ldap_id.return_value = helpers.generate_test_user()
        mock_type.return_value = self.user_type
        mock_build.return_value = self.datasets
        mock_contact.return_value = MagicMock()
        mock_preferences.return_value = ['email', 'phone']

        key_list = [
            {'user_details_id': 6},
            {'email': 'test@email.com'},
            {'api_key': 'an-api-key'},
            {'ldap_id': 'an_ldap_id'}
        ]

        for key in key_list:
            for k, v in key.items():
                result = service.get_user_by_key({'key': k, 'value': v})
                self.assertEqual(result['datasets']['ccod']['valid_licence'], True)
                self.assertIn('user_details', result)
                self.assertEqual(result['user_details']['user_type']['user_type'], 'personal-uk')

    def test_get_user_by_key_incorrect_key(self, *_):
        with self.assertRaises(ApplicationError) as context:
            service.get_user_by_key({'key': 'invalid_key', 'value': 'foo'})

        self.assertEqual(context.exception.message, 'Incorrect key: invalid_key')

    @patch('ulapd_api.services.user_service.UserDetails')
    def test_get_user_by_key_no_user(self, mock_user, *_):
        mock_user.get_user_details_by_id.return_value = None
        with self.assertRaises(ApplicationError) as context:
            service.get_user_by_key({'key': 'user_details_id', 'value': '6'})

        expected_err = ('ulapd_api', 'USER_NOT_FOUND')
        expected_err_message = errors.get_message(*expected_err, filler='6')
        expected_err_code = errors.get_code(*expected_err)

        self.assertEqual(context.exception.message, expected_err_message)
        self.assertEqual(context.exception.code, expected_err_code)

    @patch('ulapd_api.services.user_service.UserDetails')
    def test_get_user_details(self, mock_user, *_):
        mock_user.get_user_details_by_id.return_value = helpers.generate_test_user()

        result = service.get_user_details(123)
        self.assertEqual(result['user_details_id'], 123)

    @patch('ulapd_api.services.user_service.UserDetails')
    def test_get_user_details_no_user(self, mock_user, *_):
        mock_user.get_user_details_by_id.return_value = None
        with self.assertRaises(ApplicationError) as context:
            service.get_user_details(8)

        expected_err = ('ulapd_api', 'USER_NOT_FOUND')
        expected_err_message = errors.get_message(*expected_err, filler='8')
        expected_err_code = errors.get_code(*expected_err)

        self.assertEqual(context.exception.message, expected_err_message)
        self.assertEqual(context.exception.code, expected_err_code)

    @patch('ulapd_api.services.user_service.UserType')
    def test_get_user_type(self, mock_type, *_):
        test_type = MagicMock()
        test_type.as_dict.return_value = self.user_type
        mock_type.get_user_type_by_id.return_value = test_type

        result = service.get_user_type(1)
        self.assertEqual(result['user_type'], 'personal-uk')

    @patch('ulapd_api.services.user_service.UserType')
    def test_get_user_type_no_type(self, mock_type, *_):
        mock_type.get_user_type_by_id.return_value = None
        with self.assertRaises(ApplicationError) as context:
            service.get_user_type(10)

        expected_err = ('ulapd_api', 'USER_TYPE_NOT_FOUND')
        expected_err_message = errors.get_message(*expected_err, filler='10')
        expected_err_code = errors.get_code(*expected_err)

        self.assertEqual(context.exception.message, expected_err_message)
        self.assertEqual(context.exception.code, expected_err_code)

    @patch('ulapd_api.services.user_service.UserTermsLink')
    @patch('ulapd_api.services.user_service._check_agreement')
    def test_get_licence_agreement(self, mock_agreement, mock_terms, *_):
        test_terms = MagicMock()
        test_terms.date_agreed = '2019-11-21 12:10:57.070764'
        mock_terms.get_user_terms_by_licence_name.return_value = test_terms
        mock_agreement.return_value = True

        result = service.get_licence_agreement(1, 'ccod')
        self.assertEqual(result['valid_licence'], True)
        self.assertEqual(result['date_agreed'], '2019-11-21 12:10:57.070764')

    @patch('ulapd_api.services.user_service.UserTermsLink')
    def test_get_licence_agreement_no_row(self, mock_terms, *_):
        mock_terms.get_user_terms_by_licence_name.return_value = None

        result = service.get_licence_agreement(9, 'ccod')
        self.assertEqual(result['valid_licence'], False)
        self.assertEqual(result['date_agreed'], None)

    @patch('ulapd_api.services.user_service.UserDetails')
    @patch('ulapd_api.services.user_service.Licence')
    @patch('ulapd_api.services.user_service._extract_rows')
    @patch('ulapd_api.services.user_service.UserTermsLink.get_user_terms_by_licence_name')
    @patch('ulapd_api.services.user_service._check_freemium')
    @patch('ulapd_api.services.user_service.UserTermsLink')
    @patch('ulapd_api.services.user_service._handle_ldap_group')
    def test_manage_licence_agreement(self, mock_ldap, mock_user_terms, mock_freemium, mock_terms_get, mock_extract,
                                      mock_licence, mock_user, *_):
        user = MagicMock()
        user.user_details_id = 1
        mock_user.get_user_details_by_id.return_value = user
        mock_licence.return_value = MagicMock()
        mock_extract.return_value = [{'licence_id': 'ccod'}]
        mock_freemium.return_value = False
        terms_link = MagicMock()
        terms_link.user_terms_link_id = 33
        mock_user_terms.return_value = terms_link
        mock_ldap.return_value = MagicMock()
        mock_terms_get.return_value = MagicMock()

        result = service.manage_licence_agreement({'licence_id': 'ccod', 'user_details_id': 1})
        self.assertEqual(result, {'licence_id': 'ccod', 'user_details_id': 1, 'link_id': 33})

    @patch('ulapd_api.services.user_service.UserDetails')
    def test_manage_licence_agreement_no_user(self, mock_user, *_):
        mock_user.get_user_details_by_id.return_value = None

        with self.assertRaises(ApplicationError) as context:
            service.manage_licence_agreement({'licence_id': 'ccod', 'user_details_id': 1})

        expected_err = ('ulapd_api', 'LICENCE_AGREE_ERROR')
        expected_err_message = errors.get_message(*expected_err, filler='User "1" not found')
        expected_err_code = errors.get_code(*expected_err)

        self.assertEqual(context.exception.message, expected_err_message)
        self.assertEqual(context.exception.code, expected_err_code)

    @patch('ulapd_api.services.user_service.app.logger.info')
    @patch('ulapd_api.services.user_service.UserDetails')
    @patch('ulapd_api.services.user_service.Licence')
    @patch('ulapd_api.services.user_service._extract_rows')
    @patch('ulapd_api.services.user_service.UserTermsLink.get_user_terms_by_licence_name')
    @patch('ulapd_api.services.user_service._check_freemium')
    @patch('ulapd_api.services.user_service.UserTermsLink')
    @patch('ulapd_api.services.user_service._handle_ldap_group')
    def test_manage_licence_agreement_freemium(self, mock_ldap, mock_user_terms, mock_freemium, mock_terms_get,
                                               mock_extract, mock_licence, mock_user, mock_log, *_):
        user = MagicMock()
        user.user_details_id = 1
        mock_user.get_user_details_by_id.return_value = user
        mock_licence.return_value = MagicMock()
        mock_extract.return_value = [{'licence_id': 'res_cov_direct'}, {'licence_id': 'res_cov_exploration'},
                                     {'licence_id': 'res_cov_commercial'}]
        mock_freemium.return_value = True
        terms_link = MagicMock()
        terms_link.user_terms_link_id = 33
        mock_user_terms.return_value = terms_link
        mock_ldap.return_value = MagicMock()
        mock_terms_get.return_value = None

        result = service.manage_licence_agreement({'licence_id': 'res_cov', 'user_details_id': 1})
        self.assertEqual(result, {'licence_id': 'res_cov_direct', 'user_details_id': 1, 'link_id': 33})
        mock_log.assert_called_with('User 1 does not have the role res_cov so update ldap...')

    @patch('ulapd_api.services.user_service.UserDetails')
    def test_manage_multi_licence_agreement_no_user(self, mock_user, *_):
        mock_user.get_user_details_by_id.return_value = None

        with self.assertRaises(ApplicationError) as context:
            service.manage_multi_licence_agreement({'licences': [{'licence_id': 'ccod', 'agreed': True}],
                                                    'user_details_id': 1})

        expected_err = ('ulapd_api', 'LICENCE_AGREE_ERROR')
        expected_err_message = errors.get_message(*expected_err, filler='User "1" not found')
        expected_err_code = errors.get_code(*expected_err)

        self.assertEqual(context.exception.message, expected_err_message)
        self.assertEqual(context.exception.code, expected_err_code)

    # @patch('ulapd_api.services.user_service.app.logger.info')
    @patch('ulapd_api.services.user_service.UserDetails')
    @patch('ulapd_api.services.user_service._extract_rows')
    @patch('ulapd_api.services.user_service.UserTermsLink.get_user_terms_by_user_id')
    @patch('ulapd_api.services.user_service.Licence')
    @patch('ulapd_api.services.user_service.UserTermsLink')
    @patch('ulapd_api.services.user_service.UserTermsLink.delete_user_licence_agreement')
    @patch('ulapd_api.services.user_service._handle_ldap_freemium_updates')
    @patch('ulapd_api.services.user_service.update_groups_for_ldap')
    def test_manage_multi_licence_agreement(self, mock_ldap, mock_freemium, mock_delete, mock_terms, mock_licence,
                                            mock_get, mock_extract, mock_user, mock_log, *_):
        user = MagicMock()
        user.user_details_id = 1
        mock_user.get_user_details_by_id.return_value = user
        mock_get.return_value = MagicMock()
        mock_extract.return_value = [{'licence_id': 'ocod'}]
        ccod_data = MagicMock()
        ccod_data.licence_name = 'ccod'
        ccod_data.dataset_name = 'ccod'
        ocod_data = MagicMock()
        ocod_data.licence_name = 'ocod'
        ocod_data.dataset_name = 'ocod'
        mock_licence.get_all_licences.return_value = [ccod_data, ocod_data]
        mock_terms.return_value = MagicMock()
        mock_delete.return_value = MagicMock()
        mock_ldap.return_value = MagicMock()
        mock_freemium.return_value = {'ccod': True, 'ocod': False}

        result = service.manage_multi_licence_agreement({'licences': [{'licence_id': 'ccod', 'agreed': True},
                                                                      {'licence_id': 'ocod', 'agreed': False}],
                                                         'user_details_id': 1})
        self.assertEqual(result, {'ccod': True, 'ocod': False})
        # mock_log.assert_called_with("Sending these groups - {'ccod': True, 'ocod': False}, for ldap update for
        # user 1")

    # @patch('ulapd_api.services.user_service.app.logger.info')
    @patch('ulapd_api.services.user_service.UserDetails')
    @patch('ulapd_api.services.user_service._extract_rows')
    @patch('ulapd_api.services.user_service.UserTermsLink.get_user_terms_by_user_id')
    @patch('ulapd_api.services.user_service.Licence')
    @patch('ulapd_api.services.user_service.UserTermsLink')
    @patch('ulapd_api.services.user_service.UserTermsLink.delete_user_licence_agreement')
    @patch('ulapd_api.services.user_service._handle_ldap_freemium_updates')
    @patch('ulapd_api.services.user_service.update_groups_for_ldap')
    def test_manage_multi_licence_agreement_freemium(self, mock_ldap, mock_freemium, mock_delete, mock_terms,
                                                     mock_licence, mock_get, mock_extract, mock_user, mock_log, *_):
        user = MagicMock()
        user.user_details_id = 1
        mock_user.get_user_details_by_id.return_value = user
        mock_get.return_value = MagicMock()
        mock_extract.return_value = [{'licence_id': 'ocod'}]
        ccod_data = MagicMock()
        ccod_data.licence_name = 'ccod'
        ccod_data.dataset_name = 'ccod'
        ocod_data = MagicMock()
        ocod_data.licence_name = 'ocod'
        ocod_data.dataset_name = 'ocod'
        res_cov_direct_data = MagicMock()
        res_cov_direct_data.licence_name = 'res_cov_direct'
        res_cov_direct_data.dataset_name = 'res_cov'
        res_cov_exploration_data = MagicMock()
        res_cov_exploration_data.licence_name = 'res_cov_exploration'
        res_cov_exploration_data.dataset_name = 'res_cov'
        res_cov_commercial_data = MagicMock()
        res_cov_commercial_data.licence_name = 'res_cov_commercial'
        res_cov_commercial_data.dataset_name = 'res_cov'
        mock_licence.get_all_licences.return_value = [ccod_data, ocod_data, res_cov_direct_data,
                                                      res_cov_exploration_data, res_cov_commercial_data]
        mock_terms.return_value = MagicMock()
        mock_delete.return_value = MagicMock()
        mock_ldap.return_value = MagicMock()
        mock_freemium.return_value = {'ccod': True, 'ocod': False, 'res_cov': True}
        payload = {'licences': [{'licence_id': 'ccod', 'agreed': True}, {'licence_id': 'ocod', 'agreed': False},
                                {'licence_id': 'res_cov_direct', 'agreed': False},
                                {'licence_id': 'res_cov_exploration', 'agreed': False},
                                {'licence_id': 'res_cov_commercial', 'agreed': True}],
                   'user_details_id': 1}

        result = service.manage_multi_licence_agreement(payload)
        self.assertEqual(result, {'ccod': True, 'ocod': False, 'res_cov': True})
        # mock_log.assert_called_with("Sending these groups - {'ccod': True, 'ocod': False, 'res_cov': True}, "
        #                             "for ldap update for user 1")

    @patch('ulapd_api.services.user_service.UserDetails')
    @patch('ulapd_api.services.user_service._build_user_dataset_activity')
    def test_get_dataset_activity(self, mock_activity, mock_user, *_):
        mock_user.get_user_details_by_id.return_value = MagicMock()
        mock_activity.return_value = {'foo': 'bar'}

        result = service.get_dataset_activity(1)
        self.assertEqual(result, {'foo': 'bar'})

    @patch('ulapd_api.services.user_service.UserDetails')
    def test_get_dataset_activity_no_user(self, mock_user, *_):
        mock_user.get_user_details_by_id.return_value = None

        with self.assertRaises(ApplicationError) as context:
            service.get_dataset_activity(1)

        expected_err = ('ulapd_api', 'USER_NOT_FOUND')
        expected_err_message = errors.get_message(*expected_err, filler='1')
        expected_err_code = errors.get_code(*expected_err)

        self.assertEqual(context.exception.message, expected_err_message)
        self.assertEqual(context.exception.code, expected_err_code)

    @patch('ulapd_api.services.user_service.AccountAPI')
    @patch('ulapd_api.services.user_service.VerificationAPI')
    @patch('ulapd_api.services.user_service._process_new_user_data')
    @patch('ulapd_api.services.user_service.UserDetails')
    @patch('ulapd_api.services.user_service.Contact')
    def test_create_new_user_personal(self, mock_contact, mock_user, mock_process, mock_verification,
                                      mock_account, *_):
        mock_account.return_value.create.return_value = {'user_id': '123-343-454-dd5-333'}
        user = self.user_data
        user['api_key'] = '456-343-2ewe-4343'
        user['user_type_id'] = 1
        user['contactable'] = True
        mock_process.return_value = user
        mock_user.return_value = MagicMock()
        mock_verification.create.return_value = MagicMock()
        mock_account.return_value.activate.return_value = MagicMock()
        mock_contact.return_value = MagicMock()

        result = service.create_new_user(user)
        self.assertEqual(result['ldap_id'], '123-343-454-dd5-333')
        self.assertEqual(result['api_key'], '456-343-2ewe-4343')

    @patch('ulapd_api.services.user_service.AccountAPI')
    @patch('ulapd_api.services.user_service.VerificationAPI')
    @patch('ulapd_api.services.user_service._process_new_user_data')
    @patch('ulapd_api.services.user_service.UserDetails')
    @patch('ulapd_api.services.user_service.Contact')
    def test_create_new_user_uk_org(self, mock_contact, mock_user, mock_process, mock_verification, mock_account, *_):
        mock_account.return_value.create.return_value = {'user_id': '123-343-454-dd5-333'}
        user = self.user_data
        user['api_key'] = '456-343-2ewe-4343'
        user['user_type_id'] = 3
        user['user_type'] = 'organisation-uk'
        user['contactable'] = True
        mock_process.return_value = user
        mock_user.return_value = MagicMock()
        mock_verification.create.return_value = MagicMock()
        mock_account.return_value.acknowledge.return_value = MagicMock()
        mock_contact.return_value = MagicMock()

        result = service.create_new_user(user)
        self.assertEqual(result['ldap_id'], '123-343-454-dd5-333')
        self.assertEqual(result['api_key'], '456-343-2ewe-4343')

    @patch('ulapd_api.services.user_service.UserTermsLink')
    @patch('ulapd_api.services.user_service.Activity')
    @patch('ulapd_api.services.user_service.Contact')
    @patch('ulapd_api.services.user_service.UserDetails')
    def test_delete_user(self, mock_user, mock_contact, mock_activity, mock_terms, *_):
        mock_terms.return_value = MagicMock()
        mock_activity.return_value = MagicMock()
        mock_contact.return_value = MagicMock()
        mock_user.get_user_details_by_id.return_value = helpers.generate_test_user()

        result = service.delete_user(123)
        expected_result = {
            'user_id': 123,
            'message': 'user deleted'
        }
        self.assertEqual(result, expected_result)

    @patch('ulapd_api.services.user_service.UserTermsLink')
    @patch('ulapd_api.services.user_service.Activity')
    @patch('ulapd_api.services.user_service.Contact')
    @patch('ulapd_api.services.user_service.UserDetails')
    def test_delete_user_no_user(self, mock_user, mock_contact, mock_activity, mock_terms, *_):
        mock_terms.return_value = MagicMock()
        mock_activity.return_value = MagicMock()
        mock_contact.return_value = MagicMock()
        mock_user.get_user_details_by_id.return_value = None

        with self.assertRaises(ApplicationError) as context:
            service.delete_user(123)

        expected_err = ('ulapd_api', 'DELETE_USER_ERROR')
        expected_err_message = errors.get_message(*expected_err, filler='User "123" not found')
        expected_err_code = errors.get_code(*expected_err)

        self.assertEqual(context.exception.message, expected_err_message)
        self.assertEqual(context.exception.code, expected_err_code)

    @patch('ulapd_api.services.user_service.UserDetails')
    @patch('ulapd_api.services.user_service.Contact')
    def test_update_contact_preference(self, mock_contact, mock_user, *_):
        mock_user.get_user_details_by_id.return_value = helpers.generate_test_user()
        data = {
            'user_id': 123,
            'staff_id': 'cs000aa',
            'contactable': True,
            'contact_preferences': ['Telephone', 'Email']
        }
        result = service.update_contact_preference(data)
        self.assertEqual(result['contact_preferences'], ['Telephone', 'Email'])
        mock_contact.assert_called()

    @patch('ulapd_api.services.user_service.UserDetails')
    @patch('ulapd_api.services.user_service.Contact')
    def test_update_contact_preference_no_preference(self, mock_contact, mock_user, *_):
        mock_user.get_user_details_by_id.return_value = helpers.generate_test_user()
        data = {
            'user_id': 123,
            'staff_id': 'cs000aa',
            'contactable': False,
            'contact_preferences': []
        }
        result = service.update_contact_preference(data)
        self.assertEqual(result['contact_preferences'], [])
        mock_contact.delete_contact_preferences_for_user.assert_called()

    @patch('ulapd_api.services.user_service.UserDetails')
    def test_update_contact_preference_no_user(self, mock_user, *_):
        mock_user.get_user_details_by_id.return_value = None

        with self.assertRaises(ApplicationError) as context:
            service.update_contact_preference({'user_id': 123, 'contactable': True})

        expected_err = ('ulapd_api', 'USER_NOT_FOUND')
        expected_err_message = errors.get_message(*expected_err, filler='123')
        expected_err_code = errors.get_code(*expected_err)

        self.assertEqual(context.exception.message, expected_err_message)
        self.assertEqual(context.exception.code, expected_err_code)

    @patch('ulapd_api.services.user_service.UserDetails')
    @patch('ulapd_api.services.user_service.get_user_details')
    @patch('ulapd_api.services.user_service._create_api_key')
    def test_update_api_key(self, mock_api_key, mock_get_user, mock_user_details, *_):
        user = MagicMock()
        user.api_key = 'first-api-key'
        mock_user_details.get_user_details_by_id.return_value = user
        mock_api_key.return_value = 'second-api-key'
        mock_get_user.return_value = {'api_key': 'second-api-key'}
        result = service.update_api_key(123)
        self.assertEqual(result, {'api_key': 'second-api-key'})

    @patch('ulapd_api.services.user_service.UserDetails')
    def test_update_api_key_no_user(self, mock_user, *_):
        mock_user.get_user_details_by_id.return_value = None

        with self.assertRaises(ApplicationError) as context:
            service.update_api_key(123)

        expected_err = ('ulapd_api', 'RESET_API_KEY_ERROR')
        expected_err_message = errors.get_message(*expected_err, filler='User "123" not found')
        expected_err_code = errors.get_code(*expected_err)

        self.assertEqual(context.exception.message, expected_err_message)
        self.assertEqual(context.exception.code, expected_err_code)

    @patch('ulapd_api.services.user_service.UserDetails')
    @patch('ulapd_api.services.user_service.Dataset')
    @patch('ulapd_api.services.user_service.Licence')
    @patch('ulapd_api.services.user_service._extract_rows')
    @patch('ulapd_api.services.user_service.get_licence_agreement')
    @patch('ulapd_api.services.user_service._sort_out_sample')
    @patch('ulapd_api.services.user_service._sort_out_licenced_datasets')
    def test_get__users_dataset_access(self, mock_licenced_datasets, mock_sample, mock_get_licence, mock_extract,
                                       mock_licence, mock_dataset, mock_user, *_):
        mock_user.return_value = MagicMock()
        mock_dataset.get_all.return_value = helpers.generate_dataset_list()
        mock_licence.return_value = MagicMock()
        mock_extract.return_value = [{'licence_id': 'foo', 'title': 'bar'},
                                     {'licence_id': 'bar', 'title': 'foo'}]
        mock_get_licence.return_value = {'valid_licence': True}

        mock_sample.return_value = [{'id': '1', 'name': 'nps', 'title': 'nps_title', 'type': 'restricted',
                                     'licences': [{'title': 'nps licence title', 'agreed': True}]},
                                    {'id': '2', 'name': 'ccod', 'title': 'ccod_title', 'type': 'licenced',
                                     'licences': [{'title': 'ccod licence title', 'agreed': True}]}]

        mock_licenced_datasets.return_value = {'name': 'licenced', 'title': 'Free datasets',
                                               'licences': [{'ccod': {'agreed': True, 'title': 'ccod licence title'}}]}
        expected_result = [
            {'id': '1', 'name': 'nps', 'title': 'nps_title', 'type': 'restricted',
             'licences': [{'title': 'nps licence title', 'agreed': True}]},
            {'name': 'licenced', 'title': 'Free datasets',
             'licences': [{'ccod': {'agreed': True, 'title': 'ccod licence title'}}]}
        ]

        result = service.get_users_dataset_access(1)
        self.assertEqual(result, expected_result)

    @patch('ulapd_api.services.user_service.UserDetails')
    def test_get_users_dataset_access_no_user(self, mock_user, *_):
        mock_user.get_user_details_by_id.return_value = None

        with self.assertRaises(ApplicationError) as context:
            service.get_users_dataset_access(1)

        expected_err = ('ulapd_api', 'USER_NOT_FOUND')
        expected_err_message = errors.get_message(*expected_err, filler='1')
        expected_err_code = errors.get_code(*expected_err)

        self.assertEqual(context.exception.message, expected_err_message)
        self.assertEqual(context.exception.code, expected_err_code)

    def test_extract_rows_no_rows(self, *_):
        result = service._extract_rows([])
        self.assertEqual(result, [])

    def test_extract_rows(self, *_):
        mock_row = MagicMock()
        mock_row.as_dict.return_value = {'foo': 'bar'}
        result = service._extract_rows([mock_row, mock_row])
        self.assertEqual(result, [{'foo': 'bar'}, {'foo': 'bar'}])

    @patch('ulapd_api.services.user_service.Licence')
    def test_check_agreement_true(self, mock_licence, *_):
        date_agreed = datetime.strptime('2019-11-21 12:10:57.070764', '%Y-%m-%d %H:%M:%S.%f')
        licence_date = datetime.strptime('2019-09-09', '%Y-%m-%d')
        licence = MagicMock()
        licence.last_updated = licence_date.date()
        mock_licence.get_licence_by_licence_name.return_value = licence
        result = service._check_agreement('ccod', date_agreed)
        self.assertEqual(result, True)

    @patch('ulapd_api.services.user_service.Licence')
    def test_check_agreement_false(self, mock_licence, *_):
        date_agreed = datetime.strptime('2019-11-21 12:10:57.070764', '%Y-%m-%d %H:%M:%S.%f')
        licence_date = datetime.strptime('2019-11-22', '%Y-%m-%d')
        licence = MagicMock()
        licence.last_updated = licence_date.date()
        mock_licence.get_licence_by_licence_name.return_value = licence
        result = service._check_agreement('ccod', date_agreed)
        self.assertEqual(result, False)

    @patch('ulapd_api.services.user_service._create_api_key')
    @patch('ulapd_api.services.user_service._get_user_type_id')
    def test_process_new_user_data(self, mock_user_type, mock_api_key, *_):
        mock_api_key.return_value = '123-34-23d2-2dd2'
        mock_user_type.return_value = 3
        result = service._process_new_user_data({'user_id': 123,
                                                 'user_type': 'organisation-uk',
                                                 'contact_preferences': ['email', 'phone']})
        expected_result = {
            'user_id': 123,
            'user_type': 'organisation-uk',
            'api_key': '123-34-23d2-2dd2',
            'user_type_id': 3,
            'contact_preferences': ['email', 'phone'],
            'contactable': True
        }

        self.assertEqual(result, expected_result)

    @patch('ulapd_api.services.user_service._create_api_key')
    @patch('ulapd_api.services.user_service._get_user_type_id')
    def test_process_new_user_data_no_contact(self, mock_user_type, mock_api_key, *_):
        mock_api_key.return_value = '123-34-23d2-2dd2'
        mock_user_type.return_value = 3
        result = service._process_new_user_data({'user_id': 123,
                                                 'user_type': 'organisation-uk',
                                                 'contact_preferences': []})
        expected_result = {
            'user_id': 123,
            'user_type': 'organisation-uk',
            'api_key': '123-34-23d2-2dd2',
            'user_type_id': 3,
            'contact_preferences': [],
            'contactable': False
        }

        self.assertEqual(result, expected_result)

    @patch('ulapd_api.services.user_service._create_api_key')
    @patch('ulapd_api.services.user_service._get_user_type_id')
    def test_process_new_user_data_blank_values(self, mock_user_type, mock_api_key, *_):
        mock_api_key.return_value = '123-34-23d2-2dd2'
        mock_user_type.return_value = 3
        result = service._process_new_user_data({'user_id': 123,
                                                 'user_type': 'organisation-uk',
                                                 'contact_preferences': [],
                                                 'registration_no': ''})
        expected_result = {
            'user_id': 123,
            'user_type': 'organisation-uk',
            'api_key': '123-34-23d2-2dd2',
            'user_type_id': 3,
            'contact_preferences': [],
            'contactable': False,
            'registration_no': None
        }

        self.assertEqual(result, expected_result)

    @patch('ulapd_api.services.user_service.UserType')
    def test_get_user_type_by_type(self, mock_type, *_):
        user_type = MagicMock()
        user_type.as_dict.return_value = {'user_type_id': 3}
        mock_type.get_user_id_by_type.return_value = user_type
        result = service._get_user_type_id('organisation-uk')
        self.assertEqual(result, 3)

    def test_create_api_key(self, *_):
        result = service._create_api_key()
        assert isinstance(result, str)

    @patch('ulapd_api.services.user_service.Dataset')
    @patch('ulapd_api.services.user_service.get_licence_agreement')
    @patch('ulapd_api.services.user_service.UserTermsLink')
    @patch('ulapd_api.services.user_service._extract_rows')
    @patch('ulapd_api.services.user_service.Licence')
    def test_build_users_datasets(self, mock_licence, mock_extract, mock_user_terms,
                                  mock_get_licence, mock_dataset, *_):
        mock_dataset.get_dataset_by_name.return_value = helpers.generate_a_dataset()
        licence_data = MagicMock()
        licence_data.title = 'Licence Title'
        mock_licence.get_licence_by_licence_name.return_value = licence_data
        mock_user_terms.get_user_terms_by_user_id.return_value = MagicMock()
        mock_extract.return_value = [{'licence_id': 'ccod'}]

        licence = {'date_agreed': '2019-11-21 12:10:57.070764', 'valid_licence': True}
        mock_get_licence.return_value = licence

        result = service._build_users_datasets(123)
        expected_result = {
            'ccod': {
                'date_agreed': '2019-11-21 12:10:57.070764',
                'private': False,
                'valid_licence': True,
                'licence_type': 'licenced',
                'licences': ['Licence Title']
            }
        }
        self.assertEqual(result, expected_result)

    @patch('ulapd_api.services.user_service.Dataset')
    @patch('ulapd_api.services.user_service.get_licence_agreement')
    @patch('ulapd_api.services.user_service.UserTermsLink')
    @patch('ulapd_api.services.user_service._extract_rows')
    @patch('ulapd_api.services.user_service.Licence')
    @patch('ulapd_api.services.user_service.sorted')
    def test_build_users_datasets_freemium(self, mock_sorted, mock_licence, mock_extract, mock_user_terms,
                                           mock_get_licence, mock_dataset, *_):
        mock_dataset.get_dataset_by_name.return_value = helpers.generate_a_freemium_dataset()
        licence_data = MagicMock()
        licence_data.title = 'Licence Title'
        mock_licence.get_licence_by_licence_name.return_value = licence_data
        mock_user_terms.get_user_terms_by_user_id.return_value = MagicMock()
        mock_extract.return_value = [{'licence_id': 'res_cov_exploration'}, {'licence_id': 'res_cov_direct'}]
        mock_sorted.return_value = ['Direct Use', 'Exploration']

        licence = {
            'date_agreed': '2019-11-21 12:10:57.070764',
            'valid_licence': True
        }
        mock_get_licence.return_value = licence

        result = service._build_users_datasets(123)
        expected_result = {
            'res_cov': {
                'date_agreed': None,
                'private': True,
                'valid_licence': True,
                'licence_type': 'freemium',
                'licences': ['Direct Use', 'Exploration']
            }
        }
        self.assertEqual(result, expected_result)

    @patch('ulapd_api.services.user_service.delete_user')
    def test_delete_user_data(self, mock_delete, *_):
        account = MagicMock()
        account.delete = MagicMock()
        mock_delete.return_value = {'user_id': 123, 'message': 'user deleted'}
        service._delete_user_data(account, {'user_details_id': 123, 'ldap_id': 'an-ldap-id'})
        mock_delete.assert_called()

    @patch('ulapd_api.services.user_service.Dataset')
    @patch('ulapd_api.services.user_service._get_dataset_downloads')
    @patch('ulapd_api.services.user_service.get_licence_agreement')
    @patch('ulapd_api.services.user_service._extract_rows')
    @patch('ulapd_api.services.user_service.Licence')
    def test_build_user_dataset_activity(self, mock_licence, mock_extract, mock_get_licence,
                                         mock_download, mock_dataset, *_):
        mock_licence.return_value = MagicMock()
        mock_dataset.get_all.return_value = helpers.generate_dataset_list()
        mock_download.return_value = [{"date": "2019-11-22T09:28:58.610283", "file": "COU_file.zip"},
                                      {"date": "2019-11-21T12:10:27.550330", "file": "FULL_file.zip"}]
        licence = {
            'date_agreed': datetime.strptime('2019-11-21 12:10:57.070764', '%Y-%m-%d %H:%M:%S.%f'),
            'valid_licence': True
        }
        mock_get_licence.return_value = licence
        mock_extract.return_value = [{'licence_id': 'ccod'}]

        result = service._build_user_dataset_activity(123)
        expected_result = [
            {'id': 1,
             'name': 'nps',
             'private': True,
             'title': 'nps title',
             'licence_agreed': True,
             'download_history': [{'date': '2019-11-22T09:28:58.610283', 'file': 'COU_file.zip'},
                                  {'date': '2019-11-21T12:10:27.550330', 'file': 'FULL_file.zip'}],
             'licence_agreed_date': '2019-11-21T12:10:57.070764'},
            {'id': 2,
             'name': 'ccod',
             'private': False,
             'title': 'ccod title',
             'licence_agreed': True,
             'download_history': [{'date': '2019-11-22T09:28:58.610283', 'file': 'COU_file.zip'},
                                  {'date': '2019-11-21T12:10:27.550330', 'file': 'FULL_file.zip'}],
             'licence_agreed_date': '2019-11-21T12:10:57.070764'}]
        self.assertEqual(result, expected_result)

    @patch('ulapd_api.services.user_service.Dataset')
    @patch('ulapd_api.services.user_service._get_dataset_downloads')
    @patch('ulapd_api.services.user_service.get_licence_agreement')
    @patch('ulapd_api.services.user_service._extract_rows')
    @patch('ulapd_api.services.user_service.Licence')
    def test_build_user_dataset_activity_no_download(self, mock_licence, mock_extract, mock_get_licence, mock_download,
                                                     mock_dataset, *_):
        mock_licence.return_value = MagicMock()
        mock_extract.return_value = [{'licence_id': 'ccod'}]
        mock_dataset.get_all.return_value = helpers.generate_dataset_list()
        mock_download.return_value = []
        licence = {
            'date_agreed': datetime.strptime('2019-11-21 12:10:57.070764', '%Y-%m-%d %H:%M:%S.%f'),
            'valid_licence': True
        }
        mock_get_licence.return_value = licence
        result = service._build_user_dataset_activity(123)
        expected_result = [
            {'id': 1,
             'name': 'nps',
             'private': True,
             'title': 'nps title',
             'licence_agreed': True,
             'download_history': [],
             'licence_agreed_date': '2019-11-21T12:10:57.070764'},
            {'id': 2,
             'name': 'ccod',
             'private': False,
             'title': 'ccod title',
             'licence_agreed': True,
             'download_history': [],
             'licence_agreed_date': '2019-11-21T12:10:57.070764'}]
        self.assertEqual(result, expected_result)

    @patch('ulapd_api.services.user_service.Dataset')
    @patch('ulapd_api.services.user_service._get_dataset_downloads')
    @patch('ulapd_api.services.user_service.get_licence_agreement')
    @patch('ulapd_api.services.user_service._extract_rows')
    @patch('ulapd_api.services.user_service.Licence')
    def test_build_user_dataset_activity_no_licence_agreement(self, mock_licence, mock_extract, mock_get_licence,
                                                              mock_download, mock_dataset, *_):
        mock_licence.return_value = MagicMock()
        mock_extract.return_value = [{'licence_id': 'ccod'}]
        mock_dataset.get_all.return_value = helpers.generate_dataset_list()
        mock_download.return_value = []
        licence = {
            'date_agreed': datetime.strptime('2019-11-21 12:10:57.070764', '%Y-%m-%d %H:%M:%S.%f'),
            'valid_licence': False
        }
        mock_get_licence.return_value = licence
        result = service._build_user_dataset_activity(123)
        expected_result = [
            {'id': 1,
             'name': 'nps',
             'private': True,
             'title': 'nps title',
             'licence_agreed': False,
             'download_history': []},
            {'id': 2,
             'name': 'ccod',
             'private': False,
             'title': 'ccod title',
             'licence_agreed': False,
             'download_history': []}]
        self.assertEqual(result, expected_result)

    @patch('ulapd_api.services.user_service.Dataset')
    @patch('ulapd_api.services.user_service._get_dataset_downloads')
    @patch('ulapd_api.services.user_service.get_licence_agreement')
    @patch('ulapd_api.services.user_service._extract_rows')
    @patch('ulapd_api.services.user_service.Licence')
    def test_build_user_dataset_activity_freemium(self, mock_licence, mock_extract, mock_get_licence,
                                                  mock_download, mock_dataset, *_):
        mock_licence.return_value = MagicMock()
        mock_extract.return_value = [{'licence_id': 'res_cov_direct'}, {'licence_id': 'res_cov_exploration'},
                                     {'licence_id': 'res_cov_commercial'}]

        mock_dataset.get_all.return_value = [helpers.generate_a_freemium_dataset()]

        mock_download.return_value = []
        licence = {
            'date_agreed': datetime.strptime('2019-11-21 12:10:57.070764', '%Y-%m-%d %H:%M:%S.%f'),
            'valid_licence': True
        }
        mock_get_licence.return_value = licence
        result = service._build_user_dataset_activity(123)
        expected_result = [
            {'id': 3,
             'name': 'res_cov',
             'private': True,
             'title': 'Restrictive Covenants',
             'licence_agreed': True,
             'download_history': []}]
        self.assertEqual(result, expected_result)

    @patch('ulapd_api.services.user_service.Activity')
    def test_get_dataset_downloads(self, mock_activity, *_):
        a1 = MagicMock()
        a1.activity_type = 'download'
        a1.timestamp = datetime.strptime('2019-11-21 12:10:57.070764', '%Y-%m-%d %H:%M:%S.%f')
        a1.file = 'COU_file.zip'

        a2 = MagicMock()
        a2.activity_type = 'download'
        a2.timestamp = datetime.strptime('2019-11-21 12:10:58.070764', '%Y-%m-%d %H:%M:%S.%f')
        a2.file = 'FULL_file.zip'

        a3 = MagicMock()
        a3.activity_type = 'licence agreed'

        mock_activity.get_user_activity_by_dataset.return_value = [a1, a2, a3]
        result = service._get_dataset_downloads(123, 'ccod')
        expected_result = [{'date': '2019-11-21T12:10:57.070764', 'file': 'COU_file.zip'},
                           {'date': '2019-11-21T12:10:58.070764', 'file': 'FULL_file.zip'}]
        self.assertEqual(result, expected_result)

    def test_build_contact_preferences(self, *_):
        data = [
            {
                'contact_id': 1,
                'contact_type': 'email'
            },
            {
                'contact_id': 2,
                'contact_type': 'phone'
            }
        ]
        result = service._build_contact_preferences(data)
        self.assertEqual(result, ['email', 'phone'])

    def test_build_contact_preferences_no_data(self, *_):
        data = []
        result = service._build_contact_preferences(data)
        self.assertEqual(result, [])

    def test_sort_out_sample(self, *_):
        result = service._sort_out_sample(data_access_data.data_access)
        self.assertEqual(result, data_access_data.sample_result)
        datasets = []
        for row in result:
            datasets.append(row['name'])
        self.assertTrue('nps_sample' not in datasets)

    def test_sort_out_licenced_datasets(self, *_):
        result = service._sort_out_licenced_datasets(data_access_data.licenced_data)
        self.assertEqual(result, data_access_data.licenced_result)

    @patch('ulapd_api.services.user_service.AccountAPI.handle_role')
    def test_handle_ldap_group(self, mock_account, *_):
        mock_account.return_value = MagicMock()
        expected_call = {
            'ldap_id': '123-333',
            'groups': {
                'dad': True
            }
        }
        with app.app_context():
            service._handle_ldap_group('dad', '123-333', True)
        mock_account.assert_called_with(expected_call)

    @patch('ulapd_api.services.user_service.Dataset')
    def test_check_freemium_true(self, mock_dataset, *_):
        dataset = MagicMock()
        dataset.type = 'freemium'
        mock_dataset.get_dataset_by_name.return_value = dataset
        result = service._check_freemium('res_cov')
        self.assertEqual(result, True)

    @patch('ulapd_api.services.user_service.Dataset')
    def test_check_freemium_false(self, mock_dataset, *_):
        dataset = MagicMock()
        dataset.type = 'licenced'
        mock_dataset.get_dataset_by_name.return_value = dataset
        result = service._check_freemium('ocod')
        self.assertEqual(result, False)

    def test_order_freemium_licences(self, *_):
        result = service._order_freemium_licences('Direct Use')
        self.assertEqual(result, 0)

    # scenario one - freemium set to agreed and user doesn't currently have the role
    def test_handle_ldap_freemium_updates_scenario_one(self, *_):
        freemium_type = 'res_cov'
        freemium_list = [{'licence_id': 'res_cov_direct', 'agreed': False},
                         {'licence_id': 'res_cov_commercial', 'agreed': True},
                         {'licence_id': 'res_cov_exploration', 'agreed': False}]
        groups = {'res_cov': True}
        current_list = ['ccod']
        result = service._handle_ldap_freemium_updates(freemium_type, freemium_list, groups, current_list)
        # result should be the res_cov role still in groups
        self.assertEqual(result, groups)

    # scenario two - freemium set to agreed and user already has the role
    def test_handle_ldap_freemium_updates_scenario_two(self, *_):
        freemium_type = 'res_cov'
        freemium_list = [{'licence_id': 'res_cov_direct', 'agreed': False},
                         {'licence_id': 'res_cov_commercial', 'agreed': True},
                         {'licence_id': 'res_cov_exploration', 'agreed': False}]
        groups = {'res_cov': True}
        current_list = ['ccod', 'res_cov_direct']
        result = service._handle_ldap_freemium_updates(freemium_type, freemium_list, groups, current_list)
        # result should be the res_cov role is removed from groups as role already exists in ldap
        self.assertEqual(result, {})

    # scenario three - freemium set to not agreed and user currently has the role
    def test_handle_ldap_freemium_updates_scenario_three(self, *_):
        freemium_type = 'res_cov'
        freemium_list = [{'licence_id': 'res_cov_direct', 'agreed': False},
                         {'licence_id': 'res_cov_commercial', 'agreed': False},
                         {'licence_id': 'res_cov_exploration', 'agreed': False}]
        groups = {}
        current_list = ['ccod', 'res_cov_direct']
        result = service._handle_ldap_freemium_updates(freemium_type, freemium_list, groups, current_list)
        # result should be the res_cov role is still in groups set to False
        self.assertEqual(result, {'res_cov': False})
