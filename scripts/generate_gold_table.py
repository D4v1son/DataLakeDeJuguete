"""
Ejecuta una consulta Athena CTAS (CREATE TABLE AS SELECT) que agrega
la tabla silver por Region y Category, y guarda el resultado particionado
por Region en el bucket gold.
"""

import sys
import os
import time

import boto3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

session = boto3.Session()
athena = session.client("athena", region_name=config.REGION)
s3 = session.client("s3", region_name=config.REGION)

SILVER_TABLE_NAME = "datalake_de_juguete_silver_dev"
GOLD_OUTPUT_PATH = f"s3://{config.BUCKETS['gold']}/"

CTAS_QUERY = f"""
CREATE TABLE {config.GLUE_DATABASE}.{config.GOLD_TABLE_NAME}
WITH (
    format = 'PARQUET',
    external_location = '{GOLD_OUTPUT_PATH}',
    partitioned_by = ARRAY['region']
) AS
SELECT
    category,
    "sub-category" AS sub_category,
    segment,
    SUM(sales) AS total_sales,
    SUM(profit) AS total_profit,
    SUM(quantity) AS total_quantity,
    COUNT(*) AS num_orders,
    region
FROM {config.GLUE_DATABASE}.{SILVER_TABLE_NAME}
GROUP BY category, "sub-category", segment, region
"""


def run_query(query, description):
    print(f"[EJECUTANDO] {description}")
    response = athena.start_query_execution(
        QueryString=query,
        ResultConfiguration={"OutputLocation": config.ATHENA_RESULTS_PATH},
    )
    execution_id = response["QueryExecutionId"]

    while True:
        result = athena.get_query_execution(QueryExecutionId=execution_id)
        state = result["QueryExecution"]["Status"]["State"]
        print(f"   Estado: {state}")
        if state in ("SUCCEEDED", "FAILED", "CANCELLED"):
            break
        time.sleep(5)

    if state != "SUCCEEDED":
        reason = result["QueryExecution"]["Status"].get("StateChangeReason", "Sin detalle")
        raise RuntimeError(f"Consulta fallida: {state}\nMotivo: {reason}")
    print("[OK] Consulta completada")
    return execution_id


def empty_gold_bucket():
    bucket = config.BUCKETS["gold"]
    print(f"[LIMPIANDO] Objetos existentes en s3://{bucket}/")
    paginator = s3.get_paginator("list_objects_v2")
    keys_to_delete = []
    for page in paginator.paginate(Bucket=bucket):
        for obj in page.get("Contents", []):
            keys_to_delete.append({"Key": obj["Key"]})

    if not keys_to_delete:
        print("[OK] No había nada que limpiar")
        return

    for i in range(0, len(keys_to_delete), 1000):
        batch = keys_to_delete[i : i + 1000]
        s3.delete_objects(Bucket=bucket, Delete={"Objects": batch})
    print(f"[OK] {len(keys_to_delete)} objeto(s) eliminado(s)")


if __name__ == "__main__":
    empty_gold_bucket()

    try:
        run_query(
            f"DROP TABLE IF EXISTS {config.GLUE_DATABASE}.{config.GOLD_TABLE_NAME}",
            "Eliminando tabla gold anterior (si existía)",
        )
    except RuntimeError:
        pass

    run_query(CTAS_QUERY, "Creando tabla gold agregada y particionada por Region")
    print(f"\n[LISTO] Tabla '{config.GOLD_TABLE_NAME}' creada en {config.GLUE_DATABASE}")
    print(f"Archivos en: {GOLD_OUTPUT_PATH}")