from flask import Flask, send_from_directory
from .config import Config
from flask_cors import CORS

# Esta función create_app es responsable de configurar y crear una instancia de la aplicación Flask.
def create_app():

    # Se crea una nueva instancia de Flask, que representa la aplicación web.
    app = Flask(__name__)

    # Configura CORS (Cross-Origin Resource Sharing), lo que permite que recursos de la aplicación
    # sean accesibles desde dominios diferentes. En este caso, se permite el acceso desde cualquier origen ("*").
    # Esto es útil si el frontend y el backend están en servidores diferentes o en diferentes puertos.
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Carga la configuración de la aplicación desde un objeto Config, el cual debe estar definido en el módulo config.py.
    # En este archivo suelen estar variables como claves secretas, configuraciones de base de datos, etc.
    app.config.from_object(Config)

    # Importa y registra el blueprint para manejar las rutas y lógica de asistencias.
    # Al igual que con usuarios, este blueprint organiza las rutas relacionadas con la gestión de asistencias,
    # y todas las rutas dentro de este módulo estarán prefijadas con '/asistencias'.
    from .blueprints.asistencias import asistencias_bp
    # Se registra el blueprint de asistencias con el prefijo de URL '/asistencias'.
    app.register_blueprint(asistencias_bp, url_prefix='/asistencias')
    
     # Importar y registrar el blueprint para manejar las rutas de estudiantes
    from .blueprints.estudiantes import estudiantes_bp
    app.register_blueprint(estudiantes_bp, url_prefix='/estudiantes')
    
     # Ruta para servir archivos subidos
    @app.route('/uploads/<path:filename>', methods=['GET'])
    def uploaded_file(filename):
        print("HOLA FOTO")
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    
    # Retorna la instancia de la aplicación Flask ya configurada y lista para ser ejecutada.
    return app
