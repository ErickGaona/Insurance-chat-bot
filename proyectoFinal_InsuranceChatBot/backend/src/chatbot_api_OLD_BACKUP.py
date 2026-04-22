from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import uuid
try:
    from werkzeug.utils import secure_filename
except ImportError:
    # Fallback if werkzeug is not available
    def secure_filename(filename):
        return filename.replace('/', '_').replace('\\', '_')

from insurance_chatbot import InsuranceChatbot
from hybrid_insurance_chatbot import HybridInsuranceChatbot
from data_ingestion import extract_text_from_pdf, extract_articles_from_text
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for web frontend

# Configure file upload settings
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Initialize chatbots globally
chatbot = None
hybrid_chatbot = None

def initialize_chatbots():
    """Initialize both standard and hybrid chatbot instances."""
    global chatbot, hybrid_chatbot
    
    # Get the correct ChromaDB path - it's in the backend directory
    backend_dir = os.path.dirname(os.path.dirname(__file__))  # Go up from src to backend
    chroma_db_path = os.path.join(backend_dir, "chroma_db")
    
    print(f"🔍 Looking for ChromaDB at: {chroma_db_path}")
    
    # Initialize standard chatbot
    try:
        chatbot = InsuranceChatbot(chroma_db_path=chroma_db_path)
        print("✅ Standard chatbot initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize standard chatbot: {e}")
        chatbot = None
    
    # Initialize hybrid chatbot
    try:
        hybrid_chatbot = HybridInsuranceChatbot(chroma_db_path=chroma_db_path)
        print("✅ Hybrid chatbot initialized successfully")
    except Exception as e:
        print(f"⚠️ Failed to initialize hybrid chatbot: {e}")
        print("   Falling back to standard chatbot only")
        hybrid_chatbot = None
    
    return chatbot is not None or hybrid_chatbot is not None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "chatbot_ready": chatbot is not None,
        "hybrid_chatbot_ready": hybrid_chatbot is not None,
        "chatbot_type": "hybrid" if hybrid_chatbot is not None else "standard" if chatbot is not None else "none"
    })

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """Main chat endpoint with hybrid search support."""
    try:
        # Prefer hybrid chatbot if available, fall back to standard
        active_chatbot = hybrid_chatbot if hybrid_chatbot is not None else chatbot
        
        if not active_chatbot:
            return jsonify({
                "error": "No chatbot available"
            }), 500
        
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "error": "Missing 'message' field in request"
            }), 400
        
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({
                "error": "Message cannot be empty"
            }), 400
        
        # Get optional parameters
        verbose = data.get('verbose', False)
        force_web_search = data.get('force_web_search', False)
        
        # Get response from chatbot
        if hybrid_chatbot is not None:
            # Use hybrid chatbot with web search capability
            result = hybrid_chatbot.chat(
                user_message, 
                force_web_search=force_web_search,
                verbose=verbose
            )
            
            response = {
                "question": result["question"],
                "answer": result["answer"],
                "sources_used": result["sources_used"],
                "local_sources": result["local_sources"],
                "web_sources": result["web_sources"],
                "search_strategy": result["search_strategy"],
                "used_web_search": result["used_web_search"],
                "chatbot_type": "hybrid",
                "status": "success"
            }
        else:
            # Fall back to standard chatbot
            result = chatbot.chat(user_message, verbose=verbose)
            
            response = {
                "question": result["question"],
                "answer": result["answer"],
                "sources_used": result["sources_used"],
                "local_sources": result["sources_used"],
                "web_sources": 0,
                "search_strategy": "local_only",
                "used_web_search": False,
                "chatbot_type": "standard",
                "status": "success"
            }
        
        if verbose and hybrid_chatbot is not None:
            response["search_results"] = result.get("search_results", [])
            response["search_metadata"] = result.get("search_metadata", {})
        elif verbose:
            response["context_docs"] = result.get("context_docs", [])
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "error": f"Error processing request: {str(e)}",
            "status": "error"
        }), 500

