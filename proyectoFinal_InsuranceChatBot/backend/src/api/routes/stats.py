"""Statistics routes for system and document statistics."""

from flask import Blueprint, jsonify

from services.chatbot_service import get_chatbot_service

# Create stats blueprint
stats_bp = Blueprint('stats', __name__, url_prefix='/api/v1/stats')


@stats_bp.route('/', methods=['GET'])
def stats_endpoint():
    """Get database statistics."""
    try:
        chatbot_service = get_chatbot_service()
        
        if chatbot_service.is_hybrid_available():
            # Get stats from hybrid search engine
            stats = chatbot_service.hybrid_chatbot.search_engine.rag_core.get_collection_stats()
            stats["hybrid_search_available"] = True
            stats["web_search_available"] = chatbot_service.hybrid_chatbot.search_engine.brave_client is not None
            chatbot_type = "hybrid"
        else:
            # Get stats from standard chatbot
            stats = chatbot_service.chatbot.rag_core.get_collection_stats()
            stats["hybrid_search_available"] = False
            stats["web_search_available"] = False
            chatbot_type = "standard"
        
        return jsonify({
            "stats": stats,
            "chatbot_type": chatbot_type,
            "status": "success"
        })
        
    except RuntimeError as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500
    except Exception as e:
        return jsonify({
            "error": f"Error getting stats: {str(e)}",
            "status": "error"
        }), 500


@stats_bp.route('/documents', methods=['GET'])
def document_stats():
    """Get comprehensive document statistics and collection information."""
    try:
        chatbot_service = get_chatbot_service()
        
        # Get the ChromaDB collection
        if chatbot_service.is_hybrid_available():
            rag_core = chatbot_service.hybrid_chatbot.search_engine.rag_core
        else:
            rag_core = chatbot_service.chatbot.rag_core
        
        collection = rag_core.collection
        
        # Get basic stats
        basic_stats = rag_core.get_collection_stats()
        
        # Get all documents for detailed analysis
        all_docs = collection.get(include=["metadatas"])
        
        # Analyze by source
        source_stats = {}
        document_type_stats = {}
        file_extension_stats = {}
        upload_dates = []
        
        for metadata in all_docs["metadatas"]:
            # Source statistics
            source = metadata.get("source", "unknown")
            source_stats[source] = source_stats.get(source, 0) + 1
            
            # Document type statistics
            doc_type = metadata.get("document_type", "unknown")
            document_type_stats[doc_type] = document_type_stats.get(doc_type, 0) + 1
            
            # File extension statistics
            if source != "unknown" and "." in source:
                ext = source.split(".")[-1].lower()
                file_extension_stats[ext] = file_extension_stats.get(ext, 0) + 1
            
            # Upload dates
            upload_date = metadata.get("upload_date")
            if upload_date:
                upload_dates.append(upload_date)
        
        # Prepare detailed statistics
        detailed_stats = {
            **basic_stats,
            "source_breakdown": source_stats,
            "document_type_breakdown": document_type_stats,
            "file_extension_breakdown": file_extension_stats,
            "total_unique_sources": len(source_stats),
            "upload_dates": sorted(upload_dates) if upload_dates else [],
            "latest_upload": max(upload_dates) if upload_dates else None,
            "earliest_upload": min(upload_dates) if upload_dates else None
        }
        
        return jsonify({
            "detailed_stats": detailed_stats,
            "status": "success"
        })
        
    except RuntimeError as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500
    except Exception as e:
        return jsonify({
            "error": f"Error getting document stats: {str(e)}",
            "status": "error"
        }), 500