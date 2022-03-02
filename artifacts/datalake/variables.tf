variable "s3_bucket_name" {
  description = "Name of the the s3 bucket that will be your datalake"
  type        = string
  default     = "datalake-flat-937168356724"
}

variable "aws_region" {
  description = "AWS region name"
  type        = string
  default     = "us-east-1"
}
