terraform {
  required_version = "~> 1.1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.2.0"
    }
  }

  backend "s3" {
    bucket = "terraform-states-flat"
    key    = "states/dataleke/datalake.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Environment = "Dev"
      CreatedVia  = "Terraform"
    }
  }
}
