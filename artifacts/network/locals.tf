locals {
  vpc_mask             = 16
  vpc_cidr             = "${var.network_ip}/${local.vpc_mask}"
  vpc_first_two_octets = join(".", slice(split(".", var.network_ip), 0, 2))
  vpc_third_octet      = element(split(".", var.network_ip), 2)
  vpc_fourth_octet     = element(split(".", var.network_ip), 3)
}
