import os
import json
import unittest
from ulapd_api.app import app
from unittest.mock import patch, MagicMock
from common_utilities import errors
from ulapd_api.exceptions import ApplicationError

from ulapd_api.services import dataset_service as service


@patch('ulapd_api.utilities.decorators.db')
class TestDatasetService(unittest.TestCase):
    directory = os.path.dirname(__file__)
    test_metadata = json.loads(open(os.path.join(directory, 'data/metadata_example.json'), 'r').read())
    expected_metadata = json.loads(open(os.path.join(directory, 'data/expected_metadata.json'), 'r').read())
    expected_history = json.loads(open(os.path.join(directory, 'data/expected_history.json'), 'r').read())
    test_history_cache = json.loads(open(os.path.join(directory, 'data/history_cache_example.json'), 'r').read())

    def setUp(self):
        self.app = app.test_client()

    @patch("ulapd_api.services.dataset_service.Dataset")
    @patch("ulapd_api.services.dataset_service._metadata_extend")
    @patch("ulapd_api.services.dataset_service._extract_rows")
    def test_get_datasets(self, mock_extract, mock_metadata, mock_dataset, *_):
        extract = [{'foo': 'bar'}, {'foo': 'bar'}]
        mock_extract.return_value = extract
        mock_dataset.get_datasets.return_value = MagicMock()
        result = service.get_datasets()
        self.assertEqual(result, extract)

    @patch("ulapd_api.services.dataset_service.Dataset")
    @patch("ulapd_api.services.dataset_service._metadata_extend")
    @patch("ulapd_api.services.dataset_service._extract_rows")
    def test_get_datasets_simple(self, mock_extract, mock_metadata, mock_dataset, *_):
        extract = [{'foo': 'bar'}, {'foo': 'bar'}]
        mock_extract.return_value = extract
        mock_dataset.get_datasets.return_value = MagicMock()
        result = service.get_datasets(False, True)
        self.assertEqual(result, extract)

    @patch("ulapd_api.services.dataset_service.Dataset")
    @patch("ulapd_api.services.dataset_service._metadata_extend")
    def test_get_datasets_by_name(self, mock_metadata, mock_dataset, *_):
        mock_metadata.return_value = {'foo': 'bar'}
        mock_dataset.get_dataset_by_name.return_value = mock_metadata
        result = service.get_dataset_by_name('ccod')
        self.assertEqual(result, {'foo': 'bar'})

    @patch("ulapd_api.services.dataset_service.Dataset")
    def test_get_datasets_by_name_no_row(self, mock_dataset, *_):
        mock_dataset.get_dataset_by_name.return_value = None
        with self.assertRaises(ApplicationError) as context:
            service.get_dataset_by_name('ccod')

        expected_err = ('ulapd_api', 'DATASET_NOT_FOUND')
        expected_err_message = errors.get_message(*expected_err, filler='ccod')
        expected_err_code = errors.get_code(*expected_err)

        self.assertEqual(context.exception.message, expected_err_message)
        self.assertEqual(context.exception.code, expected_err_code)

    @patch("ulapd_api.services.dataset_service.Dataset")
    @patch("ulapd_api.services.dataset_service._metadata_extend_history")
    def test_get_dataset_history(self, mock_metadata, mock_dataset, *_):
        mock_metadata.return_value = {'foo': 'bar'}
        mock_dataset.get_dataset_by_name.return_value = mock_metadata
        result = service.get_dataset_history('ccod')
        self.assertEqual(result, {'foo': 'bar'})

    @patch("ulapd_api.services.dataset_service.Dataset")
    def test_get_dataset_history_no_row(self, mock_dataset, *_):
        mock_dataset.get_dataset_by_name.return_value = None
        with self.assertRaises(ApplicationError) as context:
            service.get_dataset_history('ccod')

        expected_err = ('ulapd_api', 'DATASET_NOT_FOUND')
        expected_err_message = errors.get_message(*expected_err, filler='ccod')
        expected_err_code = errors.get_code(*expected_err)

        self.assertEqual(context.exception.message, expected_err_message)
        self.assertEqual(context.exception.code, expected_err_code)

    @patch("ulapd_api.services.dataset_service.db")
    @patch("ulapd_api.services.dataset_service.Dataset")
    def test_create_dataset(self, mock_dataset, mock_db, *_):
        data = {'name': 'ulapd'}
        mock_dataset.get_dataset_by_name.return_value = None
        mock_dataset.return_value = _create_dataset_profile()
        result = service.create_dataset(data)
        self.assertEqual(result, example_dict)

    @patch("ulapd_api.services.dataset_service.db")
    @patch("ulapd_api.services.dataset_service.Dataset")
    def test_create_dataset_already_exists(self, mock_dataset, mock_db, *_):
        data = {'name': 'ulapd'}
        mock_dataset.get_dataset_by_name.return_value = MagicMock()
        mock_dataset.return_value = _create_dataset_profile()
        result = service.create_dataset(data)
        self.assertEqual(result, example_dict)

    @patch("ulapd_api.services.dataset_service.S3")
    @patch("ulapd_api.services.dataset_service.get_dataset_by_name")
    def test_get_download_link(self, mock_get_by_name, mock_s3, *_):
        mock_get_by_name.return_value.get.return_value = False
        mock_s3.return_value.build_presigned_url.return_value = 'www.gov.uk/ccod'
        result = service.get_download_link('ccod', 'CCOD_FULL_2019_11.zip', False)
        self.assertEqual(result, 'www.gov.uk/ccod')

    @patch("ulapd_api.services.dataset_service.S3")
    @patch("ulapd_api.services.dataset_service.get_dataset_by_name")
    def test_get_download_link_with_date(self, mock_get_by_name, mock_s3, *_):
        mock_get_by_name.return_value.get.return_value = False
        mock_s3.return_value.build_presigned_url.return_value = 'www.gov.uk/ccod'
        result = service.get_download_link('ccod', 'CCOD_FULL_2019_11.zip', 'August 2019')
        self.assertEqual(result, 'www.gov.uk/ccod')

    @patch("ulapd_api.services.dataset_service.S3")
    @patch("ulapd_api.services.dataset_service._fetch_prefixes")
    def test_update_historical_cache(self, mock_prefixes, mock_s3, *_):
        mock_s3.return_value = MagicMock()
        mock_s3.return_value.BUCKET_NAME.return_value = 'bucket'
        mock_s3.return_value.BUCKET_RESTRICTED.return_value = 'other_bucket'
        mock_prefixes.return_value = ['ccod/']
        mock_s3.return_value.fetch_s3_file.return_value = {'some': 'data'}
        mock_s3.write_to_s3.return_value = MagicMock()
        result = service.update_historical_cache()
        self.assertEqual(result, {'result': 'ok'})

    @patch("ulapd_api.services.dataset_service.S3")
    @patch("ulapd_api.services.dataset_service._fetch_prefixes")
    def test_update_historical_cache_exception(self, mock_prefixes, mock_s3, *_):
        mock_s3.return_value = MagicMock()
        mock_s3.return_value.BUCKET_NAME.return_value = 'bucket'
        mock_s3.return_value.BUCKET_RESTRICTED.return_value = 'other_bucket'
        mock_prefixes.return_value = ['ccod/']
        mock_s3.return_value.fetch_s3_file.side_effect = ApplicationError('Some error', 400)
        mock_s3.return_value.write_to_s3.side_effect = ApplicationError('Some error', 400)
        result = service.update_historical_cache()
        self.assertEqual(result, {'result': 'Failed to write cache, please check logs'})

    def test_extract_rows_no_rows(self, *_):
        result = service._extract_rows([])
        self.assertEqual(result, [])

    def test_extract_rows(self, *_):
        mock_row = MagicMock()
        mock_row.as_dict.return_value = {'foo': 'bar'}
        result = service._extract_rows([mock_row, mock_row])
        self.assertEqual(result, [{'foo': 'bar'}, {'foo': 'bar'}])

    @patch("ulapd_api.services.dataset_service.S3")
    @patch("ulapd_api.services.dataset_service.format_file_size")
    @patch("ulapd_api.services.dataset_service.format_last_updated_date")
    def test_metadata_extend(self, mock_date, mock_file_size, mock_s3, *_):
        row = {'name': 'ccod', 'private': False, 'external': False}
        expected_result = self.expected_metadata
        mock_s3.return_value.get_s3_resource.return_value = self.test_metadata
        mock_file_size.return_value = '1.17 MB'
        mock_date.return_value = 'October 2019'
        result = service._metadata_extend(row)
        self.assertDictEqual(expected_result, result)

    @patch("ulapd_api.services.dataset_service.S3")
    @patch("ulapd_api.services.dataset_service.format_file_size")
    @patch("ulapd_api.services.dataset_service.format_last_updated_date")
    def test_metadata_extend_history(self, mock_date, mock_file_size, mock_s3, *_):
        row = {'name': 'ccod', 'private': False, 'external': False, 'type': 'licenced'}
        expected_result = self.expected_history
        mock_s3.return_value.get_s3_resource.return_value = self.test_history_cache
        mock_file_size.return_value = '1.17 MB'
        mock_date.return_value = 'October 2019'
        result = service._metadata_extend_history(row)
        self.assertDictEqual(expected_result, result)

    def test_metadata_extend_history_external(self, *_):
        row = {'name': 'ccod', 'private': False, 'external': True}
        result = service._metadata_extend_history(row)
        self.assertDictEqual(row, result)

    @patch("ulapd_api.services.dataset_service.format_file_size")
    def test_map_resources(self, mock_file_size, *_):
        resource = {
            "file_count": 1,
            "file_name": "file",
            "format": "CSV",
            "file_size": 12345,
            "row_count": 10,
            "name": "ccod"
        }
        mock_file_size.return_value = "0.12 MB"
        expected_result = {
            "file_count": 1,
            "file_name": "file",
            "format": "CSV",
            "file_size": "0.12 MB",
            "row_count": 10,
            "name": "ccod"
        }
        result = service._map_resources(resource)
        self.assertDictEqual(result, expected_result)

    def test_fetch_prefixes(self, *_):
        data = {'CommonPrefixes': [{'Prefix': 'nps/history/2019_06/'}, {'Prefix': 'nps/history/2019_07/'}]}
        result = service._fetch_prefixes(data)
        expected_result = ['nps/history/2019_06/', 'nps/history/2019_07/']
        self.assertEqual(result, expected_result)


def _create_dataset_profile(dataset_id=1, name='foo', title='bar', version='v1', url='www',
                            notes='Hi', licence_id='fubar', state='active', type='free',
                            private=False, metadata_created='2019-11-18 09:07:49.422595', external=False):
    dataset_profile = MagicMock()
    dataset_profile.dataset_id = dataset_id
    dataset_profile.name = name
    dataset_profile.title = title
    dataset_profile.version = version
    dataset_profile.url = url
    dataset_profile.notes = notes
    dataset_profile.licence_id = licence_id
    dataset_profile.state = state
    dataset_profile.type = type
    dataset_profile.private = private
    dataset_profile.metadata_created = metadata_created
    dataset_profile.external = external
    dataset_profile.as_dict.return_value = example_dict
    return dataset_profile


example_dict = {
    'dataset_id': 1,
    'name': 'foo',
    'title': 'bar',
    'version': 'v1',
    'url': 'www',
    'notes': 'Hi',
    'licence_id': 'fubar',
    'state': 'active',
    'type': 'free',
    'private': False,
    'metadata_created': '2019-11-18 09:07:49.422595',
    'external': False
}