@app.route('/search', methods=['POST'])
def search_endpoint():
    """Direct search endpoint supporting both local and hybrid search."""
    try:
        # Prefer hybrid chatbot if available, fall back to standard
        active_chatbot = hybrid_chatbot if hybrid_chatbot is not None else chatbot
        
        if not active_chatbot:
            return jsonify({
                "error": "No chatbot available"
            }), 500
        
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "error": "Missing 'query' field in request"
            }), 400
        
        query = data['query'].strip()
        num_results = data.get('num_results', 5)
        force_web_search = data.get('force_web_search', False)
        
        if not query:
            return jsonify({
                "error": "Query cannot be empty"
            }), 400
        
        if hybrid_chatbot is not None:
            # Use hybrid search
            search_results, search_metadata = hybrid_chatbot.get_relevant_context(
                query, 
                force_web_search=force_web_search
            )
            
            return jsonify({
                "query": query,
                "results": search_results,
                "num_results": len(search_results),
                "search_metadata": search_metadata,
                "search_type": "hybrid",
                "status": "success"
            })
        else:
            # Fall back to standard ChromaDB search
            results = chatbot.get_relevant_context(query, num_docs=num_results)
            
            return jsonify({
                "query": query,
                "results": results,
                "num_results": len(results),
                "search_type": "local_only",
                "status": "success"
            })
        
    except Exception as e:
        return jsonify({
            "error": f"Error processing search: {str(e)}",
            "status": "error"
        }), 500

@app.route('/stats', methods=['GET'])
def stats_endpoint():
    """Get database statistics."""
    try:
        # Prefer hybrid chatbot if available, fall back to standard
        active_chatbot = hybrid_chatbot if hybrid_chatbot is not None else chatbot
        
        if not active_chatbot:
            return jsonify({
                "error": "No chatbot available"
            }), 500
        
        if hybrid_chatbot is not None:
            # Get stats from hybrid search engine
            stats = hybrid_chatbot.search_engine.rag_core.get_collection_stats()
            stats["hybrid_search_available"] = True
            stats["web_search_available"] = hybrid_chatbot.search_engine.brave_client is not None
        else:
            # Get stats from standard chatbot
            stats = chatbot.rag_core.get_collection_stats()
            stats["hybrid_search_available"] = False
            stats["web_search_available"] = False
        
        return jsonify({
            "stats": stats,
            "chatbot_type": "hybrid" if hybrid_chatbot is not None else "standard",
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Error getting stats: {str(e)}",
            "status": "error"
        }), 500

