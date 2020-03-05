import unittest
from unittest.mock import patch, MagicMock
from ulapd_api.main import app
from ulapd_api.services import licence_service as service


@patch('ulapd_api.utilities.decorators.db')
@patch('ulapd_api.services.licence_service.db')
class TestActivityrService(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    @patch('ulapd_api.services.licence_service.Licence')
    def test_create_licence(self, mock_licence, *_):
        licence = MagicMock()
        licence.as_dict.return_value = {'dataset_licence_id': 1}
        mock_licence.return_value = licence
        mock_licence.get_licence_by_licence_name.return_value = None
        result = service.create_licence({'licence_id': 'ccod'})
        self.assertEqual(result, {'dataset_licence_id': 1})

    @patch('ulapd_api.services.licence_service.Licence')
    def test_create_licence_already_exists(self, mock_licence, *_):
        licence = MagicMock()
        licence.as_dict.return_value = {'dataset_licence_id': 1}
        mock_licence.return_value = licence
        mock_licence.get_licence_by_licence_name.return_value = MagicMock()
        result = service.create_licence({'licence_id': 'ccod'})
        self.assertEqual(result, {'dataset_licence_id': 1})
