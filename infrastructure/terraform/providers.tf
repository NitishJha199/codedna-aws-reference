provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project   = "codedna-aws-reference"
      ManagedBy = "terraform"
      Purpose   = "codedna-e2e-validation"
    }
  }
}
