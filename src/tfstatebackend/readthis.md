The terraform state file is stored in this directory, called something like s3.<region>.tfbackend.
On the next terraform init -backend-config=s3.<region>.tfbackend, terraform uploads the state file to the s3 bucket.
