import boto3

# Selecciona la sesión que usará boto3, en este caso utiliza un usuario IAM con acceso a consola y privilegios RW
# Si solo se usa una vez lo mejor es hacerlo desde conola, dentro del entorno de trabajo de pythonm de esta forma:
# $env:AWS_PROFILE="nombre-del-perfil"
session = boto3.Session(profile_name='boto3-master-user')

# Vamos a utilizar el servicio de AWS S3 Bucket, donde subiremos el archivo.
s3 = session.client('s3')

# Subimos el archivo, OJO, este código solo funciona para un archivo concreto con un path conreto
# DEBES MODIFICAR ESTO PARA OTROS ARCHIVOS
s3.upload_file('data/SampleSuperstore.csv', 'david-s3-demo-bucket-data-lake', 'raw/SampleSuperstore.csv')