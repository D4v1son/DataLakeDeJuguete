"""
Sube el script raw_to_bronze.py a S3, crea (o actualiza) el Glue Job
correspondiente y lo ejecuta, esperando a que termine.
"""

import sys
import os
import time

import boto3
from botocore.exceptions import ClientError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

session = boto3.Session(profile_name=config.AWS_PROFILE)
s3 = session.client("s3", region_name=config.REGION)
iam = session.client("iam")
glue = session.client("glue", region_name=config.REGION)

LOCAL_SCRIPT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "raw_to_bronze.py"
)
SCRIPT_S3_KEY = f"{config.GLUE_SCRIPTS_PREFIX}raw_to_bronze.py"
OUTPUT_PATH = f"s3://{config.BUCKET_NAME}/{config.BRONZE_PREFIX}"


def get_role_arn():
    role = iam.get_role(RoleName=config.ROLE_NAME)
    return role["Role"]["Arn"]


def upload_script():
    print(f"[SUBIENDO] Script -> s3://{config.BUCKET_NAME}/{SCRIPT_S3_KEY}")
    s3.upload_file(LOCAL_SCRIPT_PATH, config.BUCKET_NAME, SCRIPT_S3_KEY)


def ensure_job(role_arn):
    script_location = f"s3://{config.BUCKET_NAME}/{SCRIPT_S3_KEY}"
    job_config = {
        "Role": role_arn,
        "Command": {
            "Name": "glueetl",
            "ScriptLocation": script_location,
            "PythonVersion": "3",
        },
        "DefaultArguments": {
            "--database_name": config.GLUE_DATABASE,
            "--table_name": config.RAW_TABLE_NAME,
            "--output_path": OUTPUT_PATH,
        },
        "GlueVersion": "4.0",
        "NumberOfWorkers": 2,
        "WorkerType": "G.1X",
    }
    try:
        glue.get_job(JobName=config.BRONZE_JOB_NAME)
        print(f"[ACTUALIZANDO] Job existente: {config.BRONZE_JOB_NAME}")
        glue.update_job(JobName=config.BRONZE_JOB_NAME, JobUpdate=job_config)
    except ClientError:
        print(f"[CREANDO] Job nuevo: {config.BRONZE_JOB_NAME}")
        glue.create_job(Name=config.BRONZE_JOB_NAME, **job_config)


def run_job():
    print(f"[EJECUTANDO] Job: {config.BRONZE_JOB_NAME}")
    run = glue.start_job_run(JobName=config.BRONZE_JOB_NAME)
    run_id = run["JobRunId"]

    while True:
        status = glue.get_job_run(
            JobName=config.BRONZE_JOB_NAME, RunId=run_id
        )["JobRun"]["JobRunState"]
        print(f"   Estado: {status}")
        if status in ("SUCCEEDED", "FAILED", "STOPPED", "TIMEOUT"):
            break
        time.sleep(15)

    if status != "SUCCEEDED":
        raise RuntimeError(f"El job terminó con estado: {status}")
    print("[OK] Job completado con éxito")


if __name__ == "__main__":
    role_arn = get_role_arn()
    upload_script()
    ensure_job(role_arn)
    run_job()
    print(f"\n[LISTO] Revisa los archivos en s3://{config.BUCKET_NAME}/{config.BRONZE_PREFIX}")