import json
import os

import boto3

s3_datalake_bucket = "datalake-flat-937168356724"


def get_subnet_id_from_tfstate() -> str:
    s3 = boto3.resource("s3")
    content_object = s3.Object("terraform-states-flat", "states/datalake/network.tfstate")
    file_content = content_object.get()["Body"].read().decode("utf-8")
    json_content = json.loads(file_content)
    return json_content["outputs"]["subnet"]["value"]


def create_emr_cluster(s3_datalake_bucket: str):
    emr = boto3.client("emr", region_name="us-east-1")
    response = emr.run_job_flow(
        Name="Proccess Data",
        LogUri=f"s3://emr-logs-{s3_datalake_bucket}",
        ReleaseLabel="emr-6.5.0",
        Applications=[
            {"Name": "Hadoop"},
            {"Name": "Hive"},
            {"Name": "Spark"},
            {"Name": "JupyterHub"},
            {"Name": "JupyterEnterpriseGateway"},
        ],
        Instances={
            "Ec2SubnetId": get_subnet_id_from_tfstate(),
            "KeepJobFlowAliveWhenNoSteps": False,
            "TerminationProtected": False,
            "InstanceFleets": [
                {
                    "Name": "Master Node",
                    "InstanceFleetType": "MASTER",
                    "TargetSpotCapacity": 1,
                    "InstanceTypeConfigs": [
                        {
                            "InstanceType": "m4.xlarge",
                            "WeightedCapacity": 1,
                            "BidPriceAsPercentageOfOnDemandPrice": 80,
                        },
                        {
                            "InstanceType": "m5.xlarge",
                            "WeightedCapacity": 1,
                            "BidPriceAsPercentageOfOnDemandPrice": 80,
                        },
                    ],
                },
                {
                    "Name": "Slaves Node",
                    "InstanceFleetType": "CORE",
                    "TargetSpotCapacity": 1,
                    "InstanceTypeConfigs": [
                        {
                            "InstanceType": "m4.xlarge",
                            "WeightedCapacity": 1,
                            "BidPriceAsPercentageOfOnDemandPrice": 80,
                        },
                        {
                            "InstanceType": "m5.xlarge",
                            "WeightedCapacity": 1,
                            "BidPriceAsPercentageOfOnDemandPrice": 80,
                        },
                    ],
                },
            ],
        },
        ServiceRole="EMR_SERVICE_ROLE",
        JobFlowRole="EMR_EC2_ROLE",
        Tags=[
            {"Key": "Environment", "Value": "Dev"},
            {"Key": "CreatedVia", "Value": "Boto3"},
        ],
    )
    return response["JobFlowId"]


def move_script_to_s3(s3_datalake_bucket: str) -> str:
    s3 = boto3.resource("s3")
    bucket_name = s3_datalake_bucket
    key = "scripts/spark_processed.py"
    current_file_path = os.path.dirname(os.path.realpath(__file__))

    s3.meta.client.upload_file(
        Filename=f"{current_file_path}/spark_processed.py",
        Bucket=bucket_name,
        Key=key,
    )
    return f"s3://{bucket_name}/{key}"


def process_data(job_flow_id: str, script_s3_path: str, s3_datalake_bucket: str):
    emr = boto3.client("emr", region_name="us-east-1")
    emr.add_job_flow_steps(
        JobFlowId=job_flow_id,
        Steps=[
            {
                "Name": "PROCESS DATA",
                "ActionOnFailure": "TERMINATE_CLUSTER",
                "HadoopJarStep": {
                    "Jar": "command-runner.jar",
                    "Args": [
                        "spark-submit",
                        "--deploy-mode",
                        "cluster",
                        script_s3_path,
                        s3_datalake_bucket,
                    ],
                },
            }
        ],
    )


def create_crawler(name: str, s3_datalake_bucket: str):
    glue = boto3.client("glue", region_name="us-east-1")
    glue.create_crawler(
        Name=name,
        Role="Glue_Crawler_Role",
        DatabaseName="processed",
        Description="This crawler is used to create metadata",
        Targets={
            "S3Targets": [
                {
                    "Path": f"s3://{s3_datalake_bucket}/consumer-zone",
                },
            ],
        },
        Tags={"CreatedVia": "Boto3", "Environment": "Dev"},
        Schedule="cron(0 10 * * ? *)",
    )


# PIPELINE
script_s3_path = move_script_to_s3(s3_datalake_bucket)
job_flow_id = create_emr_cluster(s3_datalake_bucket)
process_data(job_flow_id, script_s3_path, s3_datalake_bucket)
create_crawler("CRAWLER - PROCESSED", s3_datalake_bucket)
