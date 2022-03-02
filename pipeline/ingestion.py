import boto3

s3 = boto3.resource("s3")
s3.meta.client.upload_file(
    Filename="/home/felipe/Downloads/MICRODADOS_ENEM_2019.csv",
    Bucket="datalake-flat-937168356724",
    Key="raw-data/enem2019.csv",
)
