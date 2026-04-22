"""Error handling utilities."""

import logging
from typing import Dict, Any, Optional, Tuple
from flask import jsonify, current_app
from pydantic import ValidationError

from models.response_models import ErrorResponse


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base API error class."""
    
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class ValidationAPIError(APIError):
    """Validation error for API requests."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)


class NotFoundAPIError(APIError):
    """Resource not found error."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, details=details)


class ConflictAPIError(APIError):
    """Resource conflict error."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=409, details=details)


class ServiceUnavailableAPIError(APIError):
    """Service unavailable error."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=503, details=details)


def handle_validation_error(error: ValidationError) -> Tuple[Dict[str, Any], int]:
    """Handle Pydantic validation errors."""
    error_details = []
    for err in error.errors():
        field = " -> ".join(str(x) for x in err["loc"])
        error_details.append({
            "field": field,
            "message": err["msg"],
            "type": err["type"]
        })
    
    response = ErrorResponse(
        error="Validation error",
        status="error"
    ).dict()
    response["details"] = error_details
    
    logger.warning(f"Validation error: {error_details}")
    return response, 400


def handle_api_error(error: APIError) -> Tuple[Dict[str, Any], int]:
    """Handle custom API errors."""
    response = ErrorResponse(
        error=error.message,
        status="error"
    ).dict()
    
    if error.details:
        response["details"] = error.details
    
    logger.error(f"API error ({error.status_code}): {error.message}")
    return response, error.status_code


def handle_generic_error(error: Exception) -> Tuple[Dict[str, Any], int]:
    """Handle generic exceptions."""
    error_message = str(error)
    
    # Log the full exception in debug mode
    if current_app.debug:
        logger.exception("Unhandled exception occurred")
        response = ErrorResponse(
            error=f"Internal error: {error_message}",
            status="error"
        ).dict()
    else:
        # Don't expose internal error details in production
        logger.error(f"Unhandled exception: {error_message}")
        response = ErrorResponse(
            error="Internal server error",
            status="error"
        ).dict()
    
    return response, 500


def create_error_response(message: str, status_code: int = 400, details: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], int]:
    """Create a standardized error response."""
    response = ErrorResponse(
        error=message,
        status="error"
    ).dict()
    
    if details:
        response["details"] = details
    
    return response, status_code


def log_request_error(endpoint: str, error: Exception, request_data: Optional[Dict[str, Any]] = None):
    """Log request errors with context."""
    logger.error(
        f"Error in {endpoint}: {str(error)}",
        extra={
            "endpoint": endpoint,
            "error_type": type(error).__name__,
            "request_data": request_data
        }
    )


def validate_content_type(required_type: str = "application/json") -> None:
    """Validate request content type."""
    from flask import request
    
    if not request.content_type or not request.content_type.startswith(required_type):
        raise ValidationAPIError(f"Content-Type must be {required_type}")


def validate_request_size(max_size_mb: int = 16) -> None:
    """Validate request size."""
    from flask import request
    
    if request.content_length:
        size_mb = request.content_length / (1024 * 1024)
        if size_mb > max_size_mb:
            raise ValidationAPIError(f"Request size ({size_mb:.1f}MB) exceeds maximum allowed size ({max_size_mb}MB)")


def safe_get_json() -> Dict[str, Any]:
    """Safely get JSON from request with validation."""
    from flask import request
    
    validate_content_type()
    validate_request_size()
    
    try:
        data = request.get_json()
        if data is None:
            raise ValidationAPIError("Invalid JSON in request body")
        return data
    except Exception as e:
        raise ValidationAPIError(f"Failed to parse JSON: {str(e)}")


def handle_service_error(error: Exception, service_name: str) -> APIError:
    """Convert service errors to appropriate API errors."""
    error_message = str(error)
    
    # Map common service errors to API errors
    if "not found" in error_message.lower():
        return NotFoundAPIError(f"{service_name} error: {error_message}")
    elif "validation" in error_message.lower() or "invalid" in error_message.lower():
        return ValidationAPIError(f"{service_name} error: {error_message}")
    elif "unavailable" in error_message.lower() or "connection" in error_message.lower():
        return ServiceUnavailableAPIError(f"{service_name} error: {error_message}")
    else:
        return APIError(f"{service_name} error: {error_message}")


def require_json_content():
    """Decorator to require JSON content type."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            validate_content_type()
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator