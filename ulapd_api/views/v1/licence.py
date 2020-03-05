from flask import request, Blueprint, jsonify
from ulapd_api.services import licence_service as service
from ulapd_api.app import app
from ulapd_api.exceptions import ApplicationError

licence_bp = Blueprint('licence_bp', __name__)


@licence_bp.route('', methods=['POST'])
def create_licence():
    try:
        licence_data = request.get_json()
        new_licence = service.create_licence(licence_data)
        return jsonify(new_licence), 201
    except ApplicationError as error:
        error_message = 'Failed to create licence {} - error: {}'.format(licence_data['licence_id'], error.message)
        app.logger.error(error_message)
        return jsonify(error=error_message), error.http_code
