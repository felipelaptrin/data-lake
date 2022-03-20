# Data Lake

## Description
This project aims to create a simple Data Lake using AWS infrastructure, composed of S3 and Glue Data Catalog. The dataset used was the [RAIS](http://pdet.mte.gov.br/microdados-rais-e-caged) dataset from 2020. Data were extracted manually from the FTP server and uploaded to the RAW part of the Data Lake.

To achieve this goal, the project targets three main topics: 
- IaaC

    Instead of building the infrastructure and interacting with AWS services using the console, the entire infrastructure of this project was built using Terraform as a tool to implement and control the deployed infrastructure. All artifacts reside inside the `/artifacts` folder.

- Data processing

    All data processing was made by using Spark inside EMR clusters. To guarantee a low cost (since this is a proof of concept project) a pool of spot instances were used. The dataset used was saved in a columnar format (Parquet) with snappy compression algorithm.

- CI/CD
    
    To guarantee a better approach by using good devops practices two workflows were created by using Github Actions. Pushes made into the `develop` branch validate the Terraform artifacts while pushes made into the `main` branch apply the artifacts.

## Architecture

The Terraform artifacts created are responsible for creating the following items:
- S3
    - Data Lake bucket
- IAM
    - IAM Role for EMR EC2 instances
    - IAM Service Role for EMR
- VPC
    - VPC
    - Subnets
    - Internet Gateway
    - Route table

<p align="center">
  <img src="https://user-images.githubusercontent.com/52676348/156426895-c0212a0f-a36d-4a16-be2f-cb23837d8482.png" />
</p>

Some other resources were created by using AWS SDK for Python (Boto3):
- EMR
    - Cluster for processing the data
- Glue Crawler
    - Crawler for populate Glue Catalog


## Data Flow

The picture below ilustrates the data flow of the Data Lake.

<p align="center">
  <img src="https://user-images.githubusercontent.com/52676348/156427525-3a8985fe-6f95-41a8-83b3-d23d64b19ef3.png" />
</p>

1) The developer uses the AWS SDK (in our case Boto3) to interact with AWS and upload the dataset.
2) The dataset is uploaded to the S3 bucket that holds the data of our Data Lake (to the RAW layer - as a CSV).
3) An EMR cluster is created to process the raw data by using Spark and for saving the processed data into a staging zone in a Parquet format.
4) A Glue Crawler looks into the S3 bucket to see if there are new data.
5) A new table is created into the Glue Data Catalog.
6) The developer can use the Console (or SDK) to use the AWS Athena to query the data.
