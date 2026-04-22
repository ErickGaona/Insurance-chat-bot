"""Flask extensions initialization."""

from flask_cors import CORS


def init_extensions(app):
    """Initialize Flask extensions with the application."""
    
    # Initialize CORS with explicit configuration
    cors_origins = app.config.get('CORS_ORIGINS', ["*"])
    CORS(app, 
         origins=cors_origins,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'],
         supports_credentials=False)
    
    # Configure file upload settings
    app.config['MAX_CONTENT_LENGTH'] = app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
    app.config['UPLOAD_FOLDER'] = app.config.get('UPLOAD_FOLDER')