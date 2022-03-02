import os


def get_bucket_name_from_terraform() -> str:
    bucket_name = os.popen(
        "echo $(terraform output -state=./artifacts/datalake/terraform.tfstate s3_bucket_name)"
    ).read()
    bucket_name_without_quotes = bucket_name.strip()[1:-1]
    return bucket_name_without_quotes
