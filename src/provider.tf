provider "aws" {
  default_tags {
    tags = {
      owner       = var.client
      description = "terraform state management"
      builder     = "terraform"
    }
  }
}