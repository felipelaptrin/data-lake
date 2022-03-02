resource "aws_vpc" "vpc" {
  cidr_block = local.vpc_cidr

  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "vpc-emr-clusters"
  }
}

resource "aws_subnet" "subnets" {
  count = 3

  vpc_id            = aws_vpc.vpc.id
  cidr_block        = "${local.vpc_first_two_octets}.${tonumber(local.vpc_third_octet) + count.index}.${local.vpc_fourth_octet}/26"
  availability_zone = data.aws_availability_zones.azs.names[count.index]

  tags = {
    Name = "public-subnet-emr-${count.index}"
  }
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.vpc.id
}

resource "aws_default_route_table" "rt" {
  default_route_table_id = aws_vpc.vpc.default_route_table_id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }

  tags = {
    Name = "default-emr-rt"
  }
}
