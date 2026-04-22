"""Document management routes."""

from flask import Blueprint, request, jsonify, current_app

from services.document_service import get_document_service

# Create documents blueprint
documents_bp = Blueprint('documents', __name__, url_prefix='/api/v1/documents')


@documents_bp.route('/', methods=['POST'])
def add_document():
    """Add a new document to the ChromaDB collection. Supports both PDF file upload and direct text input."""
    try:
        print("🔍 Add document request received")
        
        document_service = get_document_service()
        upload_folder = current_app.config.get('UPLOAD_FOLDER')
        
        # Check if it's a file upload
        if 'file' in request.files:
            file = request.files['file']
            
            # Get additional metadata from form
            metadata = {}
            if 'title' in request.form:
                metadata['title'] = request.form['title']
            if 'description' in request.form:
                metadata['description'] = request.form['description']
            if 'tags' in request.form:
                metadata['tags'] = request.form['tags']
            
            result = document_service.add_document_from_file(file, upload_folder, metadata)
            return jsonify(result)
        
        # Check if it's direct text input
        elif request.is_json:
            data = request.get_json()
            
            if 'text' not in data:
                return jsonify({
                    "error": "Missing 'text' field for text input",
                    "status": "error"
                }), 400
            
            text = data['text'].strip()
            title = data.get('title', 'Untitled Document')
            metadata = data.get('metadata', {})
            
            if not text:
                return jsonify({
                    "error": "Text content cannot be empty",
                    "status": "error"
                }), 400
            
            result = document_service.add_document_from_text(text, title, metadata)
            return jsonify(result)
        
        else:
            return jsonify({
                "error": "No file or text data provided",
                "status": "error"
            }), 400
    
    except ValueError as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 400
    except RuntimeError as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500
    except Exception as e:
        return jsonify({
            "error": f"Unexpected error: {str(e)}",
            "status": "error"
        }), 500


@documents_bp.route('/', methods=['GET'])
def list_documents():
    """List all documents in the collection."""
    try:
        document_service = get_document_service()
        
        # Get query parameters
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', 0, type=int)
        
        result = document_service.list_documents(limit=limit, offset=offset)
        return jsonify(result)
    
    except RuntimeError as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500
    except Exception as e:
        return jsonify({
            "error": f"Error listing documents: {str(e)}",
            "status": "error"
        }), 500


@documents_bp.route('/<document_id>', methods=['GET'])
def get_document(document_id):
    """Get a specific document by ID."""
    try:
        document_service = get_document_service()
        result = document_service.get_document(document_id)
        return jsonify(result)
    
    except ValueError as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 404
    except RuntimeError as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500
    except Exception as e:
        return jsonify({
            "error": f"Error retrieving document: {str(e)}",
            "status": "error"
        }), 500


@documents_bp.route('/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete a specific document by ID."""
    try:
        document_service = get_document_service()
        result = document_service.delete_document(document_id)
        return jsonify(result)
    
    except ValueError as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 404
    except RuntimeError as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500
    except Exception as e:
        return jsonify({
            "error": f"Error deleting document: {str(e)}",
            "status": "error"
        }), 500


@documents_bp.route('/', methods=['DELETE'])
def delete_multiple_documents():
    """Delete multiple documents by IDs."""
    try:
        data = request.get_json()
        
        if not data or 'document_ids' not in data:
            return jsonify({
                "error": "Missing 'document_ids' field in request",
                "status": "error"
            }), 400
        
        document_service = get_document_service()
        result = document_service.delete_multiple_documents(data['document_ids'])
        
        # Return appropriate HTTP status based on result
        if result["status"] == "success":
            return jsonify(result)
        elif result["status"] == "partial_success":
            return jsonify(result), 207  # Multi-Status
        else:
            return jsonify(result), 400
    
    except ValueError as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"Error deleting documents: {str(e)}",
            "status": "error"
        }), 500


@documents_bp.route('/<document_id>', methods=['PUT'])
def update_document(document_id):
    """Update a specific document by ID."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No update data provided",
                "status": "error"
            }), 400
        
        # Note: ChromaDB doesn't support direct updates, so we would need to delete and re-add
        # For now, return not implemented
        return jsonify({
            "error": "Document update not implemented yet",
            "status": "error"
        }), 501
    
    except Exception as e:
        return jsonify({
            "error": f"Error updating document: {str(e)}",
            "status": "error"
        }), 500


@documents_bp.route('/search', methods=['POST'])
def search_documents():
    """Search documents by content."""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "error": "Missing 'query' field in request",
                "status": "error"
            }), 400
        
        query = data['query'].strip()
        num_results = data.get('num_results', 10)
        
        if not query:
            return jsonify({
                "error": "Query cannot be empty",
                "status": "error"
            }), 400
        
        document_service = get_document_service()
        result = document_service.search_documents(query, num_results)
        return jsonify(result)
    
    except RuntimeError as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500
    except Exception as e:
        return jsonify({
            "error": f"Error searching documents: {str(e)}",
            "status": "error"
        }), 500