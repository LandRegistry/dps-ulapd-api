from flask import current_app, g
from ulapd_api.app import app
from ulapd_api.exceptions import ApplicationError
from common_utilities import errors
import requests


class VerificationAPI(object):
    """Encapsulating class for Verification API integration."""
    def __init__(self):
        self.url = current_app.config["VERIFICATION_API_URL"]
        self.version = current_app.config["VERIFICATION_API_VERSION"]
        self.timeout = current_app.config["DEFAULT_TIMEOUT"]

    def create(self, data):
        url = '{0}/{1}/case'.format(self.url, self.version)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = _create_user_data(data)

        try:
            response = g.requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            current_app.logger.error('Encountered non 2xx http code from verification_api creating user')
            raise ApplicationError(*errors.get("ulapd_api", "VERIFICATION_API_HTTP_ERROR", filler=str(error)))
        except requests.exceptions.ConnectionError as error:
            current_app.logger.error('Encountered an error connecting to verification_api creating user')
            raise ApplicationError(*errors.get("ulapd_api", "VERIFICATION_API_CONN_ERROR", filler=str(error)))
        except requests.exceptions.Timeout as error:
            current_app.logger.error('Encountered a timeout when writing to verification_api creating user')
            raise ApplicationError(*errors.get("ulapd_api", "VERIFICATION_API_TIMEOUT", filler=str(error)))
        else:
            app.logger.info("Created user_details_id {}".format(payload['user_id']))
            return response.json()


def _create_user_data(data):
    data_copy = data.copy()
    payload = {
        'user_id': str(data_copy['user_details_id']),
        'ldap_id': data_copy['ldap_id'],
        'status': 'Pending'
    }

    if data_copy['user_type'] not in ['organisation-uk']:
        payload['status'] = 'Approved'

    for key in ['user_id', 'ldap_id', 'user_type_id', 'user_details_id']:
        data_copy.pop(key, None)

    payload['registration_data'] = data_copy
    return payload
