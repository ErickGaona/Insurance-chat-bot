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

def download_file_from_s3(bucket_name, s3_file_path, local_destination):
    """
    Descarga un archivo individual desde un bucket de AWS S3 a una ruta local.

    Args:
        bucket_name (str): El nombre del bucket de S3.
        s3_file_path (str): La ruta del archivo dentro del bucket (ej. 'data/dataset.csv').
        local_destination (str): La ruta de destino en el sistema de archivos local.
    """
    # Crea un cliente de S3
    s3_client = boto3.client('s3')

    # Crea la carpeta de destino si no existe
    destination_dir = os.path.dirname(local_destination)
    if destination_dir and not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    try:
        print(f"Descargando '{s3_file_path}' del bucket '{bucket_name}'...")
        # Usa el método download_file para descargar el archivo
        s3_client.download_file(bucket_name, s3_file_path, local_destination)
        print(f"¡Descarga completada! El archivo se guardó en: {local_destination}")
    except Exception as e:
        print(f"Ocurrió un error durante la descarga: {e}")


def download_folder_from_s3(bucket_name, s3_folder_prefix, local_destination_base):
    """
    Descarga una "carpeta" completa desde un bucket de AWS S3 a una ruta local.

    Args:
        bucket_name (str): El nombre del bucket de S3.
        s3_folder_prefix (str): El prefijo de la "carpeta" en S3 (ej. 'mis-imagenes/').
        local_destination_base (str): La ruta base en el sistema local para guardar los archivos.
    """
    s3_client = boto3.client('s3')

    # Lista todos los objetos (archivos) que comienzan con el prefijo dado
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=s3_folder_prefix)

    downloaded_count = 0
    for page in pages:
        if "Contents" in page:
            for obj in page["Contents"]:
                s3_file_path = obj["Key"]
                
                # Omite la "carpeta" del bucket, que es un objeto que termina en /
                if s3_file_path.endswith('/'):
                    continue
                
                # Construye la ruta de destino local, manteniendo la estructura de la carpeta
                local_file_path = os.path.join(local_destination_base, s3_file_path)
                
                # Crea la carpeta local para el archivo si no existe
                destination_dir = os.path.dirname(local_file_path)
                if not os.path.exists(destination_dir):
                    os.makedirs(destination_dir)
                
                try:
                    print(f"Descargando '{s3_file_path}'...")
                    s3_client.download_file(bucket_name, s3_file_path, local_file_path)
                    downloaded_count += 1
                except Exception as e:
                    print(f"Error al descargar '{s3_file_path}': {e}")
    
    if downloaded_count > 0:
        print(f"\n¡Descarga de carpeta completada! Total de archivos descargados: {downloaded_count}")
    else:
        print("\nNo se encontraron archivos para descargar en la carpeta especificada.")


# --- Ejemplo de uso ---
# Asegúrate de que tus credenciales estén configuradas correctamente en ~/.aws/credentials
# o con variables de entorno AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY.
s3_uri_dataset = 's3://anyoneai-datasets/queplan_insurance/'

# Analiza la URI para obtener el bucket y el prefijo de la carpeta
nombre_del_bucket, ruta_de_carpeta_s3 = parse_s3_uri(s3_uri_dataset)
ruta_local_de_destino_carpeta = 'local_data/queplan_insurance'

# Llama a la función para descargar la carpeta
print("\n--- Descargando la carpeta completa del dataset ---")
download_folder_from_s3(nombre_del_bucket, ruta_de_carpeta_s3, ruta_local_de_destino_carpeta)
