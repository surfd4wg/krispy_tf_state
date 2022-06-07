output "state_bucket" {
  value = aws_s3_bucket.main.bucket
}

output "state_table" {
  value = aws_dynamodb_table.main.name
}