resource "aws_s3_bucket" "main" {
  bucket        = var.bucket_name
  force_destroy = true

  tags = {
    Name        = var.bucket_name
    description = "terraform s3 backend bucket"
  }
}

resource "aws_s3_bucket_acl" "main" {
  bucket = aws_s3_bucket.main.id
  acl    = "private"
}

resource "aws_s3_bucket_versioning" "main" {
  bucket = aws_s3_bucket.main.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.bucket

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "main" {
  bucket                  = aws_s3_bucket.main.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_dynamodb_table" "main" {
  name           = var.table_name
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "LockID"
  attribute {
    name = "LockID"
    type = "S"
  }
}

resource "aws_iam_role" "main" {
  name = var.role_name
  assume_role_policy = jsonencode({
    "Version" = "2012-10-17"
    "Statement" = [
      {
        "Effect" = "Allow",
        "Action" = "sts:AssumeRole",
        "Principal" = {
          "AWS" : "arn:aws:iam::${var.account_id}:root"
        }
      }
    ]
  })
  tags = {
    description = "terraform backend role"
  }
}

resource "aws_iam_role_policy" "main" {
  name = "${aws_iam_role.main.name}-policy"
  role = aws_iam_role.main.name

  policy = jsonencode({
    "Version" = "2012-10-17"
    "Statement" = [
      {
        "Effect"   = "Allow",
        "Resource" = ["${aws_s3_bucket.main.arn}"],
        "Action" = [
          "s3:ListBucket",
          "s3:GetBucketVersioning"
        ]
      },
      {
        "Effect" = "Allow",
        "Action" = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject"
        ],
        "Resource" = ["${aws_s3_bucket.main.arn}/*"]
      },
      {
        "Effect" = "Allow",
        "Action" = [
          "dynamodb:DescribeTable",
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem"
        ],
        "Resource" = ["${aws_dynamodb_table.main.arn}"]
      },
    ]
  })
}
