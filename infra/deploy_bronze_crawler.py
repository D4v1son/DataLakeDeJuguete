
"""
Crea (si no existe) y ejecuta el Glue Crawler sobre la capa bronze/ del bucket.
Requiere que el Glue Job raw_to_bronze ya se haya ejecutado (archivos
parquet ya deben existir en bronze/).
"""

import sys
import os
import time

import boto3
from botocore.exceptions import ClientError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

session = boto3.Session(profile_name=config.AWS_PROFILE)
iam = session.client("iam")
glue = session.client("glue", region_name=config.REGION)


def get_role_arn():
    role = iam.get_role(RoleName=config.ROLE_NAME)
    return role["Role"]["Arn"]


def ensure_crawler(role_arn):
    s3_path = f"s3://{config.BUCKET_NAME}/{config.BRONZE_PREFIX}"
    crawler_config = {
        "Role": role_arn,
        "DatabaseName": config.GLUE_DATABASE,
        "Targets": {"S3Targets": [{"Path": s3_path}]},
    }
    try:
        glue.get_crawler(Name=config.BRONZE_CRAWLER_NAME)
        print(f"[ACTUALIZANDO] Crawler existente con la config actual: {config.BRONZE_CRAWLER_NAME}")
        glue.update_crawler(Name=config.BRONZE_CRAWLER_NAME, **crawler_config)
    except ClientError:
        print(f"[CREANDO] Crawler: {config.BRONZE_CRAWLER_NAME}")
        glue.create_crawler(Name=config.BRONZE_CRAWLER_NAME, **crawler_config)
        print("[OK] Crawler creado")


def run_crawler():
    print(f"[EJECUTANDO] Crawler: {config.BRONZE_CRAWLER_NAME}")
    try:
        glue.start_crawler(Name=config.BRONZE_CRAWLER_NAME)
    except ClientError as e:
        if "CrawlerRunningException" in str(e):
            print("[INFO] El crawler ya está en ejecución")
        else:
            raise

    while True:
        state = glue.get_crawler(Name=config.BRONZE_CRAWLER_NAME)["Crawler"]["State"]
        print(f"   Estado: {state}")
        if state == "READY":
            break
        time.sleep(10)
    print("[OK] Crawler finalizado")


if __name__ == "__main__":
    role_arn = get_role_arn()
    ensure_crawler(role_arn)
    run_crawler()
    print(f"\n[LISTO] Revisa la tabla en Glue > Data Catalog > {config.GLUE_DATABASE} > Tables")