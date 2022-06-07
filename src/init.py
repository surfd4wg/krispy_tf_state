import logging
import boto3
from botocore.exceptions import ClientError
import subprocess
import shutil
import os
import argparse

def remove_tf_directory():
    path=".terraform"
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        pass

def assert_tf_state(bucket_name, key):
    try:
        client = boto3.client("s3")
        client.head_object(
            Bucket=bucket_name,
            Key=key
        )
        return True
    except ClientError as exc:
        return False

def get_s3_bucket(bucket_name):
    try:
        client = boto3.client("s3")
        bucket_list = []
        response = client.list_buckets()
        for bucket in response["Buckets"]:
            bucket_list.append(bucket["Name"])
        if bucket_name in bucket_list:
            return True
        else:
            return False

    except ClientError as exc:
        raise SystemExit(exc)

def create_s3_bucket(bucket_name, region):
    try:
        print(f"creating s3 bucket {bucket_name}")
        client = boto3.client('s3', region_name=region)
        client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
                "LocationConstraint": region
            })
        return True
    except ClientError as exc:
        logging.error(exc)
        return False

def wait_bucket(bucket_name):
    try:
        client = boto3.client('s3')
        waiter = client.get_waiter('bucket_exists')
        waiter.wait(
            Bucket=bucket_name,
            WaiterConfig={
                'Delay': 5,
                'MaxAttempts': 5
            }
        )
        print(f"s3 bucket {bucket_name} created")
    except ClientError as exc:
        raise SystemError(exc)

def get_dynamodb_table(table_name, region):
    try:
        client = boto3.client("dynamodb", region_name=region)
        response = client.list_tables()
        if table_name in response["TableNames"]:
            return True
        else:
            return False
    except ClientError as exc:
        raise SystemExit(exc)
    
def create_dynamo_table(table_name, region):
    try:
        print(f"creating dynamodb table {table_name}")
        client = boto3.client("dynamodb", region_name=region)
        response = client.create_table(
            AttributeDefinitions = [{
                "AttributeName": "LockID",
                "AttributeType": "S"
            }],
            TableName = table_name,
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

def create_backend_config(file_name, region, bucket_name, table_name):
    data = f"""
    bucket          = \"{bucket_name}\"
    dynamodb_table  = \"{table_name}\"
    region          = \"{region}\"
    key             = "terraform-state/terraform.tfstate"
    encrypt         = \"true\"
    """
    with open(file_name, "w") as file:
        file.write(data)

def create_tf_vars(client):
    file_name = "terraform.tfvars"
    data = f"""
    client = \"{client}\"
    """
    with open(file_name, "w") as file:
        file.write(data)

def assert_file(file_name):
    if os.path.exists(file_name):
        return True
    else:
        return False

def remove_file(file_name):
    if os.path.isfile(file_name):
        os.remove(file_name)
        return True
    else:
        return False

def invoke_terraform(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    poll = process.poll() is None
    for line in process.stdout:
        print(line)
    return poll

def main(args):
    print("setting init environment")

    os.environ["TF_VAR_client"] = args.client
    os.environ["AWS_REGION"] = args.region
    os.environ["AWS_PROFILE"] = args.profile

    resource_name = f"{args.client}-{args.region}-tf-state"

    try:

        print(f"checking backend infrastructure status for region {args.region}")

        bucket=get_s3_bucket(bucket_name=resource_name)

        state_file = assert_tf_state(bucket_name=resource_name, key="terraform-state/terraform.tfstate")

        dynamodb_table=get_dynamodb_table(table_name=resource_name, region=args.region)

        if bucket == True:
            print(f"s3 bucket {resource_name} exists")
            if state_file == True:
                print("terraform state exists")
            else:
                pass
        else:
            create_s3_bucket(bucket_name=resource_name, region=args.region)
            wait_bucket(bucket_name=resource_name)
        
        if dynamodb_table == True:
            print(f"dynamodb table {dynamodb_table} exists")
        else:
            create_dynamo_table(table_name=resource_name, region=args.region)

        create_backend_config(file_name=f"s3.tfbackend", region=args.region, bucket_name=resource_name, table_name=resource_name)

        create_tf_vars(client=args.client)
    
        invoke_terraform(f"terraform fmt --recursive")

        if state_file == True:
            invoke_terraform(f"terraform init -backend-config=\"s3.tfbackend\"")
        else:
            invoke_terraform(f"terraform init -reconfigure -backend-config=\"s3.tfbackend\"")

            invoke_terraform(f"terraform import module.s3_backend.aws_s3_bucket.main {resource_name}")

            invoke_terraform(f"terraform import module.s3_backend.aws_dynamodb_table.main {resource_name}")


        invoke_terraform(f"terraform {args.action} -auto-approve")

        remove_file("terraform.tfvars")

        remove_file(".terraform.lock.hcl")

        remove_file("s3.tfbackend")

        remove_tf_directory()

    except Exception as exc:
        raise SystemExit(exc)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a",
                        "--action",
                        choices=["apply","destroy"],
                        default="plan",
                        help="terraform action to perform")
    parser.add_argument("-c",
                        "--client",
                        required=True,
                        help="owner for the terraform created resources")
    parser.add_argument("-p",
                        "--profile",
                        required=True,
                        help="aws credential profile name")
    parser.add_argument("-r",
                        "--region",
                        choices=["us-east-1","us-east-2","us-west-1","us-west-2"],
                        required=True,
                        help="aws account region")
    args = parser.parse_args()
    main(args)
