import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from ulapd_api.main import app
from ulapd_api.services import activity_service as service


@patch('ulapd_api.utilities.decorators.db')
@patch('ulapd_api.services.activity_service.db')
class TestActivityService(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    @patch('ulapd_api.services.activity_service.Activity')
    def test_add_user_activity(self, mock_activity, *_):
        data = {
            'activity_id': 1,
            'dataset_id': 'ccod',
            'timestamp': datetime.now(),
            'user_details_id': 123,
            'activity_type': 'download',
            'ip_address': '10.10.10.9.0',
            'api': False,
            'file': 'CCOD_COU_FILE.zip'
        }
        activity = MagicMock()
        activity.as_dict.return_value = data

        mock_activity.return_value = activity
        result = service.add_user_activity(data)
        self.assertEqual(result, data)

    def test_extract_rows_no_rows(self, *_):
        result = service._extract_rows([])
        self.assertEqual(result, [])

    def test_extract_rows(self, *_):
        mock_row = MagicMock()
        mock_row.as_dict.return_value = {'foo': 'bar'}
        result = service._extract_rows([mock_row, mock_row])
        self.assertEqual(result, [{'foo': 'bar'}, {'foo': 'bar'}])
