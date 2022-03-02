import os

import boto3

from utils import get_bucket_name_from_terraform


def get_download_folder() -> str:
    home_and_user = os.popen("echo ~").read()
    home_and_user = home_and_user.strip()
    return home_and_user + "/Downloads"


s3 = boto3.resource("s3")
s3.meta.client.upload_file(
    Filename=f"{get_download_folder()}/MICRODADOS_ENEM_2019.csv",
    Bucket=get_bucket_name_from_terraform(),
    Key="raw-data/enem2019.csv",
)
