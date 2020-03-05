from flask import current_app, g
from ulapd_api.app import app
from ulapd_api.exceptions import ApplicationError
from common_utilities import errors
import requests


class AccountAPI(object):
    """Encapsulating class for Account API integration."""
    def __init__(self):
        self.url = current_app.config["ACCOUNT_API_URL"]
        self.version = current_app.config["ACCOUNT_API_VERSION"]
        self.timeout = current_app.config["DEFAULT_TIMEOUT"]

    def get(self, ldap_id):
        url = '{0}/{1}/users?id={2}'.format(self.url, self.version, ldap_id)
        headers = {
            "Accept": "application/json"
        }
        try:
            response = g.requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            current_app.logger.error('Encountered non 2xx http code from account_api for retrieving user details')
            raise ApplicationError(*errors.get("ulapd_api", "ACCOUNT_API_HTTP_ERROR", filler=str(error)))
        except requests.exceptions.ConnectionError as error:
            current_app.logger.error('Encountered an error connecting to account_api for retrieving user details')
            raise ApplicationError(*errors.get("ulapd_api", "ACCOUNT_API_CONN_ERROR", filler=str(error)))
        except requests.exceptions.Timeout as error:
            current_app.logger.error('Encountered a timeout when writing to account_api for retrieving user details')
            raise ApplicationError(*errors.get("ulapd_api", "ACCOUNT_API_TIMEOUT", filler=str(error)))
        else:
            return response.json()

    def create(self, data):
        """Activate user."""
        url = '{0}/{1}/users'.format(self.url, self.version)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = _create_user_data(data)

        try:
            response = g.requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            current_app.logger.error('Encountered non 2xx http code from account_api for user activation')
            raise ApplicationError(*errors.get("ulapd_api", "ACCOUNT_API_HTTP_ERROR", filler=str(error)))
        except requests.exceptions.ConnectionError as error:
            current_app.logger.error('Encountered an error connecting to account_api for user activation')
            raise ApplicationError(*errors.get("ulapd_api", "ACCOUNT_API_CONN_ERROR", filler=str(error)))
        except requests.exceptions.Timeout as error:
            current_app.logger.error('Encountered a timeout when writing to account_api for user activation')
            raise ApplicationError(*errors.get("ulapd_api", "ACCOUNT_API_TIMEOUT", filler=str(error)))
        else:
            app.logger.info("Created user {}".format(payload['email']))
            return response.json()

    def delete(self, ldap_id):
        """delete user."""
        url = '{0}/{1}/users/{2}'.format(self.url, self.version, ldap_id)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            response = g.requests.delete(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            current_app.logger.error('Encountered non 2xx http code from account_api for user delete')
            raise ApplicationError(*errors.get("ulapd_api", "ACCOUNT_API_HTTP_ERROR", filler=str(error)))
        except requests.exceptions.ConnectionError as error:
            current_app.logger.error('Encountered an error connecting to account_api for user delete')
            raise ApplicationError(*errors.get("ulapd_api", "ACCOUNT_API_CONN_ERROR", filler=str(error)))
        except requests.exceptions.Timeout as error:
            current_app.logger.error('Encountered a timeout when writing to account_api for user delete')
            raise ApplicationError(*errors.get("ulapd_api", "ACCOUNT_API_TIMEOUT", filler=str(error)))
        else:
            app.logger.info("Deleted user {}".format(ldap_id))
            return {'message': 'deleted'}

    def activate(self, ldap_id):
        """Activate user."""
        url = '{0}/{1}/users/{2}/activate'.format(self.url, self.version, ldap_id)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            response = g.requests.post(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            current_app.logger.error('Encountered non 2xx http code from account_api for user activation')
            raise ApplicationError(*errors.get("ulapd_api", "ACCOUNT_API_HTTP_ERROR", filler=str(error)))
        except requests.exceptions.ConnectionError as error:
            current_app.logger.error('Encountered an error connecting to account_api for user activation')
            raise ApplicationError(*errors.get("ulapd_api", "ACCOUNT_API_CONN_ERROR", filler=str(error)))
        except requests.exceptions.Timeout as error:
            current_app.logger.error('Encountered a timeout when writing to account_api for user activation')
            raise ApplicationError(*errors.get("ulapd_api", "ACCOUNT_API_TIMEOUT", filler=str(error)))
        else:
            app.logger.info("Activated user {}".format(ldap_id))
            return {'message': 'activated'}

    def acknowledge(self, ldap_id):
        """Acknowledge user."""
        url = '{0}/{1}/users/{2}/acknowledge'.format(self.url, self.version, ldap_id)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            response = g.requests.post(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            current_app.logger.error('Encountered non 2xx http code from account_api for user acknowledgement')
            raise ApplicationError(*errors.get("ulapd_api", "ACCOUNT_API_HTTP_ERROR", filler=str(error)))
        except requests.exceptions.ConnectionError as error:
            current_app.logger.error('Encountered an error connecting to account_api for user acknowledgement')
            raise ApplicationError(*errors.get("ulapd_api", "ACCOUNT_API_CONN_ERROR", filler=str(error)))
        except requests.exceptions.Timeout as error:
            current_app.logger.error('Encountered a timeout when writing to account_api for user acknowledgement')
            raise ApplicationError(*errors.get("ulapd_api", "ACCOUNT_API_TIMEOUT", filler=str(error)))
        else:
            app.logger.info("Acknowledged user {}".format(ldap_id))
            return {'message': 'acknowledged'}

    def handle_role(self, data):
        """Add or remove role for user."""
        url = '{0}/{1}/users/handle_role'.format(self.url, self.version)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            response = g.requests.post(url, json=data, headers=headers, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            current_app.logger.error('Encountered non 2xx http code from account_api for adding a role')
            raise ApplicationError(*errors.get("ulapd_api", "ACCOUNT_API_HTTP_ERROR", filler=str(error)))
        except requests.exceptions.ConnectionError as error:
            current_app.logger.error('Encountered an error connecting to account_api for adding a role')
            raise ApplicationError(*errors.get("ulapd_api", "ACCOUNT_API_CONN_ERROR", filler=str(error)))
        except requests.exceptions.Timeout as error:
            current_app.logger.error('Encountered a timeout when writing to account_api adding a role')
            raise ApplicationError(*errors.get("ulapd_api", "ACCOUNT_API_TIMEOUT", filler=str(error)))
        else:
            app.logger.info("Added role for user {}".format(data['ldap_id']))
            return {'message': 'success'}

    def update_groups(self, ldap_id, groups):
        """Update users account"""
        url = '{0}/{1}/users/update_groups'.format(self.url, self.version)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        data = {
            'ldap_id': ldap_id,
            'groups': groups
        }
        try:
            response = g.requests.patch(url, json=data, headers=headers, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            current_app.logger.error('Encountered non 2xx http code from account_api for updating groups')
            raise ApplicationError(*errors.get("ulapd_api", "ACCOUNT_API_HTTP_ERROR", filler=str(error)))
        except requests.exceptions.ConnectionError as error:
            current_app.logger.error('Encountered an error connecting to account_api for updating group')
            raise ApplicationError(*errors.get("ulapd_api", "ACCOUNT_API_CONN_ERROR", filler=str(error)))
        except requests.exceptions.Timeout as error:
            current_app.logger.error('Encountered a timeout when writing to account_api for updating group')
            raise ApplicationError(*errors.get("ulapd_api", "ACCOUNT_API_TIMEOUT", filler=str(error)))
        else:
            app.logger.info("groups updated for user {}".format(ldap_id))
            return {'message': 'groups updated'}


def _create_user_data(data):
    org_name = None

    if data['user_type'] == 'organisation-uk':
        user_type = 'uk-organisation'
        org_name = data['organisation_name']
    elif data['user_type'] == 'organisation-overseas':
        user_type = 'overseas-organisation'
        org_name = data['organisation_name']
    else:
        user_type = 'personal'

    account_data = {
        'user_type': user_type,
        'email': data['email'],
        'first_name': data['first_name'],
        'surname': data['last_name']
    }

    if org_name:
        account_data['org_name'] = org_name

    return account_data


def update_groups_for_ldap(ldap_id, groups):
    try:
        account = AccountAPI()
        update_groups_retry = current_app.config["UPDATE_GROUPS_RETRY"]
        for attempts in range(int(update_groups_retry)):
            try:
                app.logger.info('Attempt {} to call account-api'.format(attempts))
                account.update_groups(ldap_id, groups)
                app.logger.info('Call to account-api to update groups successful')
                break
            except Exception as e:
                app.logger.error('Call to account-api failed on attempt {} with error {}'.format(attempts, e))
    except ApplicationError as error:
        app.logger.error('Ulapd-api failed calling account-api'
                         ' with error: {}'.format(str(error)))
