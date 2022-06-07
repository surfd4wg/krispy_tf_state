module "s3_backend" {
  source = "./modules/s3_backend"

  account_id  = data.aws_caller_identity.current.account_id
  bucket_name = "${var.client}-${data.aws_region.current.name}-tf-state"
  role_name   = "${var.client}-${data.aws_region.current.name}-tf-state-role"
  table_name  = "${var.client}-${data.aws_region.current.name}-tf-state"
}