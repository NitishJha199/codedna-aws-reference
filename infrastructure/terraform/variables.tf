variable "aws_region" {
  description = "AWS region for the CodeDNA reference environment."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Resource naming prefix."
  type        = string
  default     = "codedna-ref"
}

variable "github_owner" {
  description = "GitHub organization or user owning the reference repository."
  type        = string
  default     = "NitishJha199"
}

variable "github_repository" {
  description = "GitHub repository allowed to assume the deployment role."
  type        = string
  default     = "codedna-aws-reference"
}

variable "github_branch" {
  description = "GitHub branch allowed to deploy."
  type        = string
  default     = "main"
}
