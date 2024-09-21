from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
import boto3

# Crear el blueprint para estudiantes
estudiantes_bp = Blueprint('estudiantes', __name__)

# Inicializar el cliente de S3
s3 = boto3.client('s3')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@estudiantes_bp.route('/upload_photo', methods=['POST'])
def upload_photo():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        image_url = f'http://yourdomain.com/uploads/{filename}'  # Ajusta según tu dominio

        return jsonify({'message': 'Foto subida con éxito', 'image_url': image_url}), 201
    else:
        return jsonify({'error': 'Tipo de archivo no permitido'}), 400


@estudiantes_bp.route('/upload_photo_s3', methods=['POST'])
def upload_photo_s3():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):  # Asegúrate de que esta función esté definida
        filename = secure_filename(file.filename)

        # Inicializar el cliente de S3 utilizando las credenciales y la región
        s3 = boto3.client(
            's3',
            region_name=current_app.config['REGION_NAME'],
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY']
        )
        
        s3_bucket = current_app.config['S3_BUCKET']
        region_name = current_app.config['REGION_NAME']
        
        # Nombre de la colección
        collection_name = 'estudiantes'  # Puedes personalizar este nombre

        # Subir el archivo a S3
        try:
            # Generar un nombre único si es necesario
            s3_file_path = f"{collection_name}/{filename}"

            # Subir el archivo a S3 con permisos públicos
            s3.upload_fileobj(
                file, 
                s3_bucket, 
                s3_file_path, 
                ExtraArgs={'ACL': 'public-read'}  # Hacer que el archivo sea público
            )
            
            # Indexar en la colección de Rekognition
            rekognition = boto3.client(
                'rekognition',
                region_name=current_app.config['REGION_NAME'],
                aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY']
            )
            
            response = rekognition.index_faces(
                CollectionId=collection_name,  # Usa el ID de tu colección
                Image={'S3Object': {'Bucket': s3_bucket, 'Name': s3_file_path}},  # Usa la ruta del archivo en S3
                DetectionAttributes=['ALL']
            )

            # Crear la URL pública de la imagen subida
            image_url = f"https://{s3_bucket}.s3.{region_name}.amazonaws.com/{s3_file_path}"

            return jsonify({'message': 'Foto subida e indexada con éxito', 'image_url': image_url, 'face_records': response['FaceRecords']}), 201
        
        except Exception as e:
            return jsonify({'error': f"Error subiendo el archivo a S3 o indexando en Rekognition: {str(e)}"}), 500
    else:
        return jsonify({'error': 'Tipo de archivo no permitido'}), 400