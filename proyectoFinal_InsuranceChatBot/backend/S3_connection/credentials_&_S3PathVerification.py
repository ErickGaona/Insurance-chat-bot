import boto3
import os

def parse_s3_uri(s3_uri: str):
    """
    Parsea una URI de S3 para obtener el nombre del bucket y el prefijo de la carpeta.
    
    Args:
        s3_uri (str): La URI de S3 en formato 's3://nombre-del-bucket/prefijo/de/carpeta/'.
        
    Returns:
        tuple: Una tupla con (nombre_del_bucket, prefijo_de_la_carpeta).
    """
    if not s3_uri.startswith("s3://"):
        raise ValueError("La URI de S3 debe comenzar con 's3://'")
    
    # Elimina el prefijo 's3://'
    path = s3_uri[5:]
    
    # Separa el nombre del bucket del resto del camino
    bucket_name, *rest = path.split('/', 1)
    folder_prefix = rest[0] if rest else ''
    
    return bucket_name, folder_prefix

def check_bucket_access(bucket_name, folder_prefix):
    """
    Verifica si las credenciales tienen acceso al bucket y a la carpeta especificados.
    
    Args:
        bucket_name (str): El nombre del bucket de S3.
        folder_prefix (str): El prefijo de la carpeta a verificar.
    """
    try:
        s3_client = boto3.client('s3')
        
        # Intenta listar los contenidos de la "carpeta"
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix, MaxKeys=5)
        
        if "Contents" in response:
            print(f"¡Conexión exitosa al bucket '{bucket_name}'!")
            print(f"Archivos encontrados en la carpeta '{folder_prefix}':")
            for obj in response['Contents']:
                print(f"  - {obj['Key']}")
        else:
            print(f"Conexión exitosa, pero no se encontraron archivos en la carpeta '{folder_prefix}'.")
            
    except Exception as e:
        print(f"Error al intentar acceder al bucket '{bucket_name}':")
        print(e)
        
# --- Ejemplo de uso ---
s3_uri_dataset = 's3://anyoneai-datasets/queplan_insurance/'

print(f"--- Verificando el acceso a la URI: {s3_uri_dataset} ---")
nombre_del_bucket, ruta_de_carpeta_s3 = parse_s3_uri(s3_uri_dataset)

check_bucket_access(nombre_del_bucket, ruta_de_carpeta_s3)
