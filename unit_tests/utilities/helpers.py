from unittest.mock import MagicMock
from datetime import datetime

user_dict = {
    'user_details_id': 123,
    'user_type_id': 1,
    'ldap_id': 'an-ldap-id',
    'api_key': 'an-api-key',
    'email': 'test@email.com',
    'title': 'Mr',
    'first_name': 'Test',
    'last_name': 'Tester',
    'contactable': True,
    'telephone_number': '09909090909090',
    'address_line_1': '1',
    'address_line_2': 'New Street',
    'city': 'Faketown',
    'county': None,
    'postcode': 'AA1 1AA',
    'country': 'UK',
    'country_of_incorporation': None,
    'organisation_name': None,
    'organisation_type': None,
    'registration_number': None,
    'date_added': str(datetime.now())
}


def generate_test_user():
    test_user = MagicMock()
    test_user.user_details_id = 123
    test_user.user_type_id = 1
    test_user.ldap_id = 'an-ldap-id'
    test_user.api_key = 'an-api-key'
    test_user.email = 'test@email.com'
    test_user.title = 'Mr'
    test_user.first_name = 'Test'
    test_user.last_name = 'Tester'
    test_user.contactable = True
    test_user.telephone_number = '09909090909090'
    test_user.address_line_1 = '1'
    test_user.address_line_2 = 'New Street'
    test_user.city = 'Faketown'
    test_user.county = None
    test_user.postcode = 'AA1 1AA'
    test_user.country = 'UK'
    test_user.country_of_incorporation = None
    test_user.organisation_name = None
    test_user.organisation_type = None
    test_user.registration_number = None
    test_user.date_added = datetime.now()
    test_user.as_dict.return_value = user_dict

    return test_user


def generate_dataset_list():
    nps = MagicMock()
    nps.private = True
    nps.name = 'nps'
    nps.licence_id = 'nps'
    nps.dataset_id = 1
    nps.title = 'nps title'
    nps.type = 'restricted'

    ccod = MagicMock()
    ccod.private = False
    ccod.name = 'ccod'
    ccod.licence_id = 'ccod'
    ccod.dataset_id = 2
    ccod.title = 'ccod title'
    ccod.type = 'licenced'

    return [nps, ccod]


def generate_a_dataset():
    ccod = MagicMock()
    ccod.private = False
    ccod.name = 'ccod'
    ccod.licence_id = 'ccod'
    ccod.dataset_id = 2
    ccod.title = 'ccod title'
    ccod.type = 'licenced'

    return ccod


def generate_a_freemium_dataset():
    res_cov = MagicMock()
    res_cov.private = True
    res_cov.name = 'res_cov'
    res_cov.licence_id = 'res_cov'
    res_cov.dataset_id = 3
    res_cov.title = 'Restrictive Covenants'
    res_cov.type = 'freemium'

    return res_cov
