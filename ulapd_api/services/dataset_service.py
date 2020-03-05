from ulapd_api.models.dataset import Dataset
from ulapd_api.extensions import db
from ulapd_api.exceptions import ApplicationError
from ulapd_api.utilities.decorators import handle_errors
from ulapd_api.utilities.helpers import format_file_size, format_last_updated_date
from ulapd_api.dependencies.s3 import S3
from ulapd_api.app import app
import json
from common_utilities import errors


@handle_errors(is_get=True)
def get_datasets(external=False, simple=False):
    if simple:
        return _extract_rows(Dataset.get_all(external))
    else:
        return _extract_rows(Dataset.get_all(external), _metadata_extend)


@handle_errors(is_get=True)
def get_dataset_by_name(name):
    dataset = Dataset.get_dataset_by_name(name)
    if dataset:
        return _metadata_extend(dataset.as_dict())
    else:
        raise ApplicationError(*errors.get('ulapd_api', 'DATASET_NOT_FOUND', filler=name), http_code=404)


@handle_errors(is_get=True)
def get_dataset_history(name):
    dataset = Dataset.get_dataset_by_name(name)
    if dataset:
        return _metadata_extend_history(dataset.as_dict())
    else:
        raise ApplicationError(*errors.get('ulapd_api', 'DATASET_NOT_FOUND', filler=name), http_code=404)


@handle_errors(is_get=False)
def create_dataset(data):
    existing_dataset = Dataset.get_dataset_by_name(data['name'])
    if existing_dataset:
        db.session.delete(existing_dataset)
        db.session.flush()

    new_dataset = Dataset(data)
    db.session.add(new_dataset)
    db.session.commit()
    return new_dataset.as_dict()


@handle_errors(is_get=True)
def get_download_link(dataset_name, file_name, date=None):
    if date:
        path = '{}/history/{}/{}'.format(dataset_name, date, file_name)
    else:
        path = '{}/{}'.format(dataset_name, file_name)

    is_private = get_dataset_by_name(dataset_name).get('private')
    return S3().build_presigned_url(path, is_private)


@handle_errors(is_get=False)
def update_historical_cache():

    s3 = S3()
    session = s3.get_s3_session()
    buckets = [s3.BUCKET_NAME, s3.S3_BUCKET_RESTRICTED]

    for bucket in buckets:
        datasets = _fetch_prefixes(session.list_objects_v2(Bucket=bucket, Delimiter='/'))
        app.logger.info('Found {} datasets {}, updating cache.'.format(len(datasets), datasets))

        for dataset in datasets:
            months = _fetch_prefixes(session.list_objects_v2(Bucket=bucket, Prefix=dataset + 'history/',
                                                             Delimiter='/'))
            app.logger.info('Months found: ' + str(months))

            def fetch_metadata(month):
                if month is not None:
                    try:
                        return s3.fetch_s3_file(month + 'metadata.json', bucket)
                    except Exception as e:
                        app.logger.error('Error: {} '.format(str(e)))
                        pass
            historical_metadata = list(filter(lambda x: x is not None, map(fetch_metadata, months)))
            app.logger.info('Historical Metadata Created: ' + str(historical_metadata))

            try:
                app.logger.info('writing to S3: ' + str(json.dumps(historical_metadata)))
                s3.write_to_s3('{}history/history_cache.json'.format(dataset), json.dumps(historical_metadata), bucket)
            except Exception:
                return {
                    'result': 'Failed to write cache, please check logs'
                }

    return {
        'result': 'ok',
    }


def _extract_rows(rows, map_func=lambda _: _):
    return [map_func(row.as_dict()) for row in rows]


def _metadata_extend(row):
    if not row['external']:
        metadata = S3().get_s3_resource(row['name'], '/metadata.json', row['private'])

        # Top level elements
        row['file_count'] = metadata.get('file_count')  # Not always populated
        row['last_updated'] = format_last_updated_date(metadata['last_updated'])
        row['fee'] = metadata['fee']
        row['tech_spec_url'] = metadata['tech_spec_url']
        row['format'] = metadata['format']
        row['update_frequency'] = metadata['update_frequency']
        row['file_size'] = format_file_size(metadata['file_size'])

        # Array elements
        row['resources'] = list(map(lambda x: _map_resources(x), metadata['resources']))
        row['public_resources'] = list(map(lambda x: _map_resources(x), metadata['public_resources']))

    return row


def _metadata_extend_history(row):
    if not row['external']:
        if row['type'] == 'open':
            metadata = S3().get_s3_resource(row['name'], '/history/history_cache.json')
        else:
            metadata = S3().get_s3_resource(row['name'], '/history/history_cache.json', row['private'])

        dataset_history = []
        for file in metadata:
            resource_list = []
            for resource in file['resources']:
                resource_list.append({
                    "file_size": format_file_size(resource['file_size']),
                    "file_name": resource['file_name'],
                    "format": resource['format']
                })

            last_updated_pattern = {
                "Daily": "%d %B %Y",
                "Monthly": "%B %Y",
                "Every 3 months": "%B %Y"
            }

            pattern = last_updated_pattern[file['update_frequency']]

            dataset_history.append({
                "unsorted_date": file['last_updated'],
                "last_updated": format_last_updated_date(file['last_updated'], pattern=pattern),
                "resource_list": resource_list
            })

        dataset_history.reverse()
        row['dataset_history'] = dataset_history
        return row
    return row


def _map_resources(resource):
    return {
        "file_count": resource['file_count'],
        "file_name": resource['file_name'],
        "format": resource['format'],
        "file_size": format_file_size(resource['file_size']),
        "row_count": resource['row_count'],
        "name": resource['name']
    }


def _fetch_prefixes(list_obj):
    return list(map(lambda x: x['Prefix'], list_obj['CommonPrefixes']))
