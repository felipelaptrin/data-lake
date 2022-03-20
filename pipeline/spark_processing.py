import pyspark.sql.functions as SF
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame

import sys

spark = SparkSession.builder.appName("Spark Processing").getOrCreate()

### PARAMETERS
s3_input_path = sys.argv[1]
s3_output_path = sys.argv[2]


### FUNCTIONS
def get_standardize_column_name(column_name: str) -> str:
    column_name = column_name.lower()
    replacement = {
        "a": ["á", "à", "ã", "â"],
        "e": ["é", "è", "ẽ", "ê"],
        "i": ["í", "ì", "ĩ", "î"],
        "o": ["ó", "ò", "õ", "ô"],
        "u": ["ú", "ù", "ũ", "û"],
        "c": ["ç"],
        "_": [" ", "(", ")", "/"],
    }
    for new_char, old_char_list in replacement.items():
        for old_char in old_char_list:
            column_name = column_name.replace(old_char, new_char)
    return column_name


def standardize_headers(df: DataFrame):
    for column_name in df.columns:
        df = df.withColumnRenamed(column_name, get_standardize_column_name(column_name))
    return df


def create_uf_column(df: DataFrame):
    df = df.withColumn("uf", df["municipio"].cast("string").substr(1, 2).cast("int"))
    return df

def cast_columns(df: DataFrame):
    for column in df.columns:
        if "remun" not in column:
            continue
        df = df.withColumn(column, SF.regexp_replace(column, ",", ".").cast("double"))
    return df


### PIPELINE
    # READ
df = (
    spark.read.option("inferSchema", "true")
    .option("delimiter", ";")
    .option("header", "true")
    .option("encoding", "latin1")
    .csv(s3_input_path)
)

    # PROCESSING
df = standardize_headers(df)
df = create_uf_column(df)
df = cast_columns(df)

    # SAVE
df.write.parquet(
    s3_output_path,
    mode="append",
    partitionBy="uf",
)