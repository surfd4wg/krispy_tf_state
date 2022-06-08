import logging
import boto3
from botocore.exceptions import ClientError
import os

class S3():
    def __init__(self, bucket_name,region, key = None):
        super().__init__()
        self.bucket_name = bucket_name
        self.key = key
        self.region = region

        self.client = boto3.client("s3", region_name=self.region)
        
    def assert_bucket(self):
        try:
            bucket_list = []
            response = self.client.list_buckets()
            for bucket in response["Buckets"]:
                bucket_list.append(bucket["Name"])
            if self.bucket_name in bucket_list:
                return True
            else:
                return False

        except ClientError as exc:
            raise SystemExit(exc)


    def assert_object(self):
        try:
            self.client.head_object(
                Bucket=self.bucket_name,
                Key=self.key
            )
            return True
        except ClientError as exc:
            return False

    def create_bucket(self):
        try:
            self.client.create_bucket(
                Bucket=self.bucket_name,
                CreateBucketConfiguration={
                    "LocationConstraint": self.region
                })
            self.wait_bucket()
            return True
        except ClientError as exc:
            logging.error(exc)
            return False

    def wait_bucket(self):
        try:
            waiter = self.client.get_waiter('bucket_exists')
            waiter.wait(
                Bucket=self.bucket_name,
                WaiterConfig={
                    'Delay': 5,
                    'MaxAttempts': 5
                }
            )
        except ClientError as exc:
            raise SystemError(exc)

class DynamoDb():
    def __init__(self, table_name, region):
        super().__init__()
        self.table_name = table_name
        self.region = region
        self.client = boto3.client("dynamodb", region_name=self.region)

    def assert_table(self):
        try:
            response = self.client.list_tables()
            if self.table_name in response["TableNames"]:
                return True
            else:
                return False
        except ClientError as exc:
            raise SystemExit(exc)

    def create_table(self):
        try:
            response = self.client.create_table(
                AttributeDefinitions = [{
                    "AttributeName": "LockID",
                    "AttributeType": "S"
                }],
                TableName = self.table_name,
                KeySchema = [
                    {
                        "AttributeName": "LockID",
                        "KeyType": "HASH"
                    }
                ],
                ProvisionedThroughput={
                    "ReadCapacityUnits": 10,
                    "WriteCapacityUnits": 10,
                },
            )

            return response

        except ClientError as exc:
            logging.error(exc)
            return False
        
