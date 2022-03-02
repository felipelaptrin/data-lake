resource "aws_s3_bucket" "datalake_storage" {
  bucket = var.s3_bucket_name
}

resource "aws_s3_bucket_acl" "datalake_storage" {
  bucket = aws_s3_bucket.datalake_storage.id
  acl    = "private"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "datalake_encryption" {
  bucket = aws_s3_bucket.datalake_storage.bucket

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "datalake_storage" {
  bucket = aws_s3_bucket.datalake_storage.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
