from ulapd_api.app import app
from ulapd_api.dependencies.s3 import S3

import logging
import unittest

log = logging.getLogger(__name__)


class TestS3(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_get_s3_resource(self):
        test_s3 = S3()
        response = test_s3.get_s3_resource('ccod', '/metadata.json')
        print(str(response))
        self.assertIn('resources', response)

    def test_s3_build_presigned_url(self):
        test_s3 = S3()
        response = test_s3.build_presigned_url('ccod', 'CCOD_FULL_2019_09.zip')
        print(str(response))
        self.assertIn('ccod', response)
