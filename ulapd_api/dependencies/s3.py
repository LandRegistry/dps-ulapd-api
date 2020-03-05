import boto3
from botocore.client import Config
from botocore.errorfactory import ClientError
import requests
from ulapd_api.app import app
from flask import current_app
import json


class S3(object):

    def __init__(self):
        self.BUCKET_NAME = app.config.get('S3_BUCKET')
        self.S3_BUCKET_RESTRICTED = app.config.get('S3_BUCKET_RESTRICTED')
        self.S3_REGION = app.config.get('S3_BUCKET_REGION')
        self.S3_URL_EXPIRATION = app.config.get('S3_URL_EXPIRATION')

    def get_s3_session(self):
        return boto3.client('s3', config=Config(signature_version='s3v4',
                                                region_name=self.S3_REGION))

    def get_s3_resource(self, dataset_id, resource, restricted_bucket=False):
        key = dataset_id + resource
        try:
            s3 = self.get_s3_session()

            bucket = self.S3_BUCKET_RESTRICTED if restricted_bucket else self.BUCKET_NAME

            url = s3.generate_presigned_url(ClientMethod='get_object',
                                            Params={'Bucket': bucket, 'Key': key},
                                            ExpiresIn=self.S3_URL_EXPIRATION)

            resp = requests.get(url)

            try:
                json_resp = resp.json()
                return json_resp
            except ValueError as e:
                current_app.logger.error('Something went wrong getting a resource from S3: ' + str(e))
                return resp.text
        except Exception as e:
            current_app.logger.error(str(e))
            raise e

    def build_presigned_url(self, path, restricted_bucket=False):
        s3 = self.get_s3_session()

        bucket = self.S3_BUCKET_RESTRICTED if restricted_bucket else self.BUCKET_NAME

        url = s3.generate_presigned_url(ClientMethod='get_object',
                                        Params={
                                            'Bucket': bucket,
                                            'Key': path,
                                            'ResponseContentType': 'application/force-download'
                                        },
                                        ExpiresIn=self.S3_URL_EXPIRATION)
        return url

    def fetch_s3_file(self, path, bucket):
        try:
            s3 = self.get_s3_session()
            res = s3.get_object(Bucket=bucket, Key=path)
            return json.loads(res['Body'].read())
        except ClientError:
            current_app.logger.info("There was no file in the S3 folder: {}".format(path))
            pass
        except Exception as e:
            current_app.logger.error("Something went wrong fetching the S3 file: {}".format(e))
            raise e

    def write_to_s3(self, path, content, bucket):
        try:
            s3 = self.get_s3_session()
            s3.put_object(Body=content, Bucket=bucket, Key=path)
        except Exception as e:
            current_app.logger.error("Something went wrong writing to the S3 bucket: {}".format(e))
            raise e
