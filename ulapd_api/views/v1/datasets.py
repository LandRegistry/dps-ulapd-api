from flask import Blueprint, jsonify, current_app, request
from ulapd_api.services import dataset_service
from ulapd_api.exceptions import ApplicationError

datasets = Blueprint('dataset_bp', __name__)


@datasets.route('', methods=['GET'])
def get_datasets():
    try:
        external = True if request.args.get('external') else False
        simple = True if request.args.get('simple') else False
        return jsonify(dataset_service.get_datasets(external, simple))
    except ApplicationError as error:
        error_message = 'Failed to get datasets - error: {}'.format(error.message)
        current_app.logger.error(error_message)
        return jsonify(error=error_message), error.http_code


@datasets.route('', methods=['POST'])
def create_dataset():
    try:
        dataset_data = request.get_json()
        new_dataset = dataset_service.create_dataset(dataset_data)
        return jsonify(new_dataset)
    except ApplicationError as error:
        error_message = 'Failed to create dataset: {} - error: {}'.format(dataset_data['name'], error.message)
        current_app.logger.error(error_message)
        return jsonify(error=error_message), error.http_code


@datasets.route('/<name>', methods=['GET'])
def get_dataset_by_name(name):
    try:
        return jsonify(dataset_service.get_dataset_by_name(name))
    except ApplicationError as error:
        error_message = 'Failed to get dataset: {} - error: {}'.format(name, error.message)
        current_app.logger.error(error_message)
        return jsonify(error=error_message), error.http_code


@datasets.route('/<name>/history', methods=['GET'])
def get_dataset_history(name):
    try:
        return jsonify(dataset_service.get_dataset_history(name))
    except ApplicationError as error:
        error_message = 'Failed to get dataset: {} history - error: {}'.format(name, error.message)
        current_app.logger.error(error_message)
        return jsonify(error=error_message), error.http_code


@datasets.route('/download/<name>/<file>', methods=['GET'])
@datasets.route('/download/history/<name>/<file>/<date>', methods=['GET'])
def get_download_link(name, file, date=None):
    try:
        if date:
            return jsonify(link=dataset_service.get_download_link(name, file, date))
        return jsonify(link=dataset_service.get_download_link(name, file))
    except ApplicationError as error:
        error_message = 'Failed to get download link for dataset: {} - error: {}'.format(name, error.message)
        current_app.logger.error(error_message)
        return jsonify(error=error_message), error.http_code


@datasets.route('/historical_cache', methods=['PUT'])
def historical_cache():
    try:
        result = dataset_service.update_historical_cache()
        return jsonify(result)
    except ApplicationError as error:
        error_message = 'Failed to update historical cache:  {} '.format(error.message)
        current_app.logger.error(error_message)
        return jsonify(error=error_message), error.http_code
