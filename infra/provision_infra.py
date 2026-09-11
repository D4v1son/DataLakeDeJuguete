"""
Provisiona la infraestructura base del data lake:
- Bucket S3 con la estructura de prefijos raw/bronze/silver/gold
- Rol IAM para que Glue pueda leer/escribir en el bucket
- Base de datos en el Glue Data Catalog
 
Importante: si un recurso ya existe, lo detecta y no lo recrea.
"""

import json
import time
import sys
import os

import boto3
from botocore.exceptions import ClientError

# Le digo a Python dónde encontrar el archivo config con las especifiaciones de la infraestructura que vamos a crear.
# Este archivo no contiene información sensible como claves de acceso.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

session = boto3.Session(profile_name=config.AWS_PROFILE) # Este es un perffil IAM no el root user, pero tiene mucho permisos sensibles.
s3 = session.client("s3", region_name=config.REGION)
iam = session.client("iam")
glue = session.client("glue", region_name=config.REGION)

def ensure_bucket():
    try:
        s3.head_bucket(Bucket=config.BUCKET_NAME)
        print(f"[OK] Bucket ya existe: {config.BUCKET_NAME}")
    except ClientError:
        print(f"[CREANDO] Bucket: {config.BUCKET_NAME}")
        if config.REGION == "us-east-1":
            s3.create_bucket(Bucket=config.BUCKET_NAME)
        else:
            s3.create_bucket(
                Bucket=config.BUCKET_NAME,
                CreateBucketConfiguration={"LocationConstraint": config.REGION},
            )
        print("[OK] Bucket creado")
 
    for prefix in [config.RAW_PREFIX, config.BRONZE_PREFIX, config.SILVER_PREFIX, config.GOLD_PREFIX]:
        s3.put_object(Bucket=config.BUCKET_NAME, Key=prefix)
    print("[OK] Prefijos verificados/creados")
 
 
def ensure_iam_role():
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "glue.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }
    try:
        role = iam.get_role(RoleName=config.ROLE_NAME)
        print(f"[OK] Rol ya existe: {config.ROLE_NAME}")
        return role["Role"]["Arn"]
    except ClientError:
        print(f"[CREANDO] Rol IAM: {config.ROLE_NAME}")
        role = iam.create_role(
            RoleName=config.ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="Rol para que Glue lea/escriba en el data lake de juguete",
        )
        # Permisos generales de Glue + lectura/escritura en S3
        iam.attach_role_policy(
            RoleName=config.ROLE_NAME,
            PolicyArn="arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole",
        )
        iam.attach_role_policy(
            RoleName=config.ROLE_NAME,
            PolicyArn="arn:aws:iam::aws:policy/AmazonS3FullAccess",
        )
        print("[OK] Rol creado y políticas adjuntadas")
        print("Esperando propagación del rol (10s)...")
        time.sleep(10)
        return role["Role"]["Arn"]
 
 
def ensure_glue_database():
    try:
        glue.get_database(Name=config.GLUE_DATABASE)
        print(f"[OK] Base de datos Glue ya existe: {config.GLUE_DATABASE}")
    except ClientError:
        print(f"[CREANDO] Base de datos Glue: {config.GLUE_DATABASE}")
        glue.create_database(DatabaseInput={"Name": config.GLUE_DATABASE})
        print("[OK] Base de datos creada")
 
 
if __name__ == "__main__":
    ensure_bucket()
    role_arn = ensure_iam_role()
    ensure_glue_database()
    print(f"\n[LISTO] Rol ARN: {role_arn}")
    print("Guarda este ARN si vas a necesitarlo en otros scripts (o léelo con boto3 directamente).")