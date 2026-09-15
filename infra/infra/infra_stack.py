from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
    aws_iam as iam,
    aws_glue as glue,
)
from constructs import Construct

class InfraStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        env_name = self.node.try_get_context("env") or "dev"
        project = "datalake-de-juguete"
        database_name = f"{project}_{env_name}".replace("-", "_")

        # --- 1. Buckets por capa ---
        layers = ["raw", "bronze", "silver", "gold"]
        self.buckets = {}

        for layer in layers:
            bucket = s3.Bucket(
                self, f"{layer.capitalize()}Bucket",
                bucket_name=f"{project}-{layer}-{env_name}",
                versioned=True,
                block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
                removal_policy=RemovalPolicy.DESTROY,
                auto_delete_objects=True,
            )
            self.buckets[layer] = bucket

        # --- 2. Bucket dedicado a scripts/assets de Glue ---
        scripts_bucket = s3.Bucket(
            self, "ScriptsBucket",
            bucket_name=f"{project}-scripts-{env_name}",
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )
        # ⚠️ AQUÍ YA NO va el grant_read_write todavía — glue_role no existe aún

        # --- 3. Rol IAM para Glue ---
        glue_role = iam.Role(
            self, "GlueDataLakeRole",
            role_name=f"{project}-glue-role-{env_name}",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSGlueServiceRole"
                )
            ],
        )

        # --- 4. Permisos: AHORA SÍ, aquí van TODOS los grant_read_write ---
        for bucket in self.buckets.values():
            bucket.grant_read_write(glue_role)
        scripts_bucket.grant_read_write(glue_role)   # <-- esta línea va AQUÍ

        # --- 5. Base de datos Glue ---
        glue_database = glue.CfnDatabase(
            self, "DataLakeDatabase",
            catalog_id=self.account,
            database_input=glue.CfnDatabase.DatabaseInputProperty(
                name=database_name,
            ),
        )

        # --- 6. Crawlers ---
        crawler_layers = ["raw", "bronze", "silver"]
        self.crawlers = {}

        for layer in crawler_layers:
            crawler = glue.CfnCrawler(
                self, f"{layer.capitalize()}Crawler",
                name=f"{project}-{layer}-crawler-{env_name}",
                role=glue_role.role_arn,
                database_name=database_name,
                targets=glue.CfnCrawler.TargetsProperty(
                    s3_targets=[
                        glue.CfnCrawler.S3TargetProperty(
                            path=f"s3://{self.buckets[layer].bucket_name}/"
                        )
                    ]
                ),
            )
            crawler.node.add_dependency(glue_database)
            self.crawlers[layer] = crawler

        # --- 7. Glue Job: raw -> bronze ---
        bronze_job = glue.CfnJob(
            self, "RawToBronzeJob",
            name=f"{project}-raw-to-bronze-{env_name}",
            role=glue_role.role_arn,
            command=glue.CfnJob.JobCommandProperty(
                name="glueetl",
                script_location=f"s3://{scripts_bucket.bucket_name}/raw_to_bronze.py",
                python_version="3",
            ),
            default_arguments={
                "--database_name": database_name,
                "--table_name": "datalake_de_juguete_raw_dev",
                "--output_path": f"s3://{self.buckets['bronze'].bucket_name}/",
            },
            glue_version="4.0",
            number_of_workers=2,
            worker_type="G.1X",
        )