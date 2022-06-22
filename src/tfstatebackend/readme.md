The terraform state file is stored in this directory, called something like s3..tfbackend. 
On the next terraform init -backend-config=s3..tfbackend, terraform uploads the state file to the s3 bucket.

On every terraform init following this, the same command terraform init -backend-config=s3.<region>.tfbackend must be run, 
  in order to point terraform to the state file in s3, as specified in the s3.tfbackend file.
