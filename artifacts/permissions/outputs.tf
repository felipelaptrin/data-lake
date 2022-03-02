output "emr_ec2_role" {
  value = aws_iam_role.emr_ec2_policy.name
}

output "emr_service_role" {
  value = aws_iam_role.emr_service_policy.name
}
