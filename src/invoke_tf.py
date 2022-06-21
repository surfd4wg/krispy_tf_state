import shutil
import os
import argparse
from py_modules.aws import *
from py_modules.terraform import *


def remove_directory(dir_name):
    if os.path.isdir(dir_name):
        shutil.rmtree(dir_name)
    else:
        pass

def remove_file(file_name):
    if os.path.isfile(file_name):
        os.remove(file_name)
        return True
    else:
        return False

def main(args):

    os.environ["AWS_REGION"] = args.region
    os.environ["AWS_PROFILE"] = args.profile

    resource_name = f"{args.client}-{args.region}-tf-state"

    backend_file = f"s3.{args.region}.tfbackend"
    tfvar_file = "terraform.tfvars"

    print(f"checking backend infrastructure status for region {args.region}")

    bucket_exists = S3(bucket_name=resource_name, region=args.region).assert_bucket()

    state_exists = S3(bucket_name=resource_name, region=args.region,key="terraform-state/terraform.tfstate")

    table_exists = DynamoDb(table_name=resource_name, region=args.region).assert_table()

    if bucket_exists == True:
        print(f"S3 bucket {resource_name} exists")
    else:
        S3(bucket_name=resource_name, region=args.region).create_bucket()

    if table_exists == True:
        print(f"DynamoDb table {resource_name} exists")
    else:
        DynamoDb(table_name=resource_name, region=args.region).create_table()

    if bucket_exists == True and table_exists == True:
        print(f"backend infrastructure exists in region {args.region}")

    backend_args = {
        "client": str(args.client),
        "bucket_name": str(resource_name),
        "table_name": str(resource_name),
        "region": str(args.region),
        "file_name": str(backend_file)
    }

    TfFiles(**backend_args).tf_backend_config()

    tfvar_args = {
        "client": args.client,
        "file_name": str(tfvar_file)
    }

    TfFiles(**tfvar_args).tf_vars()

    if args.action == "destroy":
        TfCmd(backend_config=backend_file).tf_init()
        TfCmd().tf_destroy()

    elif args.action == "apply":
        if state_exists == True:
            TfCmd(backend_config=backend_file).tf_init()
        else:
            TfCmd(backend_config=backend_file).tf_init()
            TfCmd(module_import=f"module.s3_backend.aws_s3_bucket.main {resource_name}").tf_import()
            TfCmd(module_import=f"module.s3_backend.aws_dynamodb_table.main {resource_name}").tf_import()
        TfCmd().tf_apply()

    elif args.action == "plan":
        TfCmd(backend_config=backend_file).tf_init()
        TfCmd().tf_plan()

    move_file(source=backend_file, destination="./tfstatebackend/{backend_file}")

    remove_directory(".terraform")
    #remove_file(backend_args.get("file_name"))
    #remove_file(tfvar_args.get("file_name"))
    remove_file(".terraform.lock.hcl")
    remove_file("terraform.tfstate")
    remove_file("errored.tfstate")

def move_file(source, destination):
    shutil.move(source, destination)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a",
                        "--action",
                        choices=["apply","destroy","plan"],
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