import uuid
from datetime import datetime
from common_utilities import errors
from ulapd_api.app import app
from ulapd_api.exceptions import ApplicationError
from ulapd_api.extensions import db
from ulapd_api.models.user_details import UserDetails
from ulapd_api.models.user_type import UserType
from ulapd_api.models.licence import Licence
from ulapd_api.models.user_terms_link import UserTermsLink
from ulapd_api.models.dataset import Dataset
from ulapd_api.models.activity import Activity
from ulapd_api.models.contact import Contact
from ulapd_api.utilities.decorators import handle_errors
from ulapd_api.dependencies.account_api import AccountAPI, update_groups_for_ldap
from ulapd_api.dependencies.verification_api import VerificationAPI


@handle_errors(is_get=True)
def get_all_users():
    users = _extract_rows(UserDetails.get_user_details_all())
    user_list = []
    for user in users:
        user_type = get_user_type(user['user_type_id'])
        user_dict = {
            'user_details': user,
            'user_type': user_type
        }
        user_list.append(user_dict)

    return user_list


@handle_errors(is_get=True)
def get_user_by_key(user_data):
    if user_data['key'] == 'user_details_id':
        user = UserDetails.get_user_details_by_id(user_data['value'])
    elif user_data['key'] == 'email':
        user = UserDetails.get_user_details_by_email(user_data['value'])
    elif user_data['key'] == 'api_key':
        user = UserDetails.get_user_details_by_api_key(user_data['value'])
    elif user_data['key'] == 'ldap_id':
        user = UserDetails.get_user_details_by_ldap_id(user_data['value'])
    else:
        raise ApplicationError('Incorrect key: {}'.format(user_data['key']), 'E101', http_code=404)

    if user:
        user_details = user.as_dict()
        user_type = get_user_type(user_details['user_type_id'])
        user_details['user_type'] = user_type
        contact_preferences = _build_contact_preferences(
            _extract_rows(Contact.get_contact_preferences_for_user(user_details['user_details_id'])))
        user_details['contact_preferences'] = contact_preferences
        user_dict = {
            'user_details': user_details,
            'datasets': _build_users_datasets(user_details['user_details_id'])
        }
        return user_dict
    else:
        raise ApplicationError(*errors.get('ulapd_api', 'USER_NOT_FOUND', filler=user_data['value']), http_code=404)


@handle_errors(is_get=True)
def get_user_details(user_id):
    user_details = UserDetails.get_user_details_by_id(user_id)
    if user_details:
        result = user_details.as_dict()
    else:
        app.logger.error("User '{}' not found".format(user_id))
        raise ApplicationError(*errors.get('ulapd_api', 'USER_NOT_FOUND', filler=user_id), http_code=404)

    return result


@handle_errors(is_get=True)
def get_user_type(type_id):
    user_type = UserType.get_user_type_by_id(type_id)
    if user_type:
        result = user_type.as_dict()
    else:
        app.logger.error("User type '{}' not found".format(type_id))
        raise ApplicationError(*errors.get('ulapd_api', 'USER_TYPE_NOT_FOUND', filler=type_id), http_code=404)

    return result


@handle_errors(is_get=True)
def get_user_licences(user_id):
    return _extract_rows(UserTermsLink.get_user_terms_by_user_id(user_id))


@handle_errors(is_get=True)
def get_licence_agreement(user_id, licence_name):
    result = {
        'user_id': user_id,
        'licence': licence_name,
        'valid_licence': False,
        'date_agreed': None
    }

    licence = UserTermsLink.get_user_terms_by_licence_name(user_id, licence_name)
    if licence:
        result['valid_licence'] = _check_agreement(licence_name, licence.date_agreed)
        result['date_agreed'] = licence.date_agreed
    return result


