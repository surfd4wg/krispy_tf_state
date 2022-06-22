# klm_s3_tf_backend

## Description

Creates AWS infrastrure for managing terraform state

resources created

| Name | Purpose |
|------|---------|
| s3 | bucket to store terraform state files |
| dynamodb table | table for managing terraform state locks |
| iam | role and policy for utilizing infrastructure |

### Getting started
Pre-Reqs:
```bash
export AWS_PROFILE=your profile
export AWS_REGION=your region
```

1. clone this repo

```bash
https://github.com/surfd4wg/krispy_tf_state.git
```

2. navigate to the src directory

```bash
cd src
```

3. run invoke_tf.py

```bash
python invoke_tf.py --action apply --client test --profile default --region us-east-1
```

4. cd to your main terraform deployment directory
```
cd ../..
```
5. copy the backend file to current directory
```
cp src/tfstatebackend/s3.<region>.tfbackend .
```
6. create a new provider.tf file
```
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~>3.70.0"
    }
  }

  backend "s3" {}
}

provider "aws" {
}
```
7. terraform init with the newly created backend file
```
terraform init -backend-config="s3.<region>.tfbackend"
```
8. continue adding your additional terraform deployment files to the current directory (not the one used to create the backend). Followed by:
```
terraform init -backend-config="s3.<region>.tfbackend"
terraform plan
terraform apply -auto-approve
etc.
```
### invoke_tf.py

invoke_tf.py is a python script with logic to manage executing terraform to create the backend infrastructure and manage its state. Imports class from python files in the py_modules directory

arguments

| name | switch | description |
|------|--------|-------------|
| action | -a | terraform action to perform, accepts **apply** or **destroy** |
| client | -c | owner for the terraform created resources |
| profile | -p | aws credential profile name |
| region | -r | aws account region |

Todo:

Add step to migrate state to local on destroy to remove error related to releasing state lock

Init process

- Sets environment variables from profile and region to set environment variables AWS_PROFILE and AWS_REGION for terraform auth- 

- Sets variable **resource_name** used for naming terraform resources from the client and region arguments, ex **client-us-east-1-tf-state**
  
- Checks if an s3 bucket and a dynamodb table named **resource_name** exists, creates the resources if they do not exists using boto3
  
- Generates a backend config file named s3.tfbackend using the **resource_name** and **region** arguments. ex:

```bash
bucket          = "{client}-us-east-1-tf-state"
dynamodb_table  = "{client}-us-east-1-tf-state"
key             = "state/terraform.tfstate"
region          = "us-east-1"
encrypt         = true
```

- Generates terraform.tfvars file using the **client** argument to be used by terraform, ex:

```bash
client = "client"
```

- If an existing terraform state was found, runs **terraform init** using the backend config file. If not state is found, runs **terraform init** using the backend, then imports the terraform module resources for the s3 bucket and the dynamodb table into the state

- Executes terrform using the **action** argument (apply or destroy)

To use with an existing or new terraform deployment, configure the provider.tf to point to the backend, for example:
```
terraform {
  backend "s3" {
    bucket = "backend bucket name"
    dynamodb_table = "name of the dynamodb table"
    key    = "some folder name/terraform.tfstate"
    encrypt = true
    region = "region your in"
  }
}
```
