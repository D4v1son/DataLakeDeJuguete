"""
Glue ETL Job: raw -> bronze
Lee la tabla 'raw' del Data Catalog y la escribe en formato Parquet
en la capa bronze del bucket S3. Este script lo ejecuta AWS Glue,
no tu máquina local.
"""

import sys
from awsglue.utils import getResolvedOptions # type: ignore
from pyspark.context import SparkContext # type: ignore
from awsglue.context import GlueContext # type: ignore
from awsglue.job import Job # type: ignore

args = getResolvedOptions(sys.argv, ["JOB_NAME", "database_name", "table_name", "output_path"])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

raw_dyf = glueContext.create_dynamic_frame.from_catalog(
    database=args["database_name"],
    table_name=args["table_name"],
)

glueContext.write_dynamic_frame.from_options(
    frame=raw_dyf,
    connection_type="s3",
    connection_options={"path": args["output_path"]},
    format="parquet",
)

job.commit()