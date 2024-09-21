import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

class Config:
    # Claves de AWS
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    REGION_NAME = os.getenv('REGION_NAME')
    S3_BUCKET = os.getenv('AWS_S3_BUCKET')

    
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads') 
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
