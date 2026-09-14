
# ¿Qué es el Data Lake de Juguete?

Este es un repositorio cuya finalidad es aprender más sobre data lakes, en particular cómo levantar uno mediante los servicios en la nube de Amazon. La escala del data lake propuesto es increíblemente pequeño, de ahí el apodo "de juguete", y carece de aplicación real. Por tanto, sirve como ejemplo de la estructura básica que debería tener un data lake realmente funcional.

# Arquitectura

```mermaid
flowchart LR
    subgraph Ingesta["Ingesta"]
        Local[Script local boto3]
    end

    subgraph S3["S3 Bucket"]
        Raw[("raw/")]
        Bronze[("bronze/")]
        Silver[("silver/")]
        Gold[("gold/")]
    end

    subgraph Compute["Procesamiento"]
        CrawlerRaw[Crawler raw]
        JobBronze[Job raw_to_bronze]
        CrawlerBronze[Crawler bronze]
        JobSilver[Job bronze_to_silver]
        CrawlerSilver[Crawler silver]
    end

    subgraph Catalog["Glue Catalog"]
        DB[(datalake_juguete)]
    end

    subgraph AthenaGroup["Athena"]
        Athena[Athena SQL]
    end

    Local -->|sube CSV| Raw

    Raw --> CrawlerRaw
    CrawlerRaw -->|escribe tabla| DB
    DB -->|lee tabla| JobBronze
    JobBronze --> Bronze

    Bronze --> CrawlerBronze
    CrawlerBronze -->|escribe tabla| DB
    DB -->|lee tabla| JobSilver
    JobSilver --> Silver

    Silver --> CrawlerSilver
    CrawlerSilver -->|escribe tabla| DB
    DB -->|lee tabla| Athena
    Athena -->|CTAS| Gold

    classDef s3style fill:#FFE8CC,stroke:#D9822B,stroke-width:1.5px,color:#5C3A00
    classDef catalogstyle fill:#D6E8FF,stroke:#2B6CB0,stroke-width:1.5px,color:#1A365D
    classDef computestyle fill:#E3F9E5,stroke:#2F855A,stroke-width:1.5px,color:#1C4532
    classDef ingestastyle fill:#F3E8FF,stroke:#805AD5,stroke-width:1.5px,color:#44337A

    class Raw,Bronze,Silver,Gold s3style
    class DB catalogstyle
    class CrawlerRaw,JobBronze,CrawlerBronze,JobSilver,CrawlerSilver,Athena computestyle
    class Local ingestastyle

    style Ingesta fill:transparent,stroke:#805AD5,stroke-width:2px,color:#ffffff,font-weight:bold
    style S3 fill:transparent,stroke:#D9822B,stroke-width:2px,color:#ffffff,font-weight:bold
    style Compute fill:transparent,stroke:#2F855A,stroke-width:2px,color:#ffffff,font-weight:bold
    style Catalog fill:transparent,stroke:#2B6CB0,stroke-width:2px,color:#ffffff,font-weight:bold
    style AthenaGroup fill:transparent,stroke:#2F855A,stroke-width:2px,color:#ffffff,font-weight:bold
```

# Créditos/Licencias

- [Sample Superstore Dataset](https://www.kaggle.com/datasets/bravehart101/sample-supermarket-dataset), CC0: Public Domain

