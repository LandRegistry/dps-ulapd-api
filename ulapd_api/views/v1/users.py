from flask import request, Blueprint, jsonify
from ulapd_api.services import user_service as service
from ulapd_api.app import app
from ulapd_api.exceptions import ApplicationError


users_bp = Blueprint('users_bp', __name__)


@users_bp.route('', methods=['GET'])
def get_users():
    try:
        app.logger.info("Getting details for all users")
        users = service.get_all_users()
        return jsonify(users)
    except ApplicationError as error:
        error_message = "Failed to get all users - error: {}".format(error.message)
        app.logger.error(error_message)
        return jsonify(error=error_message), error.http_code


@users_bp.route('/<type>/<id>', methods=['GET'])
def get_user_by_key(type, id):
    try:
        app.logger.info("Getting details for user")
        user = service.get_user_by_key({'key': type, 'value': id})
        return jsonify(user)
    except ApplicationError as error:
        error_message = "Failed to get user: {} by key: {} - error: {}".format(id, type, error.message)
        app.logger.error(error_message)
        return jsonify(error=error_message), error.http_code


@users_bp.route('/licence/<user_id>', methods=['GET'])
def get_user_licences(user_id):
    try:
        app.logger.info("Getting licence details for user {}".format(user_id))
        user_licences = service.get_user_licences(user_id)
        return jsonify(user_licences)
    except ApplicationError as error:
        error_message = "Failed to get user licences - error: {}".format(error.message)
        app.logger.error(error_message)
        return jsonify(error=error_message), error.http_code


@users_bp.route('/licence/<user_id>/<licence_id>', methods=['GET'])
def get_agreed_licence(user_id, licence_id):
    try:
        app.logger.info("Getting licence agreement for user {} and licence {}".format(user_id, licence_id))
        agreed_licence = service.get_licence_agreement(user_id, licence_id)
        return jsonify(agreed_licence)
    except ApplicationError as error:
        error_message = "Failed to get agreed licence - error: {}".format(error.message)
        app.logger.error(error_message)
        return jsonify(error=error_message), error.http_code


@users_bp.route('/licence', methods=['POST'])
def manage_user_licence():
    try:
        licence = request.get_json()
        if 'licences' in licence:
            app.logger.info("Managing multiple licence agreements for user {}".format(licence['user_details_id']))
            new_licence = service.manage_multi_licence_agreement(licence)
        else:
            app.logger.info("Managing licence agreement for user {} and licence {}".format(licence['user_details_id'],
                                                                                           licence['licence_id']))
            new_licence = service.manage_licence_agreement(licence)
        return jsonify(new_licence), 201
    except ApplicationError as error:
        error_message = "Failed to add agreed licence - error: {}".format(error.message)
        app.logger.error(error_message)
        return jsonify(error=error_message), error.http_code


@users_bp.route('/dataset-activity/<user_id>', methods=['GET'])
def get_user_dataset_activity(user_id):
    try:
        app.logger.info("Getting dataset activity for user {}".format(user_id))
        dataset_activity = service.get_dataset_activity(user_id)
        return jsonify(dataset_activity)
    except ApplicationError as error:
        error_message = "Failed to get dataset activity {}".format(error.message)
        app.logger.error(error_message)
        return jsonify(error=error_message), error.http_code


@users_bp.route('', methods=['POST'])
def create_user():
    try:
        user_data = request.get_json()
        app.logger.info("Creating new user")
        new_user = service.create_new_user(user_data)
        return jsonify(new_user), 201
    except ApplicationError as error:
        error_message = "Failed to create new user - error: {}".format(error.message)
        app.logger.error(error_message)
        return jsonify(error=error_message), error.http_code


@users_bp.route('/contact_preference', methods=['PATCH'])
def update_user_contact_preference():
    try:
        user_data = request.get_json()
        app.logger.info("Updating the contact preference for user {}".format(user_data['user_id']))
        updated_user = service.update_contact_preference(user_data)
        app.logger.info("Update complete...")
        return jsonify(updated_user)
    except ApplicationError as error:
        error_message = "Failed to update user preference - error: {}".format(error.message)
        app.logger.error(error_message)
        return jsonify(error=error_message), error.http_code


@users_bp.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        app.logger.info("Creating new user")
        deleted_user = service.delete_user(user_id)
        return jsonify(deleted_user)
    except ApplicationError as error:
        error_message = "Failed to delete user - error: {}".format(error.message)
        app.logger.error(error_message)
        return jsonify(error=error_message), error.http_code


@users_bp.route('/<user_id>/update_api_key', methods=['POST'])
def update_api_key(user_id):
    try:
        app.logger.info("Resetting API key for user: {}".format(user_id))
        updated_user = service.update_api_key(user_id)
        return jsonify(updated_user)
    except ApplicationError as error:
        error_message = "Failed to update API key for user: {} - error: {}".format(user_id, error.message)
        app.logger.error(error_message)
        return jsonify(error=error_message), error.http_code


@users_bp.route('/dataset-access/<user_id>', methods=['GET'])
def get_users_dataset_access(user_id):
    try:
        app.logger.info('Getting dataset access for user: {}'.format(user_id))
        data_access = service.get_users_dataset_access(user_id)
        return jsonify(data_access)
    except ApplicationError as error:
        error_message = "Failed to get data access for user: {} - error: {}".format(user_id, error.message)
        app.logger.error(error_message)
        return jsonify(error=error_message), error.http_code