@app.route('/add_document', methods=['POST'])
def add_document():
    """
    Add a new document to the ChromaDB collection.
    Supports both PDF file upload and direct text input.
    """
    try:
        global chatbot, hybrid_chatbot
        
        print("🔍 Add document request received")
        
        if chatbot is None and hybrid_chatbot is None:
            print("❌ No chatbot available")
            return jsonify({
                "error": "No chatbot available",
                "status": "error"
            }), 500
        
        # Get the ChromaDB collection (use hybrid if available, otherwise standard)
        if hybrid_chatbot is not None:
            rag_core = hybrid_chatbot.search_engine.rag_core
            print("✅ Using hybrid chatbot RAG core")
        else:
            rag_core = chatbot.rag_core
            print("✅ Using standard chatbot RAG core")
        
        collection = rag_core.collection
        
        # Initialize embedding model (same as used in ChromaDBBuilder)
        print("🔄 Initializing embedding model...")
        try:
            embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            print("✅ Embedding model loaded")
        except Exception as e:
            print(f"❌ Embedding model error: {e}")
            return jsonify({
                "error": f"Failed to load embedding model: {str(e)}",
                "status": "error"
            }), 500
        
        documents = []
        metadatas = []
        ids = []
        
        # Add timestamp for all documents
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        
        # Check if it's a file upload
        if 'file' in request.files:
            print("📄 Processing file upload")
            file = request.files['file']
            if file.filename == '':
                return jsonify({
                    "error": "No file selected",
                    "status": "error"
                }), 400
            
            # Validate file type
            allowed_extensions = {'.pdf', '.txt', '.docx'}
            file_ext = os.path.splitext(file.filename.lower())[1]
            
            if file_ext not in allowed_extensions:
                return jsonify({
                    "error": f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}",
                    "status": "error"
                }), 400
            
            filename = secure_filename(file.filename)
            print(f"📄 Processing file: {filename} (type: {file_ext})")
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as temp_file:
                try:
                    file.save(temp_file.name)
                    print(f"💾 Saved temp file: {temp_file.name}")
                    
                    # Extract text based on file type
                    text = ""
                    if file_ext == '.pdf':
                        text = extract_text_from_pdf(temp_file.name)
                        print(f"📝 Extracted {len(text)} characters from PDF")
                    elif file_ext == '.txt':
                        with open(temp_file.name, 'r', encoding='utf-8') as f:
                            text = f.read()
                        print(f"📝 Read {len(text)} characters from TXT")
                    elif file_ext == '.docx':
                        try:
                            import docx
                            doc = docx.Document(temp_file.name)
                            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                            print(f"📝 Extracted {len(text)} characters from DOCX")
                        except ImportError:
                            return jsonify({
                                "error": "DOCX support not available. Please install python-docx.",
                                "status": "error"
                            }), 500
                    
                    # Clean up temp file
                    os.unlink(temp_file.name)
                    print("🗑️ Cleaned up temp file")
                    
                except Exception as e:
                    print(f"❌ File processing error: {e}")
                    # Try to clean up temp file even if there was an error
                    try:
                        os.unlink(temp_file.name)
                    except:
                        pass
                    return jsonify({
                        "error": f"Failed to process file: {str(e)}",
                        "status": "error"
                    }), 500
            
            if not text or len(text.strip()) < 10:
                return jsonify({
                    "error": "Could not extract meaningful text from file or file is too short",
                    "status": "error"
                }), 400
            
            # Extract articles/chunks from text
            try:
                articles = extract_articles_from_text(text, filename)
                print(f"📖 Extracted {len(articles)} chunks")
            except Exception as e:
                print(f"❌ Article extraction error: {e}")
                return jsonify({
                    "error": f"Failed to extract content: {str(e)}",
                    "status": "error"
                }), 500
            
            if not articles:
                # If no articles found, create a single chunk
                articles = [{
                    'file_name': filename,
                    'article_number': '1',
                    'article_title': f"Content from {filename}",
                    'article_content': text,
                    'chunk_type': 'full_document'
                }]
                print("📄 Created single document chunk")
            
            # Process each article/chunk
            for i, article in enumerate(articles):
                doc_id = f"upload_{filename}_{article['article_number']}_{str(uuid.uuid4())[:8]}"
                document_text = f"{article['article_title']}\n\n{article['article_content']}"
                
                documents.append(document_text)
                metadatas.append({
                    "source": "file_upload",
                    "document_type": "policy_article" if file_ext == '.pdf' else "text_document",
                    "file_name": filename,
                    "original_filename": file.filename,
                    "file_extension": file_ext,
                    "article_number": str(article['article_number']),
                    "article_title": article['article_title'],
                    "chunk_type": article.get('chunk_type', 'article'),
                    "upload_date": timestamp,
                    "created_date": timestamp,
                    "file_size_chars": len(text),
                    "chunk_index": i
                })
                ids.append(doc_id)
        
        # Check if it's direct text input
        elif request.is_json:
            print("📝 Processing JSON text input")
            try:
                data = request.get_json()
                print(f"📄 JSON data keys: {data.keys() if data else 'None'}")
            except Exception as e:
                print(f"❌ JSON parsing error: {e}")
                return jsonify({
                    "error": f"Invalid JSON data: {str(e)}",
                    "status": "error"
                }), 400
            
            if not data or 'text' not in data:
                return jsonify({
                    "error": "Missing 'text' field in JSON data",
                    "status": "error"
                }), 400
            
            text = data['text'].strip()
            if len(text) < 10:
                return jsonify({
                    "error": "Text content is too short (minimum 10 characters)",
                    "status": "error"
                }), 400
            
            title = data.get('title', 'Untitled Document').strip()
            doc_type = data.get('document_type', 'general_document')
            source = data.get('source', 'manual_input')
            category = data.get('category', 'general')
            
            print(f"📝 Text document: title='{title}', type='{doc_type}', length={len(text)}")
            
            doc_id = f"manual_{str(uuid.uuid4())}"
            
            documents.append(text)
            metadatas.append({
                "source": source,
                "document_type": doc_type,
                "title": title,
                "category": category,
                "file_name": f"{title}.txt",
                "upload_date": timestamp,
                "created_date": timestamp,
                "text_length": len(text),
                "content_type": "manual_text"
            })
            ids.append(doc_id)
        
        else:
            print("❌ No valid input found")
            return jsonify({
                "error": "No file or JSON data provided",
                "status": "error"
            }), 400
        
        if not documents:
            return jsonify({
                "error": "No documents to add",
                "status": "error"
            }), 400
        
        # Validate document sizes
        max_chars = 50000  # 50k character limit per document
        oversized_docs = [i for i, doc in enumerate(documents) if len(doc) > max_chars]
        if oversized_docs:
            return jsonify({
                "error": f"Documents {oversized_docs} exceed maximum size of {max_chars} characters",
                "status": "error"
            }), 400
        
        # Check for duplicate content
        existing_docs = collection.get(include=["documents"])
        if existing_docs["documents"]:
            for i, new_doc in enumerate(documents):
                for existing_doc in existing_docs["documents"]:
                    # Simple similarity check (exact match or very similar)
                    if new_doc == existing_doc or (
                        len(new_doc) > 100 and 
                        len(existing_doc) > 100 and
                        new_doc[:100] == existing_doc[:100]
                    ):
                        print(f"⚠️ Potential duplicate detected for document {i}")
                        # Don't reject, but warn in metadata
                        metadatas[i]["potential_duplicate"] = True
        
        # Generate embeddings
        print(f"🔄 Generating embeddings for {len(documents)} documents...")
        try:
            embeddings = embedding_model.encode(documents).tolist()
            print(f"✅ Generated {len(embeddings)} embeddings")
        except Exception as e:
            print(f"❌ Embedding generation error: {e}")
            return jsonify({
                "error": f"Failed to generate embeddings: {str(e)}",
                "status": "error"
            }), 500
        
        # Add to ChromaDB collection
        try:
            print("💾 Adding documents to ChromaDB...")
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
            print("✅ Documents added to ChromaDB successfully")
        except Exception as e:
            print(f"❌ ChromaDB add error: {e}")
            return jsonify({
                "error": f"Failed to add documents to database: {str(e)}",
                "status": "error"
            }), 500
        
        # Get updated stats
        try:
            new_stats = rag_core.get_collection_stats()
            print(f"📊 Updated stats: {new_stats['total_documents']} total documents")
        except Exception as e:
            print(f"⚠️ Stats error (non-critical): {e}")
            new_stats = {"total_documents": "unknown"}
        
        print(f"🎉 Successfully added {len(documents)} documents")
        
        # Prepare response with summary
        response_data = {
            "message": f"Successfully added {len(documents)} documents to the knowledge base",
            "documents_added": len(documents),
            "new_total_documents": new_stats["total_documents"],
            "document_ids": ids,
            "processing_summary": {
                "total_chars_processed": sum(len(doc) for doc in documents),
                "average_doc_length": sum(len(doc) for doc in documents) // len(documents),
                "upload_timestamp": timestamp
            },
            "status": "success"
        }
        
        # Add warnings if any
        warnings = []
        duplicates = [i for i, meta in enumerate(metadatas) if meta.get("potential_duplicate")]
        if duplicates:
            warnings.append(f"Potential duplicates detected in documents: {duplicates}")
        
        if warnings:
            response_data["warnings"] = warnings
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Unexpected error in add_document: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": f"Error adding document: {str(e)}",
            "status": "error"
        }), 500

