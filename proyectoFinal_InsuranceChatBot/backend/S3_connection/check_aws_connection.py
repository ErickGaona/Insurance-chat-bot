import boto3

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
nombre_del_bucket = 'anyoneai-datasets'
ruta_de_carpeta_s3 = 's3://anyoneai-datasets/queplan_insurance/'

check_bucket_access(nombre_del_bucket, ruta_de_carpeta_s3)