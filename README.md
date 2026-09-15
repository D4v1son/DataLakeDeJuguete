🌐 Español | [English](README.en.md)

doc version 2.1

# ¿Qué es el Data Lake de Juguete?

Este es un repositorio cuya finalidad es aprender más sobre data lakes, en particular cómo levantar uno mediante los servicios en la nube de Amazon, con la infraestructura totalmente automatizada como código (IaC). La escala del data lake propuesto es increíblemente pequeño, de ahí el apodo "de juguete", y carece de aplicación real. Por tanto, sirve como ejemplo de la estructura básica que debería tener un data lake realmente funcional.

# Arquitectura

El pipeline sigue una arquitectura por capas (medallion architecture: raw → bronze → silver → gold), donde cada capa se cataloga automáticamente antes de pasar a la siguiente. Cada capa vive en su propio bucket S3, y hay un bucket adicional dedicado a los scripts/assets que necesita Glue para ejecutar los jobs, y a los resultados de las consultas de Athena.

1. **Ingesta**: un script local (`upload_raw_csv.py`) sube el CSV de origen al bucket `raw`, sin transformar.
2. **Catalogación**: un Glue Crawler lee cada capa (raw, bronze, silver) y registra su esquema como tabla en el Glue Catalog, para que pueda consultarse por nombre en lugar de por ruta S3.
3. **Transformación (bronze)**: el Glue Job `raw_to_bronze` lee la tabla `raw` desde el catálogo y la convierte a formato Parquet en el bucket `bronze`.
4. **Limpieza (silver)**: el Glue Job `bronze_to_silver` lee `bronze`, aplica reglas de limpieza (elimina nulos, valores fuera de rango y duplicados) y escribe el resultado en el bucket `silver`.
5. **Agregación (gold)**: una consulta Athena (CTAS) agrega los datos de `silver` por categoría y región, y escribe el resultado particionado en el bucket `gold`, listo para análisis.

Toda la infraestructura persistente (buckets, rol IAM, base de datos, crawlers y Glue Jobs) se define de forma declarativa con **AWS CDK** y se despliega con `cdk deploy` — sin pasos manuales en la consola de AWS y sin scripts imperativos comprobando "si ya existe". Los scripts en `/scripts` solo se encargan de la parte de *ejecución*: subir código/datos y lanzar procesos ya definidos en la infraestructura.

```mermaid
flowchart LR
    subgraph Ingesta["Ingesta"]
        Local[Script local boto3]
    end

    subgraph S3["S3 Buckets (uno por capa + scripts)"]
        Raw[("raw")]
        Bronze[("bronze")]
        Silver[("silver")]
        Gold[("gold")]
        Scripts[("scripts")]
    end

    subgraph Compute["Procesamiento"]
        CrawlerRaw[Crawler raw]
        JobBronze[Job raw_to_bronze]
        CrawlerBronze[Crawler bronze]
        JobSilver[Job bronze_to_silver]
        CrawlerSilver[Crawler silver]
    end

    subgraph Catalog["Glue Catalog"]
        DB[(datalake_de_juguete_dev)]
    end

    subgraph AthenaGroup["Athena"]
        Athena[Athena SQL]
    end

    Local -->|sube CSV| Raw
    Scripts -.->|bronze job| JobBronze
    Scripts -.->|silver job| JobSilver
    Scripts -.->|resultados de consulta| Athena

    Raw --> CrawlerRaw
    CrawlerRaw -->|escribe| DB
    DB -->|lee| JobBronze
    JobBronze --> Bronze

    Bronze --> CrawlerBronze
    CrawlerBronze -->|escribe| DB
    DB -->|lee| JobSilver
    JobSilver --> Silver

    Silver --> CrawlerSilver
    CrawlerSilver -->|escribe| DB
    DB -->|lee| Athena
    Athena -->|CTAS| Gold

    classDef s3style fill:#FFE8CC,stroke:#D9822B,stroke-width:1.5px,color:#5C3A00
    classDef catalogstyle fill:#D6E8FF,stroke:#2B6CB0,stroke-width:1.5px,color:#1A365D
    classDef computestyle fill:#E3F9E5,stroke:#2F855A,stroke-width:1.5px,color:#1C4532
    classDef ingestastyle fill:#F3E8FF,stroke:#805AD5,stroke-width:1.5px,color:#44337A

    class Raw,Bronze,Silver,Gold,Scripts s3style
    class DB catalogstyle
    class CrawlerRaw,JobBronze,CrawlerBronze,JobSilver,CrawlerSilver,Athena computestyle
    class Local ingestastyle

    style Ingesta fill:transparent,stroke:#805AD5,stroke-width:2px,color:#ffffff,font-weight:bold
    style S3 fill:transparent,stroke:#D9822B,stroke-width:2px,color:#ffffff,font-weight:bold
    style Compute fill:transparent,stroke:#2F855A,stroke-width:2px,color:#ffffff,font-weight:bold
    style Catalog fill:transparent,stroke:#2B6CB0,stroke-width:2px,color:#ffffff,font-weight:bold
    style AthenaGroup fill:transparent,stroke:#2F855A,stroke-width:2px,color:#ffffff,font-weight:bold
```

# Servicios AWS

