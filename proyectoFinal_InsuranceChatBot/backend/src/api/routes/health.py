"""Health check routes."""

from flask import Blueprint, jsonify

from services.chatbot_service import get_chatbot_service

# Create health blueprint
health_bp = Blueprint('health', __name__, url_prefix='/api/v1')


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        chatbot_service = get_chatbot_service()
        health_status = chatbot_service.get_health_status()
        return jsonify(health_status)
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "chatbot_ready": False,
            "hybrid_chatbot_ready": False,
            "chatbot_type": "none"
        }), 500


@health_bp.route('/detailed', methods=['GET'])
def detailed_health_check():
    """Detailed health check endpoint."""
    try:
        chatbot_service = get_chatbot_service()
        health_status = chatbot_service.get_health_status()
        
        # Add more detailed information
        detailed_status = {
            **health_status,
            "service_initialized": True,
            "chroma_db_path": chatbot_service.chroma_db_path
        }
        
        return jsonify(detailed_status)
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "service_initialized": False,
            "chatbot_ready": False,
            "hybrid_chatbot_ready": False,
            "chatbot_type": "none"
        }), 500