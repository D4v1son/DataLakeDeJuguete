"""
Lanza uno o varios Glue Crawlers y espera a que terminen.
Se ejecuta DESPUÉS de 'cdk deploy' (la infraestructura ya debe existir).

Uso:
    python scripts/run_crawlers.py raw bronze silver
    python scripts/run_crawlers.py bronze
"""

import sys
import time
import os

import boto3
from botocore.exceptions import ClientError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

session = boto3.Session()
glue = session.client("glue", region_name=config.REGION)


def run_crawler(layer: str):
    crawler_name = config.CRAWLERS[layer]

    print(f"[EJECUTANDO] Crawler: {crawler_name}")
    try:
        glue.start_crawler(Name=crawler_name)
    except ClientError as e:
        if "CrawlerRunningException" in str(e):
            print("[INFO] El crawler ya está en ejecución")
        else:
            raise

    while True:
        state = glue.get_crawler(Name=crawler_name)["Crawler"]["State"]
        print(f"   Estado: {state}")
        if state == "READY":
            break
        time.sleep(10)

    print(f"[OK] Crawler {crawler_name} finalizado\n")


if __name__ == "__main__":
    layers = sys.argv[1:] or ["raw", "bronze", "silver"]

    for layer in layers:
        run_crawler(layer)

    print("[LISTO] Todos los crawlers finalizados. Revisa Glue > Data Catalog.")