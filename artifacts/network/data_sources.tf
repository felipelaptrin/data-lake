data "aws_availability_zones" "azs" {
  state = "available"
  filter {
    name   = "region-name"
    values = [var.aws_region]
  }

}
