resource "aws_iam_role" "emr_ec2_policy" {
  name        = "EMR_EC2_ROLE_2"
  description = "This IAM Role is used by the EC2 instances used in a EMR Cluster"
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AmazonElasticMapReduceforEC2Role",
    "arn:aws:iam::aws:policy/AmazonS3FullAccess"
  ]
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ec2.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_instance_profile" "emr_ec2_instance_profile" {
  name = "EMR_EC2_ROLE_2"
  role = aws_iam_role.emr_ec2_policy.name
}

resource "aws_iam_role" "emr_service_policy" {
  name                = "EMR_SERVICE_ROLE_2"
  description         = "This IAM Role is used as a service Role for EMR service"
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AmazonElasticMapReduceRole"]
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "elasticmapreduce.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
}
