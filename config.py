BUCKET_NAME = "s3-demo-bucket-data-lake"
REGION = "eu-west-1"

ROLE_NAME = "AWSGlueServiceRole-crawler"

GLUE_DATABASE = "datalake_juguete"
CRAWLER_NAME = "crawler-raw-superstore-csv"

RAW_TABLE_NAME = "raw"
BRONZE_JOB_NAME = "job-raw-to-bronze"
SILVER_JOB_NAME = "job-bronze-to-silver"

RAW_PREFIX = "raw/"
BRONZE_PREFIX = "bronze/"
SILVER_PREFIX = "silver/"
GOLD_PREFIX = "gold/"

ATHENA_RESULTS_PREFIX = "athena-results/"