@handle_errors(is_get=False)
def manage_licence_agreement(data):
    try:
        user = UserDetails.get_user_details_by_id(data['user_details_id'])
        if not user:
            app.logger.error("No user found for id {}".format(data['user_details_id']))
            raise ApplicationError(*errors.get('ulapd_api', 'USER_NOT_FOUND',
                                               filler=data['user_details_id']), http_code=404)

        # check to see if user already has this type of licence
        ldap_update_needed = True
        licence_data = _extract_rows(Licence.get_licences_by_dataset_name(data['licence_id']))
        for rows in licence_data:
            user_licence = UserTermsLink.get_user_terms_by_licence_name(user.user_details_id, rows['licence_id'])
            if user_licence:
                app.logger.info('User {} already has the role {} so not updating ldap...'.format(user.user_details_id,
                                                                                                 data['licence_id']))
                ldap_update_needed = False

        stored_licence_id = data['licence_id']
        if _check_freemium(data['licence_id']):
            data['licence_id'] += '_direct'
        licence = UserTermsLink(data)
        db.session.add(licence)

        if ldap_update_needed:
            app.logger.info('User {} does not have the role {} so update ldap...'.format(user.user_details_id,
                                                                                         stored_licence_id))
            _handle_ldap_group(stored_licence_id, user.ldap_id, True)

        db.session.commit()
        data['link_id'] = licence.user_terms_link_id
        return data
    except Exception as e:
        app.logger.error('Failed to manage licence for user {} with error - {}'.format(data['user_details_id'],
                                                                                       str(e)))
        db.session.rollback()
        db.session.close()
        raise ApplicationError(*errors.get('ulapd_api', 'LICENCE_AGREE_ERROR', filler=e), http_code=400)


@handle_errors(is_get=False)
def manage_multi_licence_agreement(data):
    try:
        user = UserDetails.get_user_details_by_id(data['user_details_id'])
        if not user:
            app.logger.error("No user found for id {}".format(data['user_details_id']))
            raise ApplicationError(*errors.get('ulapd_api', 'USER_NOT_FOUND',
                                               filler=data['user_details_id']), http_code=404)

        current_licences = _extract_rows(UserTermsLink.get_user_terms_by_user_id(data['user_details_id']))
        current_list = [d['licence_id'] for d in current_licences]

        all_licences = Licence.get_all_licences()
        licence_dict = {}
        for rows in all_licences:
            licence_dict[rows.licence_name] = rows.dataset_name

        groups = {}
        for row in data['licences']:
            if row['licence_id'] not in current_list and row['agreed']:
                app.logger.info('Adding licence {} to db and ldap'.format(row['licence_id']))
                role = licence_dict[row['licence_id']]
                groups[role] = row['agreed']
                new_user_licence = UserTermsLink({'user_details_id': user.user_details_id,
                                                  'licence_id': row['licence_id']})
                db.session.add(new_user_licence)
            elif row['licence_id'] in current_list and not row['agreed']:
                app.logger.info('Removing licence {} from db and ldap'.format(row['licence_id']))
                role = licence_dict[row['licence_id']]
                groups[role] = row['agreed']
                UserTermsLink.delete_user_licence_agreement(user.user_details_id, row['licence_id'])
            else:
                app.logger.info('There is no change for licence {}'.format(row['licence_id']))

        # sort out freemium
        res_covs = [d for d in data['licences'] if 'res_cov' in d['licence_id']]
        groups = _handle_ldap_freemium_updates('res_cov', res_covs, groups, current_list)

        if bool(groups):
            app.logger.info('Sending these groups - {}, for ldap update for user {}'.format(groups,
                                                                                            user.user_details_id))
            update_groups_for_ldap(user.ldap_id, groups)
        else:
            app.logger.info('No groups to update in ldap for user {}'.format(user.user_details_id))

        db.session.commit()
        return groups
    except Exception as e:
        app.logger.error('Failed to manage multi licences for user {} with error - {}'.format(data['user_details_id'],
                                                                                              str(e)))
        db.session.rollback()
        db.session.close()
        raise ApplicationError(*errors.get('ulapd_api', 'LICENCE_AGREE_ERROR', filler=e), http_code=400)


