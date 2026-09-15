"""
Crea (si no existe) y ejecuta el Glue Crawler sobre la capa raw/ del bucket.
Requiere que provision_infra.py se haya ejecutado antes (bucket, rol y
base de datos ya deben existir).
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
    s3_path = f"s3://{config.BUCKET_NAME}/{config.RAW_PREFIX}"
    try:
        glue.get_crawler(Name=config.CRAWLER_NAME)
        print(f"[OK] Crawler ya existe: {config.CRAWLER_NAME}")
    except ClientError:
        print(f"[CREANDO] Crawler: {config.CRAWLER_NAME}")
        glue.create_crawler(
            Name=config.CRAWLER_NAME,
            Role=role_arn,
            DatabaseName=config.GLUE_DATABASE,
            Targets={"S3Targets": [{"Path": s3_path}]},
        )
        print("[OK] Crawler creado")
 
 
def run_crawler():
    print(f"[EJECUTANDO] Crawler: {config.CRAWLER_NAME}")
    try:
        glue.start_crawler(Name=config.CRAWLER_NAME)
    except ClientError as e:
        if "CrawlerRunningException" in str(e):
            print("[INFO] El crawler ya está en ejecución")
        else:
            raise
 
    while True:
        state = glue.get_crawler(Name=config.CRAWLER_NAME)["Crawler"]["State"]
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