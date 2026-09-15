"""
Sube el CSV de origen a la capa raw del data lake.
Usa las credenciales por defecto de AWS.
"""

import sys
import os
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

LOCAL_FILE = Path(__file__).parent.parent / "data" / "SampleSuperstore.csv"
S3_KEY = "SampleSuperstore.csv"

session = boto3.Session()
s3 = session.client("s3", region_name=config.REGION)


def upload_file():
    if not LOCAL_FILE.exists():
        print(f"[ERROR] No se encuentra el archivo: {LOCAL_FILE}")
        sys.exit(1)

    bucket_name = config.BUCKETS["raw"]
    print(f"[SUBIENDO] {LOCAL_FILE.name} -> s3://{bucket_name}/{S3_KEY}")
    try:
        s3.upload_file(str(LOCAL_FILE), bucket_name, S3_KEY)
        print("[OK] Archivo subido correctamente")
    except ClientError as e:
        print(f"[ERROR] No se pudo subir el archivo: {e}")
        sys.exit(1)


if __name__ == "__main__":
    upload_file()