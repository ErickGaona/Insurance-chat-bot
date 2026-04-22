"""Chat routes for chatbot interactions."""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from services.chatbot_service import get_chatbot_service
from models.request_models import ChatRequest
from models.response_models import ChatResponse, ErrorResponse
from utils.error_handlers import (
    handle_validation_error, 
    handle_api_error, 
    handle_generic_error,
    safe_get_json,
    APIError,
    ServiceUnavailableAPIError
)

# Create chat blueprint
chat_bp = Blueprint('chat', __name__, url_prefix='/api/v1')


@chat_bp.route('/chat', methods=['POST'])
def chat_endpoint():
    """Main chat endpoint with hybrid search support."""
    try:
        # Validate and parse request
        data = safe_get_json()
        chat_request = ChatRequest(**data)
        
        # Get chatbot service
        chatbot_service = get_chatbot_service()
        
        # Get response from chatbot service
        result = chatbot_service.chat(
            message=chat_request.message,
            verbose=chat_request.verbose,
            force_web_search=chat_request.force_web_search
        )
        
        # Create response model
        response = ChatResponse(**result)
        return jsonify(response.dict())
        
    except ValidationError as e:
        error_response, status_code = handle_validation_error(e)
        return jsonify(error_response), status_code
    except RuntimeError as e:
        api_error = ServiceUnavailableAPIError(str(e))
        error_response, status_code = handle_api_error(api_error)
        return jsonify(error_response), status_code
    except APIError as e:
        error_response, status_code = handle_api_error(e)
        return jsonify(error_response), status_code
    except Exception as e:
        error_response, status_code = handle_generic_error(e)
        return jsonify(error_response), status_code


@chat_bp.route('/hybrid', methods=['POST'])
def hybrid_chat_endpoint():
    """Chat endpoint that forces hybrid search."""
    try:
        # Validate and parse request
        data = safe_get_json()
        chat_request = ChatRequest(**data)
        
        # Get chatbot service
        chatbot_service = get_chatbot_service()
        
        if not chatbot_service.is_hybrid_available():
            raise ServiceUnavailableAPIError("Hybrid chatbot not available")
        
        # Force web search for hybrid endpoint
        result = chatbot_service.chat(
            message=chat_request.message,
            verbose=chat_request.verbose,
            force_web_search=True
        )
        
        # Create response model
        response = ChatResponse(**result)
        return jsonify(response.dict())
        
    except ValidationError as e:
        error_response, status_code = handle_validation_error(e)
        return jsonify(error_response), status_code
    except APIError as e:
        error_response, status_code = handle_api_error(e)
        return jsonify(error_response), status_code
    except Exception as e:
        error_response, status_code = handle_generic_error(e)
        return jsonify(error_response), status_code