@handle_errors(is_get=True)
def get_dataset_activity(user_id):
    user = UserDetails.get_user_details_by_id(user_id)
    if user:
        return _build_user_dataset_activity(user_id)
    else:
        app.logger.error("No user found for id {}".format(user_id))
        raise ApplicationError(*errors.get('ulapd_api', 'USER_NOT_FOUND', filler=user_id), http_code=404)


@handle_errors(is_get=False)
def create_new_user(user_data):
    try:
        account = AccountAPI()
        verification = VerificationAPI()
        app.logger.info('Creating user in ldap for {}'.format(user_data['email']))
        response = account.create(user_data)
        user_data['ldap_id'] = response['user_id']

        user_data = _process_new_user_data(user_data)
        app.logger.info('Adding user {} to the ulapd database...'.format(user_data['email']))
        new_user_details = UserDetails(user_data)
        db.session.add(new_user_details)
        db.session.commit()
        user_data['user_details_id'] = new_user_details.user_details_id

        if user_data['contactable']:
            app.logger.info('Inserting the contact preferences for {}...'.format(user_data['email']))
            for preference in user_data['contact_preferences']:
                contact = {
                    'user_details_id': user_data['user_details_id'],
                    'contact_type': preference
                }
                contact_preference = Contact(contact)
                db.session.add(contact_preference)
        db.session.commit()
        app.logger.info('Finished adding user {} to the ulapd database...'.format(user_data['email']))

        # Add the user details to verification database for DST
        app.logger.info('Adding user {} to verification db...'.format(user_data['email']))
        verification.create(user_data)

        # Call to account-api to activate or acknowledge user
        is_uk_org = 'organisation-uk' in user_data['user_type']

        if is_uk_org:
            app.logger.info('Acknowledging user')
            account.acknowledge(user_data['ldap_id'])
        else:
            app.logger.info('Activating user')
            account.activate(user_data['ldap_id'])

        db.session.close()
        return user_data
    except Exception as e:
        app.logger.error('Failed to create user with error - {}'.format(str(e)))
        db.session.rollback()
        _delete_user_data(account, user_data)
        db.session.close()
        raise ApplicationError(*errors.get('ulapd_api', 'CREATE_USER_ERROR', filler=e), http_code=400)


@handle_errors(is_get=False)
def delete_user(user_id):
    try:
        UserTermsLink.delete_user_by_user_id(user_id)
        Activity.delete_user_by_user_id(user_id)
        Contact.delete_contact_preferences_for_user(user_id)

        user = UserDetails.get_user_details_by_id(user_id)
        if user:
            db.session.delete(user)
        else:
            app.logger.error("No user: {} found for deletion".format(user_id))
            db.session.rollback()
            db.session.close()
            raise ApplicationError(*errors.get('ulapd_api', 'USER_NOT_FOUND', filler=user_id), http_code=404)
        db.session.commit()
        return {'user_id': user_id, 'message': 'user deleted'}
    except Exception as e:
        db.session.rollback()
        db.session.close()
        raise ApplicationError(*errors.get('ulapd_api', 'DELETE_USER_ERROR', filler=e), http_code=400)


@handle_errors(is_get=False)
def update_contact_preference(user_data):
    user = UserDetails.get_user_details_by_id(user_data['user_id'])
    if user:
        app.logger.info('Deleting contact preferences for user {}'.format(user_data['user_id']))

        Contact.delete_contact_preferences_for_user(user_data['user_id'])
        for contacts in user_data['contact_preferences']:
            contact = {
                'user_details_id': user_data['user_id'],
                'contact_type': contacts
            }
            contact_preference = Contact(contact)
            db.session.add(contact_preference)

        user.contactable = user_data['contactable']
        db.session.commit()
        user_details = user.as_dict()
        user_details['contact_preferences'] = user_data['contact_preferences']
        return user_details
    else:
        raise ApplicationError(*errors.get('ulapd_api', 'USER_NOT_FOUND', user_data['user_id']), http_code=404)


