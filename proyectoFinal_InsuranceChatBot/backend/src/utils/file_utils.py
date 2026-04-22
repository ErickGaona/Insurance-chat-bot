"""File handling utilities."""

import os
import tempfile
import uuid
from typing import Optional

try:
    from werkzeug.utils import secure_filename
except ImportError:
    # Fallback if werkzeug is not available
    def secure_filename(filename):
        return filename.replace('/', '_').replace('\\', '_')


def get_secure_filename(filename: str) -> str:
    """Get a secure version of the filename."""
    return secure_filename(filename)


def save_uploaded_file(file, upload_folder: str) -> str:
    """Save uploaded file to temporary location and return the path."""
    if file.filename == '':
        raise ValueError("No file selected")
    
    if file:
        # Create secure filename
        filename = get_secure_filename(file.filename)
        
        # Add UUID to avoid naming conflicts
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        
        filepath = os.path.join(upload_folder, unique_filename)
        file.save(filepath)
        return filepath
    
    raise ValueError("Invalid file")


def cleanup_temp_file(filepath: str) -> None:
    """Clean up temporary file."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Warning: Could not clean up temp file {filepath}: {e}")


def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    return os.path.splitext(filename)[1].lower()


def is_pdf_file(filename: str) -> bool:
    """Check if file is a PDF."""
    return get_file_extension(filename) == '.pdf'