from flask import Blueprint, jsonify, current_app, request
from ulapd_api.services import activity_service
from ulapd_api.exceptions import ApplicationError


activity_bp = Blueprint('activity_bp', __name__)


@activity_bp.route('/<user_id>', methods=['GET'])
def get_activity(user_id):
    try:
        user_activity = activity_service.get_user_activity_list(user_id)
        return jsonify(user_activity)
    except ApplicationError as error:
        error_message = 'Failed to get user activity: {} - error: {}'.format(user_id, error.message)
        current_app.logger.error(error_message)
        return jsonify(error=error_message), error.http_code


@activity_bp.route('', methods=['POST'])
def add_activity():
    try:
        activity_data = request.get_json()
        new_activity = activity_service.add_user_activity(activity_data)
        return jsonify(new_activity)
    except ApplicationError as error:
        error_message = 'Failed to add activity - error: {}'.format(error.message)
        current_app.logger.error(error_message)
        return jsonify(error=error_message), error.http_code
