variable "account_id" {
  type        = string
  description = "aws partition for "
}

variable "bucket_name" {
  type        = string
  description = "name for the state s3 bucket"
}

variable "role_name" {
  type        = string
  description = "name for the state management iam role"
}

variable "table_name" {
  type        = string
  description = "name for the locking dynamodb table"
}