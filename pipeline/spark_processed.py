import sys

from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Spark Processing").getOrCreate()

# PARAMETERS
bucket_name = sys.argv[1]
# PIPELINE
df = spark.read.options(
    delimiter=";",
    inferSchema=True,
    header=True,
).csv(f"s3://{bucket_name}/raw-data/enem2019.csv")

df = df.write.mode("append").parquet("s3://datalake-flat-937168356724/consumer-zone/enem")
