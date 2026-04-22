"""Search routes for document and content search."""

from flask import Blueprint, request, jsonify

from services.chatbot_service import get_chatbot_service

# Create search blueprint
search_bp = Blueprint('search', __name__, url_prefix='/api/v1/search')


@search_bp.route('/', methods=['POST'])
def search_endpoint():
    """Direct search endpoint supporting both local and hybrid search."""
    try:
        chatbot_service = get_chatbot_service()
        
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "error": "Missing 'query' field in request"
            }), 400
        
        query = data['query'].strip()
        num_results = data.get('num_results', 10)
        include_metadata = data.get('include_metadata', True)
        
        if not query:
            return jsonify({
                "error": "Query cannot be empty"
            }), 400
        
        # Use chatbot service search method
        response = chatbot_service.search(
            query=query,
            num_results=num_results,
            include_metadata=include_metadata
        )
        
        # Add search type information
        response["search_type"] = (
            "hybrid" if chatbot_service.is_hybrid_available() 
            else "local_only"
        )
        
        return jsonify(response)
        
    except RuntimeError as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500
    except Exception as e:
        return jsonify({
            "error": f"Error processing search: {str(e)}",
            "status": "error"
        }), 500


@search_bp.route('/hybrid', methods=['POST'])
def hybrid_search_endpoint():
    """Search endpoint that forces hybrid search."""
    try:
        chatbot_service = get_chatbot_service()
        
        if not chatbot_service.is_hybrid_available():
            return jsonify({
                "error": "Hybrid search not available"
            }), 503
        
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "error": "Missing 'query' field in request"
            }), 400
        
        query = data['query'].strip()
        force_web_search = data.get('force_web_search', True)
        
        if not query:
            return jsonify({
                "error": "Query cannot be empty"
            }), 400
        
        # Use hybrid chatbot directly for web search
        search_results, search_metadata = chatbot_service.hybrid_chatbot.get_relevant_context(
            query, 
            force_web_search=force_web_search
        )
        
        return jsonify({
            "query": query,
            "results": search_results,
            "num_results": len(search_results),
            "search_metadata": search_metadata,
            "search_type": "hybrid",
            "forced_web_search": force_web_search,
            "status": "success"
        })
        
    except RuntimeError as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500
    except Exception as e:
        return jsonify({
            "error": f"Error processing hybrid search: {str(e)}",
            "status": "error"
        }), 500