@handle_errors(is_get=False)
def update_api_key(user_id):
    try:
        user = UserDetails.get_user_details_by_id(user_id)
        if user:
            user.api_key = _create_api_key()
            db.session.commit()
            return get_user_details(user_id)
        else:
            raise ApplicationError(*errors.get('ulapd_api', 'USER_NOT_FOUND', filler=user_id), http_code=404)

    except Exception as e:
        raise ApplicationError(*errors.get('ulapd_api', 'RESET_API_KEY_ERROR', filler=e), http_code=400)


@handle_errors(is_get=True)
def get_users_dataset_access(user_id):
    user = UserDetails.get_user_details_by_id(user_id)
    if user:
        datasets = Dataset.get_all()
        dataset_access = []

        for row in datasets:
            if row.type != 'open':
                dataset_dict = {
                    'id': row.dataset_id,
                    'name': row.name,
                    'title': row.title,
                    'type': row.type
                }
                licence_names = _extract_rows(Licence.get_licences_by_dataset_name(row.name))

                licence_dict = {}
                for licence_rows in licence_names:
                    licence = get_licence_agreement(user_id, licence_rows['licence_id'])
                    licence_dict[licence_rows['licence_id']] = {
                        'title': licence_rows['title'],
                        'agreed': licence['valid_licence']
                    }

                dataset_dict['licences'] = licence_dict
                dataset_access.append(dataset_dict)

        dataset_access = _sort_out_sample(dataset_access)

        licenced_datasets = [d for d in dataset_access if d['type'] == 'licenced']
        non_licenced_datasets = [d for d in dataset_access if d['type'] != 'licenced']

        full_access = non_licenced_datasets
        full_access.append(_sort_out_licenced_datasets(licenced_datasets))
        return full_access
    else:
        app.logger.error("No user found for id {}".format(user_id))
        raise ApplicationError(*errors.get('ulapd_api', 'USER_NOT_FOUND', filler=user_id), http_code=404)


def _extract_rows(rows):
    return [row.as_dict() for row in rows]


def _check_agreement(licence_name, date_agreed):
    converted_date = date_agreed.date()
    agreed = False
    licence = Licence.get_licence_by_licence_name(licence_name)
    if licence and licence.last_updated <= converted_date:
        agreed = True
    return agreed


def _process_new_user_data(user_data):
    user_data['api_key'] = _create_api_key()
    user_data['user_type_id'] = _get_user_type_id(user_data['user_type'])
    for key, value in user_data.items():
        if value == '':
            user_data[key] = None

    if user_data['contact_preferences'] is not None and len(user_data['contact_preferences']) > 0:
        user_data['contactable'] = True
    else:
        user_data['contactable'] = False
    return user_data


def _get_user_type_id(user_type):
    user_type_data = UserType.get_user_id_by_type(user_type)
    user_type_dict = user_type_data.as_dict()
    return user_type_dict['user_type_id']


def _create_api_key():
    return str(uuid.uuid4())


def _build_users_datasets(user_id):
    user_licences = _extract_rows(UserTermsLink.get_user_terms_by_user_id(user_id))
    dataset_access = {}
    for rows in user_licences:
        licence = get_licence_agreement(user_id, rows['licence_id'])
        if licence['valid_licence']:
            licence_data = Licence.get_licence_by_licence_name(rows['licence_id'])
            dataset_data = Dataset.get_dataset_by_name(licence_data.dataset_name)
            if dataset_data.name in dataset_access:
                dataset_access[dataset_data.name]['licences'].append(licence_data.title)
                dataset_access[dataset_data.name]['date_agreed'] = None
            else:
                dataset_access[dataset_data.name] = {'date_agreed': str(licence['date_agreed']),
                                                     'private': dataset_data.private,
                                                     'valid_licence': licence['valid_licence'],
                                                     'licence_type': dataset_data.type,
                                                     'licences': [licence_data.title]}

    # Need to sort freemium licences into their correct order
    for key, value in dataset_access.items():
        if value['licence_type'] == 'freemium':
            value['licences'] = sorted(value['licences'], key=_order_freemium_licences)
    return dataset_access


def _delete_user_data(account, data):
    account.delete(data['ldap_id'])
    delete_user(data['user_details_id'])
    return


