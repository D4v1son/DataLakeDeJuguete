
# ¿Qué es el Data Lake de Juguete?

Este es un repositorio cuya finalidad es aprender más sobre data lakes, en particular cómo levantar uno mediante los servicios en la nube de Amazon. La escala del data lake propuesto es increíblemente pequeño, de ahí el apodo "de juguete", y carece de aplicación real. Por tanto, sirve como ejemplo de la estructura básica que debería tener un data lake realmente funcional.

# Arquitectura

```mermaid
flowchart LR
    A[CSV local] -->|boto3 upload_raw.py| B[S3: raw/]
    B -->|Glue Crawler| C[(Glue Data Catalog: raw)]
    C -->|Glue Job: raw_to_bronze| D[S3: bronze/ Parquet]
    D -->|Glue Crawler| E[(Glue Data Catalog: bronze)]
    E -->|Glue Job: bronze_to_silver limpieza| F[S3: silver/ Parquet]
    F -->|Glue Crawler| G[(Glue Data Catalog: silver)]
    G -->|Athena CTAS agregación| H[S3: gold/ particionado por Region]
    H -->|Consultas SQL| I[Athena Query Editor]
```

# Créditos/Licencias

- [Sample Superstore Dataset](https://www.kaggle.com/datasets/bravehart101/sample-supermarket-dataset), CC0: Public Domain