@app.route('/list_documents', methods=['GET'])
def list_documents():
    """
    List all documents in the ChromaDB collection with pagination and filtering.
    """
    try:
        global chatbot, hybrid_chatbot
        
        if chatbot is None and hybrid_chatbot is None:
            return jsonify({
                "error": "No chatbot available",
                "status": "error"
            }), 500
        
        # Get the ChromaDB collection
        if hybrid_chatbot is not None:
            rag_core = hybrid_chatbot.search_engine.rag_core
        else:
            rag_core = chatbot.rag_core
        
        collection = rag_core.collection
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)  # Max 100 per page
        
        # Get filter parameters
        source_filter = request.args.get('source')
        document_type_filter = request.args.get('document_type')
        file_name_filter = request.args.get('file_name')
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Build where clause for filtering
        where_clause = {}
        if source_filter:
            where_clause["source"] = source_filter
        if document_type_filter:
            where_clause["document_type"] = document_type_filter
        if file_name_filter:
            where_clause["file_name"] = {"$contains": file_name_filter}
        
        # Get documents with pagination and filtering
        try:
            if where_clause:
                results = collection.get(
                    limit=per_page,
                    offset=offset,
                    where=where_clause,
                    include=["documents", "metadatas"]
                )
            else:
                results = collection.get(
                    limit=per_page,
                    offset=offset,
                    include=["documents", "metadatas"]
                )
        except Exception as filter_error:
            # If filtering fails, try without filters
            print(f"Filter error: {filter_error}, trying without filters")
            results = collection.get(
                limit=per_page,
                offset=offset,
                include=["documents", "metadatas"]
            )
        
        # Get total count (approximate if filtering is used)
        try:
            if where_clause:
                # For filtered results, we need to count differently
                all_filtered = collection.get(where=where_clause, include=["metadatas"])
                total_docs = len(all_filtered["ids"])
            else:
                total_docs = collection.count()
        except:
            total_docs = len(results["ids"])
        
        # Format results
        documents = []
        for i, doc in enumerate(results["documents"]):
            metadata = results["metadatas"][i] if i < len(results["metadatas"]) else {}
            documents.append({
                "id": results["ids"][i],
                "preview": doc[:200] + "..." if len(doc) > 200 else doc,
                "metadata": metadata,
                "length": len(doc),
                "created_date": metadata.get("created_date", "Unknown")
            })
        
        return jsonify({
            "documents": documents,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_documents": total_docs,
                "total_pages": (total_docs + per_page - 1) // per_page,
                "has_next": offset + per_page < total_docs,
                "has_prev": page > 1
            },
            "filters": {
                "source": source_filter,
                "document_type": document_type_filter,
                "file_name": file_name_filter
            },
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Error listing documents: {str(e)}",
            "status": "error"
        }), 500

