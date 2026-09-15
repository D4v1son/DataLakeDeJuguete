"""
Sube raw_to_bronze.py al bucket de scripts, lanza el Glue Job
'raw_to_bronze' y espera a que termine.
Requiere que 'cdk deploy' ya haya creado el Job.
"""

import sys
import os
import time

import boto3
from botocore.exceptions import ClientError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

session = boto3.Session()
s3 = session.client("s3", region_name=config.REGION)
glue = session.client("glue", region_name=config.REGION)

LOCAL_SCRIPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw_to_bronze.py")
SCRIPT_S3_KEY = "raw_to_bronze.py"


def upload_script():
    bucket = config.BUCKETS["scripts"]
    print(f"[SUBIENDO] Script -> s3://{bucket}/{SCRIPT_S3_KEY}")
    s3.upload_file(LOCAL_SCRIPT_PATH, bucket, SCRIPT_S3_KEY)


def run_job():
    job_name = config.JOBS["raw_to_bronze"]
    print(f"[EJECUTANDO] Job: {job_name}")
    run = glue.start_job_run(JobName=job_name)
    run_id = run["JobRunId"]

    while True:
        status = glue.get_job_run(JobName=job_name, RunId=run_id)["JobRun"]["JobRunState"]
        print(f"   Estado: {status}")
        if status in ("SUCCEEDED", "FAILED", "STOPPED", "TIMEOUT"):
            break
        time.sleep(15)

    if status != "SUCCEEDED":
        raise RuntimeError(f"El job terminó con estado: {status}")
    print("[OK] Job completado con éxito")


if __name__ == "__main__":
    upload_script()
    run_job()
    print(f"\n[LISTO] Revisa los archivos en s3://{config.BUCKETS['bronze']}/")