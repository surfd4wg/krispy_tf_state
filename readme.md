# r3d_aws_tf_backend

## Description

Creates AWS infrastrure for managing terraform state

resources created

| Name | Purpose |
|------|---------|
| s3 | bucket to store terraform state files |
| dynamodb table | table for managing terraform state locks |
| iam | role and policy for utilizing infrastructure |

### Getting started

clone this repo

```bash
https://github.com/r3dlocust/r3d_aws_tf_backend.git
```

navigate to the src directory

```bash
cd src
```

run init.py

```bash
python init.py --action apply --client test --profile default --region us-east-1
```

### init.py

Init.py is a python script with logic to manage executing the terraform to create the backend infrastructure and manage its state.

arguments

| name | switch | description |
|------|--------|-------------|
| action | -a | terraform action to perform, accepts **apply** or **destroy** |
| client | -c | owner for the terraform created resources |
| profile | -p | aws credential profile name |
| region | -r | aws account region |

Todo:

Add step to migrate state to local on destroy to remove error related to releasing state lock