@app.route('/get_document/<document_id>', methods=['GET'])
def get_document(document_id):
    """
    Get a specific document by ID.
    """
    try:
        global chatbot, hybrid_chatbot
        
        if chatbot is None and hybrid_chatbot is None:
            return jsonify({
                "error": "No chatbot available",
                "status": "error"
            }), 500
        
        # Get the ChromaDB collection
        if hybrid_chatbot is not None:
            rag_core = hybrid_chatbot.search_engine.rag_core
        else:
            rag_core = chatbot.rag_core
        
        collection = rag_core.collection
        
        # Get the specific document
        results = collection.get(
            ids=[document_id],
            include=["documents", "metadatas"]
        )
        
        if not results["ids"]:
            return jsonify({
                "error": "Document not found",
                "status": "error"
            }), 404
        
        document = {
            "id": results["ids"][0],
            "content": results["documents"][0],
            "metadata": results["metadatas"][0],
            "length": len(results["documents"][0])
        }
        
        return jsonify({
            "document": document,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Error getting document: {str(e)}",
            "status": "error"
        }), 500

@app.route('/delete_document/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """
    Delete a specific document by ID.
    """
    try:
        global chatbot, hybrid_chatbot
        
        if chatbot is None and hybrid_chatbot is None:
            return jsonify({
                "error": "No chatbot available",
                "status": "error"
            }), 500
        
        # Get the ChromaDB collection
        if hybrid_chatbot is not None:
            rag_core = hybrid_chatbot.search_engine.rag_core
        else:
            rag_core = chatbot.rag_core
        
        collection = rag_core.collection
        
        # Check if document exists first
        existing = collection.get(ids=[document_id], include=["metadatas"])
        if not existing["ids"]:
            return jsonify({
                "error": "Document not found",
                "status": "error"
            }), 404
        
        # Delete the document
        collection.delete(ids=[document_id])
        
        # Get updated stats
        new_stats = rag_core.get_collection_stats()
        
        return jsonify({
            "message": f"Document {document_id} deleted successfully",
            "deleted_document": {
                "id": document_id,
                "metadata": existing["metadatas"][0]
            },
            "new_total_documents": new_stats["total_documents"],
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Error deleting document: {str(e)}",
            "status": "error"
        }), 500

@app.route('/delete_documents', methods=['POST'])
def delete_documents():
    """
    Delete multiple documents by IDs or by filter criteria.
    """
    try:
        global chatbot, hybrid_chatbot
        
        if chatbot is None and hybrid_chatbot is None:
            return jsonify({
                "error": "No chatbot available",
                "status": "error"
            }), 500
        
        # Get the ChromaDB collection
        if hybrid_chatbot is not None:
            rag_core = hybrid_chatbot.search_engine.rag_core
        else:
            rag_core = chatbot.rag_core
        
        collection = rag_core.collection
        
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "No data provided",
                "status": "error"
            }), 400
        
        # Method 1: Delete by specific IDs
        if 'document_ids' in data:
            document_ids = data['document_ids']
            if not isinstance(document_ids, list) or not document_ids:
                return jsonify({
                    "error": "document_ids must be a non-empty list",
                    "status": "error"
                }), 400
            
            # Check which documents exist
            existing = collection.get(ids=document_ids, include=["metadatas"])
            existing_ids = existing["ids"]
            
            if not existing_ids:
                return jsonify({
                    "error": "None of the specified documents were found",
                    "status": "error"
                }), 404
            
            # Delete existing documents
            collection.delete(ids=existing_ids)
            
            deleted_count = len(existing_ids)
            not_found_count = len(document_ids) - deleted_count
            
        # Method 2: Delete by filter criteria
        elif 'filter_criteria' in data:
            filter_criteria = data['filter_criteria']
            
            # Get documents that match filter
            matching_docs = collection.get(where=filter_criteria, include=["metadatas"])
            
            if not matching_docs["ids"]:
                return jsonify({
                    "message": "No documents found matching the filter criteria",
                    "deleted_count": 0,
                    "status": "success"
                })
            
            # Delete matching documents
            collection.delete(where=filter_criteria)
            
            deleted_count = len(matching_docs["ids"])
            not_found_count = 0
            existing_ids = matching_docs["ids"]
            
        else:
            return jsonify({
                "error": "Either 'document_ids' or 'filter_criteria' must be provided",
                "status": "error"
            }), 400
        
        # Get updated stats
        new_stats = rag_core.get_collection_stats()
        
        response = {
            "message": f"Successfully deleted {deleted_count} documents",
            "deleted_count": deleted_count,
            "deleted_document_ids": existing_ids,
            "new_total_documents": new_stats["total_documents"],
            "status": "success"
        }
        
        if not_found_count > 0:
            response["not_found_count"] = not_found_count
            response["message"] += f" ({not_found_count} documents were not found)"
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "error": f"Error deleting documents: {str(e)}",
            "status": "error"
        }), 500

@app.route('/update_document/<document_id>', methods=['PUT'])
def update_document(document_id):
    """
    Update a specific document's content and/or metadata.
    """
    try:
        global chatbot, hybrid_chatbot
        
        if chatbot is None and hybrid_chatbot is None:
            return jsonify({
                "error": "No chatbot available",
                "status": "error"
            }), 500
        
        # Get the ChromaDB collection
        if hybrid_chatbot is not None:
            rag_core = hybrid_chatbot.search_engine.rag_core
        else:
            rag_core = chatbot.rag_core
        
        collection = rag_core.collection
        
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "No data provided",
                "status": "error"
            }), 400
        
        # Check if document exists
        existing = collection.get(ids=[document_id], include=["documents", "metadatas"])
        if not existing["ids"]:
            return jsonify({
                "error": "Document not found",
                "status": "error"
            }), 404
        
        # Get current document data
        current_document = existing["documents"][0]
        current_metadata = existing["metadatas"][0]
        
        # Update content if provided
        new_content = data.get('content', current_document)
        
        # Update metadata if provided
        new_metadata = current_metadata.copy()
        if 'metadata' in data:
            new_metadata.update(data['metadata'])
        
        # Add update timestamp
        from datetime import datetime
        new_metadata['last_updated'] = datetime.now().isoformat()
        
        # Delete old document
        collection.delete(ids=[document_id])
        
        # Generate new embedding if content changed
        if new_content != current_document:
            embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            new_embedding = embedding_model.encode(new_content).tolist()
        else:
            # Get original embedding (not directly accessible, so regenerate)
            embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            new_embedding = embedding_model.encode(new_content).tolist()
        
        # Add updated document
        collection.add(
            documents=[new_content],
            metadatas=[new_metadata],
            ids=[document_id],
            embeddings=[new_embedding]
        )
        
        return jsonify({
            "message": f"Document {document_id} updated successfully",
            "updated_document": {
                "id": document_id,
                "content": new_content[:200] + "..." if len(new_content) > 200 else new_content,
                "metadata": new_metadata,
                "length": len(new_content)
            },
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Error updating document: {str(e)}",
            "status": "error"
        }), 500

@app.route('/document_stats', methods=['GET'])
def document_stats():
    """
    Get comprehensive document statistics and collection information.
    """
    try:
        global chatbot, hybrid_chatbot
        
        if chatbot is None and hybrid_chatbot is None:
            return jsonify({
                "error": "No chatbot available",
                "status": "error"
            }), 500
        
        # Get the ChromaDB collection
        if hybrid_chatbot is not None:
            rag_core = hybrid_chatbot.search_engine.rag_core
        else:
            rag_core = chatbot.rag_core
        
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
            
            # File extension statistics (if available)
            file_ext = metadata.get("file_extension", "")
            if file_ext:
                file_extension_stats[file_ext] = file_extension_stats.get(file_ext, 0) + 1
            
            # Upload dates
            upload_date = metadata.get("upload_date") or metadata.get("created_date")
            if upload_date:
                upload_dates.append(upload_date)
        
        # Calculate time-based statistics
        recent_uploads = 0
        if upload_dates:
            from datetime import datetime, timedelta
            now = datetime.now()
            week_ago = now - timedelta(days=7)
            
            for date_str in upload_dates:
                try:
                    upload_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    if upload_date.replace(tzinfo=None) > week_ago:
                        recent_uploads += 1
                except:
                    continue
        
        return jsonify({
            "basic_stats": basic_stats,
            "detailed_stats": {
                "by_source": source_stats,
                "by_document_type": document_type_stats,
                "by_file_extension": file_extension_stats,
                "recent_uploads_7_days": recent_uploads,
                "total_uploads_tracked": len(upload_dates)
            },
            "collection_info": {
                "collection_name": collection.name,
                "total_documents": len(all_docs["ids"])
            },
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Error getting document statistics: {str(e)}",
            "status": "error"
        }), 500

@app.route('/search_documents', methods=['POST'])
def search_documents():
    """
    Search documents in the collection with advanced filtering.
    """
    try:
        global chatbot, hybrid_chatbot
        
        if chatbot is None and hybrid_chatbot is None:
            return jsonify({
                "error": "No chatbot available",
                "status": "error"
            }), 500
        
        # Get the ChromaDB collection
        if hybrid_chatbot is not None:
            rag_core = hybrid_chatbot.search_engine.rag_core
        else:
            rag_core = chatbot.rag_core
        
        collection = rag_core.collection
        
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "No search data provided",
                "status": "error"
            }), 400
        
        query = data.get('query', '').strip()
        num_results = min(data.get('num_results', 10), 50)  # Max 50 results
        
        # Metadata filters
        filters = data.get('filters', {})
        where_clause = {}
        
        if filters.get('source'):
            where_clause['source'] = filters['source']
        if filters.get('document_type'):
            where_clause['document_type'] = filters['document_type']
        if filters.get('file_name'):
            where_clause['file_name'] = {"$contains": filters['file_name']}
        
        if query:
            # Semantic search with optional filtering
            search_kwargs = {
                "query_texts": [query],
                "n_results": num_results,
                "include": ["documents", "metadatas", "distances"]
            }
            
            if where_clause:
                search_kwargs["where"] = where_clause
            
            results = collection.query(**search_kwargs)
            
            # Format results
            search_results = []
            for i in range(len(results["documents"][0])):
                search_results.append({
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "similarity_score": 1.0 - results["distances"][0][i],  # Convert distance to similarity
                    "preview": results["documents"][0][i][:300] + "..." if len(results["documents"][0][i]) > 300 else results["documents"][0][i]
                })
            
            return jsonify({
                "query": query,
                "results": search_results,
                "num_results": len(search_results),
                "filters_applied": filters,
                "search_type": "semantic",
                "status": "success"
            })
        
        else:
            # Just filter without semantic search
            get_kwargs = {
                "include": ["documents", "metadatas"],
                "limit": num_results
            }
            
            if where_clause:
                get_kwargs["where"] = where_clause
            
            results = collection.get(**get_kwargs)
            
            # Format results
            filtered_results = []
            for i in range(len(results["documents"])):
                filtered_results.append({
                    "id": results["ids"][i],
                    "content": results["documents"][i],
                    "metadata": results["metadatas"][i],
                    "preview": results["documents"][i][:300] + "..." if len(results["documents"][i]) > 300 else results["documents"][i]
                })
            
            return jsonify({
                "results": filtered_results,
                "num_results": len(filtered_results),
                "filters_applied": filters,
                "search_type": "filter_only",
                "status": "success"
            })
        
    except Exception as e:
        return jsonify({
            "error": f"Error searching documents: {str(e)}",
            "status": "error"
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "status": "error"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "status": "error"
    }), 500

if __name__ == '__main__':
    print("🚀 Starting Enhanced Insurance Chatbot API with Hybrid Search...")
    
    # Initialize chatbots
    if initialize_chatbots():
        if hybrid_chatbot is not None:
            print("🌐 Hybrid search enabled (ChromaDB + Brave Search)")
        elif chatbot is not None:
            print("� Standard search only (ChromaDB)")
        
        print("�🌐 Starting Flask server...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("❌ Failed to start - no chatbot available")