"""
Glue ETL Job: bronze -> silver
Lee la tabla 'bronze' del Data Catalog y aplica limpieza básica:
- Elimina filas con nulos en Sales, Quantity o Profit
- Filtra Discount fuera de rango [0, 1]
- Filtra Sales y Quantity no positivos
- Elimina duplicados exactos
Escribe el resultado en formato Parquet en la capa silver.
"""

import sys
from awsglue.utils import getResolvedOptions # type: ignore
from pyspark.context import SparkContext # type: ignore
from awsglue.context import GlueContext # type: ignore
from awsglue.job import Job # type: ignore
from pyspark.sql.functions import col

args = getResolvedOptions(sys.argv, ["JOB_NAME", "database_name", "table_name", "output_path"])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

bronze_dyf = glueContext.create_dynamic_frame.from_catalog(
    database=args["database_name"],
    table_name=args["table_name"],
)

df = bronze_dyf.toDF()

df_clean = (
    df.dropna(subset=["Sales", "Quantity", "Profit"])
    .filter((col("Discount") >= 0) & (col("Discount") <= 1))
    .filter((col("Sales") > 0) & (col("Quantity") > 0))
    .dropDuplicates()
)

from awsglue.dynamicframe import DynamicFrame # type: ignore

silver_dyf = DynamicFrame.fromDF(df_clean, glueContext, "silver_dyf")

glueContext.write_dynamic_frame.from_options(
    frame=silver_dyf,
    connection_type="s3",
    connection_options={"path": args["output_path"]},
    format="parquet",
)

job.commit()