import cv2
import numpy as np
import boto3
import requests
from flask import Blueprint, jsonify, request, current_app
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

asistencias_bp = Blueprint('asistencias', __name__)

@asistencias_bp.route('/marcar', methods=['GET'])
def marcarAsistenciaRF():
    try:
        # Configurar boto3 para AWS Rekognition
       # Configurar boto3 para AWS Rekognition utilizando las credenciales desde app.config
        rekognition = boto3.client(
            'rekognition',
            region_name=current_app.config['REGION_NAME'],
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY']
        )
        
        # URLs estáticas de las imágenes de prueba
        source_image_url = 'https://www.famousbirthdays.com/faces/ann-lisa-image.jpg'
        target_image_url = 'https://image.tmdb.org/t/p/original/61yiWYGIfU2jZtTdWGYStZOL0AC.jpg'

        # Descargar las imágenes desde las URLs
        source_image_response = requests.get(source_image_url)
        target_image_response = requests.get(target_image_url)

        if source_image_response.status_code != 200 or target_image_response.status_code != 200:
            return jsonify({'error': 'No se pudo descargar una o ambas imágenes.'}), 400

        # Convertir las imágenes a bytes
        source_image_bytes = source_image_response.content
        target_image_bytes = target_image_response.content

        # Llamar a Rekognition para comparar rostros usando imágenes en bytes
        response = rekognition.compare_faces(
            SourceImage={'Bytes': source_image_bytes},
            TargetImage={'Bytes': target_image_bytes},
            SimilarityThreshold=80  # Umbral de similitud del 80%
        )


        # Revisar si se encontraron coincidencias
        if response['FaceMatches']:
            similarities = [
                {
                    'Similarity': match['Similarity'],
                    'Face': match['Face']
                }
                for match in response['FaceMatches']
            ]
            return jsonify({'matches': similarities})
        else:
            return jsonify({'message': 'No se encontraron coincidencias.'})

    except Exception as e:
        return jsonify({'error': f"Error inesperado: {str(e)}"}), 500

@asistencias_bp.route('/detect_faces', methods=['POST'])
def detect_faces():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    # Obtener la imagen del cuerpo de la solicitud
    if 'image' not in request.files:
        return jsonify({'error': 'No image file found in the request'}), 400
    
    # Leer la imagen
    file = request.files['image']
    img = np.asarray(bytearray(file.read()), dtype=np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    
    if img is None:
        return jsonify({'error': 'Unable to decode image'}), 400

    # Convertir la imagen a escala de grises (necesario para Haar Cascade)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detectar rostros en la imagen
    faces_detected = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,  # Factor de escala
        minNeighbors=5,   # Vecinos mínimos para confirmar una cara
        minSize=(30, 30), # Tamaño mínimo de la ventana de detección
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    # Extraer las caras detectadas
    faces = []
    for (x, y, w, h) in faces_detected:
        faces.append({
            'startX': int(x),
            'startY': int(y),
            'endX': int(x + w),
            'endY': int(y + h),
            'confidence': 1.0  # Haar Cascade no proporciona una medida de confianza real
        })

    # Devolver las coordenadas de las caras detectadas en formato JSON
    return jsonify({'faces': faces})

@asistencias_bp.route('/buscar_rostro', methods=['POST'])
def buscar_rostro_en_coleccion():
    rekognition = boto3.client(
        'rekognition',
        region_name=current_app.config['REGION_NAME'],
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY']
    )

    try:
        # Configurar boto3 para AWS Rekognition
        rekognition = boto3.client(
            'rekognition',
            region_name=current_app.config['REGION_NAME'],
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY']
        )
        
        # Obtener la imagen del cuerpo de la solicitud
        if 'image' not in request.files:
            return jsonify({'error': 'No image file found in the request'}), 400
        
        # Leer la imagen
        file = request.files['image']
        img_bytes = file.read()

        # Llamar a Rekognition para buscar rostros en la colección
        response = rekognition.search_faces_by_image(
            CollectionId='estudiantes',  # Cambia esto por el nombre de tu colección
            Image={'Bytes': img_bytes},
            MaxFaces=5,  # Número máximo de coincidencias que deseas obtener
            FaceMatchThreshold=80  # Umbral de similitud
        )

        # Revisar si se encontraron coincidencias
        if response['FaceMatches']:
            coincidencias = [
                {
                    'FaceId': match['Face']['FaceId'],
                    'Similarity': match['Similarity']
                }
                for match in response['FaceMatches']
            ]
            return jsonify({'matches': coincidencias})
        else:
            return jsonify({'message': 'No se encontraron coincidencias.'})

    except NoCredentialsError:
        return jsonify({'error': 'Credenciales de AWS no encontradas.'}), 403
    except PartialCredentialsError:
        return jsonify({'error': 'Credenciales de AWS incompletas.'}), 403
    except ClientError as e:
        return jsonify({'error': f"Error en la operación: {str(e)}"}), 500
    except Exception as e:
        return jsonify({'error': f"Error inesperado: {str(e)}"}), 500

 