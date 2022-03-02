import json
import os

import boto3

from utils import get_bucket_name_from_terraform


def get_subnet_name_from_terraform() -> str:
    subnet = os.popen(
        "echo $(terraform output -state=./artifacts/network/terraform.tfstate subnet)"
    ).read()
    subnet_without_quotes = subnet.strip()[1:-1]
    return subnet_without_quotes


def get_role_names_from_terraform() -> list:
    roles = os.popen(
        "echo $(terraform output -state=./artifacts/permissions/terraform.tfstate -json)"
    ).read()
    roles = json.loads(roles)
    return [roles["emr_service_role"]["value"], roles["emr_ec2_role"]["value"]]


def create_emr_cluster():
    emr = boto3.client("emr", region_name="us-east-1")
    response = emr.run_job_flow(
        Name="Proccess Data",
        LogUri=f"s3://emr-logs-{get_bucket_name_from_terraform()}",
        ReleaseLabel="emr-6.5.0",
        Applications=[
            {"Name": "Hadoop"},
            {"Name": "Hive"},
            {"Name": "Spark"},
            {"Name": "JupyterHub"},
            {"Name": "JupyterEnterpriseGateway"},
        ],
        Instances={
            "Ec2SubnetId": get_subnet_name_from_terraform(),
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
        ServiceRole=get_role_names_from_terraform()[0],  # "EMR_DefaultRole"
        JobFlowRole=get_role_names_from_terraform()[1],  # "EMR_EC2_DefaultRole",
        Tags=[
            {"Key": "Environment", "Value": "Dev"},
            {"Key": "CreatedVia", "Value": "Boto3"},
        ],
    )
    return response["JobFlowId"]


def move_script_to_s3():
    s3 = boto3.resource("s3")
    bucket_name = get_bucket_name_from_terraform()
    key = "scripts/spark_processed.py"
    current_file_path = os.path.dirname(os.path.realpath(__file__))

    s3.meta.client.upload_file(
        Filename=f"{current_file_path}/spark_processed.py",
        Bucket=bucket_name,
        Key=key,
    )
    return f"s3://{bucket_name}/{key}"


def process_data(job_flow_id: str, script_s3_path: str):
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
                        get_bucket_name_from_terraform(),
                    ],
                },
            }
        ],
    )


def create_crawler(name: str):
    glue = boto3.client("glue", region_name="us-east-1")
    glue.create_crawler(
        Name=name,
        Role="Glue_Crawler_Role",
        DatabaseName="processed",
        Description="This crawler is used to create metadata",
        Targets={
            "S3Targets": [
                {
                    "Path": f"s3://{get_bucket_name_from_terraform()}/consumer-zone",
                },
            ],
        },
        Tags={"CreatedVia": "Boto3", "Environment": "Dev"},
        Schedule="cron(0 10 * * ? *)",
    )


def start_crawler(name: str):
    glue = boto3.client("glue", region_name="us-east-1")
    glue.start_crawler(Name=name)


script_s3_path = move_script_to_s3()
job_flow_id = create_emr_cluster()
process_data(job_flow_id, script_s3_path)
create_crawler("CRAWLER - PROCESSED")
# start_crawler("CRAWLER - PROCESSED")