- [S3](https://aws.amazon.com/es/s3/), almacenamiento por capas de nuestros datos (un bucket por capa, más uno para scripts/assets).
- [Glue](https://aws.amazon.com/es/glue/), catálogo de datos (tablas por capas), crawlers y jobs ETL.
- [Athena](https://aws.amazon.com/es/athena/), consultas SQL (serverless).
- [IAM](https://aws.amazon.com/es/iam/), control de permisos y perfiles de trabajo.
- [CDK](https://aws.amazon.com/es/cdk/), definición de la infraestructura como código (Python).

# Estructura del Repositorio
```
DataLakeDeJuguete/
├── data/
│ └── SampleSuperstore.csv       # Dataset de ejemplo (Sample Superstore)
├── infra/                       # Proyecto CDK (infraestructura como código)
│ ├── infra/
│ │ └── infra_stack.py           # Buckets S3 (incl. scripts), rol IAM, base de datos Glue, crawlers y Glue Jobs
│ ├── app.py                     # Punto de entrada de la app CDK
│ ├── cdk.json
│ └── requirements.txt
├── glue_jobs/
│ ├── raw_to_bronze.py           # Script PySpark: raw (CSV) -> bronze (Parquet)
│ └── bronze_to_silver.py        # Script PySpark: bronze -> silver (limpieza)
├── scripts/
│ ├── upload_raw_csv.py          # Sube el CSV local a S3 (bucket raw)
│ ├── run_crawlers.py            # Lanza uno o varios crawlers y espera a que terminen
│ ├── deploy_bronze_job.py       # Sube raw_to_bronze.py al bucket scripts y ejecuta el Job
│ ├── deploy_silver_job.py       # Sube bronze_to_silver.py al bucket scripts y ejecuta el Job
│ └── generate_gold_table.py     # CTAS de Athena: agrega silver -> gold, particionado por Region
├── config.py                    # Nombres de recursos compartidos (deben coincidir con infra_stack.py)
├── requirements.txt
├── .gitignore
└── README.md
```

**Por qué esta separación:**
- **`infra/`** es un proyecto CDK autocontenido (con su propio entorno virtual y dependencias) que declara toda la infraestructura persistente: buckets, rol, catálogo, crawlers y Glue Jobs. No contiene lógica de ejecución, solo definición del estado deseado.
- **`glue_jobs/`** contiene únicamente los scripts PySpark que ejecuta AWS Glue en la nube (no se ejecutan en tu máquina). Su creación y configuración como recursos ya vive en `infra_stack.py`.
- **`scripts/`** son utilidades de ejecución: suben datos y código a S3, y lanzan procesos (crawlers, jobs, consultas Athena) que la infraestructura ya tiene definidos.
- **`config.py`** centraliza los nombres de recursos (buckets, base de datos, crawlers, jobs) para que los scripts de ejecución no dupliquen esos valores. Debe mantenerse en sincronía con los nombres generados en `infra_stack.py`.

# Cómo Ejecutarlo

### Requisitos

- Cuenta de AWS con un usuario IAM configurado localmente (perfil en `~/.aws/credentials`, gestionado aquí con la extensión AWS Toolkit para VS Code).
- El usuario IAM necesita permisos sobre S3, IAM (crear roles), Glue y Athena.
- Python 3.9+ instalado.
- Node.js instalado (necesario para la CLI de AWS CDK).

### Instalación

```bash
# Entorno del proyecto de datos (raíz del repo)
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# CLI de CDK (una sola vez por máquina)
npm install -g aws-cdk

# Entorno del proyecto CDK
cd infra
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Orden de ejecución

La primera vez, en una cuenta/región nueva, hay que hacer bootstrap de CDK:

```bash
cd infra
cdk bootstrap aws://TU_CUENTA/TU_REGION
```

A partir de ahí, el flujo es:

```bash
# 1. Despliega toda la infraestructura (buckets, rol, base de datos, crawlers, Glue Jobs)
cd infra
cdk deploy

# 2. Sube el CSV de origen al bucket raw
python scripts\upload_raw_csv.py

# 3. Cataloga raw
python scripts\run_crawlers.py raw

# 4. Transforma raw -> bronze (Parquet)
python scripts\deploy_bronze_job.py

# 5. Cataloga bronze
python scripts\run_crawlers.py bronze

# 6. Limpia bronze -> silver
python scripts\deploy_silver_job.py

# 7. Cataloga silver
python scripts\run_crawlers.py silver

# 8. Agrega silver -> gold (particionado por Region)
python scripts\generate_gold_table.py
```

Para revisar cambios en la infraestructura antes de aplicarlos, usa `cdk diff` en vez de `cdk deploy` directamente.

# Dataset y Configuración

Este proyecto usa el dataset público **Sample Superstore** como ejemplo para validar el pipeline.

Los nombres de recursos (buckets, base de datos, crawlers, jobs) se generan a partir del nombre del proyecto y el entorno (`dev` por defecto), definidos en `infra_stack.py` y reflejados en `config.py`. Para reproducir este proyecto con otra cuenta de AWS o con un dataset distinto:

1. Ajustar el nombre del proyecto/entorno en `infra_stack.py` (y actualizar `config.py` en consecuencia) si hace falta.
2. Sustituir el CSV en `data/` por el dataset deseado.
3. Ajustar la consulta de agregación en `scripts/generate_gold_table.py` si las columnas del nuevo dataset difieren de las de Superstore.

# Notas

Como se ha mencionado anteriormente, este es un proyecto de investigación y deja mucho que desear como data lake propiamente dicho. Una versión *real* tendrá datos que posiblemente se tengan que actualizar con frecuencia, muchos más requisitos de seguridad, y separación de entornos (dev/pre/pro) mediante contextos de CDK.

# Créditos/Licencias

- [Sample Superstore Dataset](https://www.kaggle.com/datasets/bravehart101/sample-supermarket-dataset), CC0: Public Domain