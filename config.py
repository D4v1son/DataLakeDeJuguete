"""
Configuración centralizada para los scripts en /scripts y /glue_jobs.
 
IMPORTANTE: estos valores deben coincidir con los definidos en
infra/infra/infra_stack.py. Si cambias el nombre del proyecto o el
entorno ahí, actualízalo también aquí.
"""

REGION = "eu-north-1"
PROJECT = "datalake-de-juguete"
ENV_NAME = "dev"

# Nombres derivados (mismo patrón que en infra_stack.py)
GLUE_DATABASE = f"{PROJECT}_{ENV_NAME}".replace("-", "_")

BUCKETS = {
    "raw": f"{PROJECT}-raw-{ENV_NAME}",
    "bronze": f"{PROJECT}-bronze-{ENV_NAME}",
    "silver": f"{PROJECT}-silver-{ENV_NAME}",
    "gold": f"{PROJECT}-gold-{ENV_NAME}",
    "scripts": f"{PROJECT}-scripts-{ENV_NAME}",
}

CRAWLERS = {
    "raw": f"{PROJECT}-raw-crawler-{ENV_NAME}",
    "bronze": f"{PROJECT}-bronze-crawler-{ENV_NAME}",
    "silver": f"{PROJECT}-silver-crawler-{ENV_NAME}",
}

JOBS = {
    "raw_to_bronze": f"{PROJECT}-raw-to-bronze-{ENV_NAME}",
}



"""
Versión antigua (falta region)

BUCKET_NAME = "s3-demo-bucket-data-lake"

AWS_PROFILE = "boto3-master-user"

ROLE_NAME = "AWSGlueServiceRole-crawler"

GLUE_DATABASE = "datalake_juguete"
CRAWLER_NAME = "crawler-raw-superstore-csv"

BRONZE_JOB_NAME = "job-raw-to-bronze"
RAW_TABLE_NAME = "raw"  # confirma que coincide con el nombre real que le puso el crawler
GLUE_SCRIPTS_PREFIX = "glue-scripts/"
BRONZE_CRAWLER_NAME = "crawler-bronze-superstore"

SILVER_JOB_NAME = "job-bronze-to-silver"
SILVER_CRAWLER_NAME = "crawler-silver-superstore"

RAW_PREFIX = "raw/"
BRONZE_PREFIX = "bronze/"
SILVER_PREFIX = "silver/"
GOLD_PREFIX = "gold/"

ATHENA_RESULTS_PREFIX = "athena-results/"
"""
