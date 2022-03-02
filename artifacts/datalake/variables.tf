variable "s3_bucket_name" {
  description = "Name of the the s3 bucket"
  type        = string
  nullable    = false
}

variable "aws_region" {
  description = "AWS region name"
  type        = string
  default     = "us-east-1"
}
