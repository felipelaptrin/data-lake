variable "network_ip" {
  description = "CIDR block of the Network"
  type        = string
  default     = "172.20.0.0"
}

variable "aws_region" {
  description = "The name of the aws_region"
  type        = string
  default     = "us-east-1"
}