def _build_user_dataset_activity(user_id):
    dataset = Dataset.get_all()
    dataset_activity = []
    for row in dataset:
        dataset_dict = {
            'id': row.dataset_id,
            'name': row.name,
            'private': row.private,
            'title': row.title,
            'licence_agreed': False,
            'download_history': _get_dataset_downloads(user_id, row.name)
        }

        licence_names = _extract_rows(Licence.get_licences_by_dataset_name(row.name))

        if len(licence_names) > 1:
            for licence in licence_names:
                this_licence = get_licence_agreement(user_id, licence['licence_id'])
                if this_licence['valid_licence']:
                    dataset_dict['licence_agreed'] = True
                    break
        else:
            licence = get_licence_agreement(user_id, row.licence_name)
            if licence['valid_licence']:
                dataset_dict['licence_agreed'] = True
                converted_date = datetime.strftime(licence['date_agreed'], '%Y-%m-%dT%H:%M:%S.%f')
                dataset_dict['licence_agreed_date'] = str(converted_date)
        dataset_activity.append(dataset_dict)
    return dataset_activity


def _get_dataset_downloads(user_id, name):
    activities = Activity.get_user_activity_by_dataset(user_id, name)
    downloads = []
    for download in activities:
        if download.activity_type == 'download':
            converted_date = datetime.strftime(download.timestamp, '%Y-%m-%dT%H:%M:%S.%f')
            download_dict = {
                'date': str(converted_date),
                'file': download.file
            }
            downloads.append(download_dict)

    return downloads


def _build_contact_preferences(contact_preferences):
    return [row['contact_type'] for row in contact_preferences]


def _sort_out_sample(dataset_access):
    # for showing dataset access add sample licence info to parent and remove from the list
    for rows in dataset_access:
        if rows['name'][-7:] == '_sample':
            main_dataset = rows['name'][:-7]
            index = next((index for (index, d) in enumerate(dataset_access) if d["name"] == main_dataset), None)
            sample_licence = rows['licences'][rows['name']]
            dataset_access[index]['licences'][main_dataset]['title'] = 'Full dataset'
            sample_licence['title'] = 'Sample'
            dataset_access[index]['licences'][rows['name']] = sample_licence

    return [d for d in dataset_access if d['name'][-7:] != '_sample']


def _sort_out_licenced_datasets(licenced_datasets):
    # for showing dataset access licenced datasets need to be lumped together under free datasets
    licenced_dict = {
        'name': 'licenced',
        'title': 'Free datasets',
    }

    free_dict = {}
    for items in licenced_datasets:
        item_licence = items['licences']
        item_licence[items['name']]['title'] = items['title']
        free_dict.update(item_licence)
    licenced_dict['licences'] = free_dict
    return licenced_dict


def _handle_ldap_group(licence, ldap_id, agreed):
    account = AccountAPI()
    payload = {
        'ldap_id': ldap_id,
        'groups': {
            licence: agreed
        }
    }
    return account.handle_role(payload)


def _check_freemium(dataset):
    details = Dataset.get_dataset_by_name(dataset)
    return True if details.type == 'freemium' else False


def _handle_ldap_freemium_updates(freemium_type, freemium_list, groups, current_list):
    agreed_freemium = [d for d in freemium_list if d['agreed']]
    if len(agreed_freemium) > 0 and freemium_type in groups:
        if freemium_type in str(current_list):
            app.logger.info('user already has role {} so not updating ldap'.format(freemium_type))
            del groups[freemium_type]
        else:
            groups[freemium_type] = True
    elif len(agreed_freemium) == 0 and freemium_type in str(current_list):
        direct_licence = freemium_type + '_direct'
        if direct_licence in str(current_list) and freemium_type in groups:
            app.logger.info('user has direct licence for role {} so not updating ldap'.format(freemium_type))
            del groups[freemium_type]
        else:
            groups[freemium_type] = False

    return groups


def _order_freemium_licences(item):
    func_list = ['Direct Use', 'Exploration', 'Commercial']
    return func_list.index(item)
