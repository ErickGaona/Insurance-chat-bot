"""Flask application factory."""

from flask import Flask

from api.config import config
from api.extensions import init_extensions
from services.chatbot_service import initialize_chatbot_service


def create_app(config_name='default'):
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_extensions(app)
    
    # Initialize chatbot service
    chroma_db_path = app.config.get('CHROMA_DB_PATH')
    if not initialize_chatbot_service(chroma_db_path):
        print("⚠️ Warning: Chatbot service initialization failed")
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app


def register_blueprints(app):
    """Register all blueprints with the application."""
    from api.routes.health import health_bp
    from api.routes.chat import chat_bp
    from api.routes.search import search_bp
    from api.routes.stats import stats_bp
    from api.routes.documents import documents_bp
    
    app.register_blueprint(health_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(documents_bp)


def register_error_handlers(app):
    """Register error handlers."""
    
    @app.errorhandler(404)
    def not_found(error):
        return {
            "error": "Endpoint not found",
            "status": "error"
        }, 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return {
            "error": "Method not allowed",
            "status": "error"
        }, 405
    
    @app.errorhandler(500)
    def internal_error(error):
        return {
            "error": "Internal server error",
            "status": "error"
        }, 500