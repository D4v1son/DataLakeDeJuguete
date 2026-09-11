BUCKET_NAME = "s3-demo-bucket-data-lake"
REGION = "eu-north-1"

AWS_PROFILE = "boto3-master-user"

ROLE_NAME = "AWSGlueServiceRole-crawler"

GLUE_DATABASE = "datalake_juguete"
CRAWLER_NAME = "crawler-raw-superstore-csv"

BRONZE_JOB_NAME = "job-raw-to-bronze"
RAW_TABLE_NAME = "raw"  # confirma que coincide con el nombre real que le puso el crawler
GLUE_SCRIPTS_PREFIX = "glue-scripts/"


SILVER_JOB_NAME = "job-bronze-to-silver"

RAW_PREFIX = "raw/"
BRONZE_PREFIX = "bronze/"
SILVER_PREFIX = "silver/"
GOLD_PREFIX = "gold/"

ATHENA_RESULTS_PREFIX = "athena-results/"