"""Input validation utilities."""

import re
from typing import Any, Dict, List, Optional, Union
from flask import request


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """Validate that all required fields are present in the data."""
    if not data:
        raise ValueError("Request data cannot be empty")
    
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")


def validate_non_empty_string(value: Any, field_name: str) -> str:
    """Validate that a value is a non-empty string."""
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    
    cleaned_value = value.strip()
    if not cleaned_value:
        raise ValueError(f"{field_name} cannot be empty")
    
    return cleaned_value


def validate_positive_integer(value: Any, field_name: str, min_value: int = 1, max_value: Optional[int] = None) -> int:
    """Validate that a value is a positive integer within bounds."""
    if not isinstance(value, int):
        raise ValueError(f"{field_name} must be an integer")
    
    if value < min_value:
        raise ValueError(f"{field_name} must be at least {min_value}")
    
    if max_value is not None and value > max_value:
        raise ValueError(f"{field_name} must be at most {max_value}")
    
    return value


def validate_list(value: Any, field_name: str, min_length: int = 0, max_length: Optional[int] = None) -> List[Any]:
    """Validate that a value is a list with appropriate length."""
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list")
    
    if len(value) < min_length:
        raise ValueError(f"{field_name} must contain at least {min_length} items")
    
    if max_length is not None and len(value) > max_length:
        raise ValueError(f"{field_name} must contain at most {max_length} items")
    
    return value


def validate_email(email: str) -> str:
    """Validate email format."""
    if not email:
        raise ValueError("Email cannot be empty")
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValueError("Invalid email format")
    
    return email.lower().strip()


def validate_boolean(value: Any, field_name: str) -> bool:
    """Validate and convert a value to boolean."""
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        value_lower = value.lower()
        if value_lower in ('true', '1', 'yes', 'on'):
            return True
        elif value_lower in ('false', '0', 'no', 'off'):
            return False
    
    raise ValueError(f"{field_name} must be a boolean value")


def validate_choice(value: Any, field_name: str, choices: List[Any]) -> Any:
    """Validate that a value is one of the allowed choices."""
    if value not in choices:
        raise ValueError(f"{field_name} must be one of: {', '.join(map(str, choices))}")
    
    return value


def validate_string_length(value: str, field_name: str, min_length: int = 0, max_length: Optional[int] = None) -> str:
    """Validate string length constraints."""
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    
    if len(value) < min_length:
        raise ValueError(f"{field_name} must be at least {min_length} characters long")
    
    if max_length is not None and len(value) > max_length:
        raise ValueError(f"{field_name} must be at most {max_length} characters long")
    
    return value


def validate_json_content_type():
    """Validate that the request has JSON content type."""
    if not request.is_json:
        raise ValueError("Request must have Content-Type: application/json")


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename by removing or replacing invalid characters."""
    if not filename:
        raise ValueError("Filename cannot be empty")
    
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Ensure it's not empty after sanitization
    if not sanitized:
        raise ValueError("Filename contains only invalid characters")
    
    return sanitized


class ValidationError(ValueError):
    """Custom validation error for better error handling."""
    pass


def validate_pagination_params(limit: Optional[int] = None, offset: Optional[int] = None) -> tuple[Optional[int], int]:
    """Validate pagination parameters."""
    if limit is not None:
        limit = validate_positive_integer(limit, "limit", min_value=1, max_value=1000)
    
    if offset is not None:
        offset = validate_positive_integer(offset, "offset", min_value=0)
    else:
        offset = 0
    
    return limit, offset