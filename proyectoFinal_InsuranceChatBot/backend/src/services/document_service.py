"""Document service for managing document operations."""

import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

from sentence_transformers import SentenceTransformer

from data_ingestion import extract_text_from_pdf, extract_articles_from_text
from services.chatbot_service import get_chatbot_service
from utils.file_utils import save_uploaded_file, cleanup_temp_file, is_pdf_file


class DocumentService:
    """Service class for managing document operations."""
    
    def __init__(self):
        """Initialize the document service."""
        self.embedding_model = None
        self._initialize_embedding_model()
    
    def _initialize_embedding_model(self):
        """Initialize the embedding model."""
        try:
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            print("✅ Embedding model loaded")
        except Exception as e:
            print(f"❌ Embedding model error: {e}")
            raise RuntimeError(f"Failed to load embedding model: {str(e)}")
    
    def _get_collection(self):
        """Get the ChromaDB collection from chatbot service."""
        chatbot_service = get_chatbot_service()
        
        if chatbot_service.is_hybrid_available():
            return chatbot_service.hybrid_chatbot.search_engine.rag_core.collection
        else:
            return chatbot_service.chatbot.rag_core.collection
    
    def add_document_from_file(self, file, upload_folder: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add a document from uploaded file."""
        if not file or file.filename == '':
            raise ValueError("No file selected")
        
        print("📄 Processing file upload")
        
        # Save file temporarily
        filepath = save_uploaded_file(file, upload_folder)
        
        try:
            # Check if it's a PDF
            if is_pdf_file(file.filename):
                return self._process_pdf_file(filepath, file.filename, metadata)
            else:
                # Try to read as text file
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                return self._process_text_content(content, file.filename, metadata)
        
        finally:
            # Clean up temporary file
            cleanup_temp_file(filepath)
    
    def add_document_from_text(self, text: str, title: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add a document from direct text input."""
        print("📝 Processing direct text input")
        return self._process_text_content(text, title, metadata)
    
    def _process_pdf_file(self, filepath: str, filename: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a PDF file and add to collection."""
        print(f"📖 Processing PDF: {filename}")
        
        # Extract text from PDF
        try:
            pdf_text = extract_text_from_pdf(filepath)
            if not pdf_text or not pdf_text.strip():
                raise ValueError("Could not extract text from PDF or PDF is empty")
        except Exception as e:
            raise ValueError(f"Error extracting text from PDF: {str(e)}")
        
        # Extract articles/sections from the PDF text
        try:
            articles = extract_articles_from_text(pdf_text, filename)
            if not articles:
                # If no articles found, treat the whole document as one article
                articles = [{
                    'title': f"Document: {filename}",
                    'content': pdf_text,
                    'source': filename
                }]
        except Exception as e:
            print(f"⚠️ Article extraction failed, using full document: {e}")
            articles = [{
                'title': f"Document: {filename}",
                'content': pdf_text,
                'source': filename
            }]
        
        return self._add_articles_to_collection(articles, filename, metadata)
    
    def _process_text_content(self, content: str, source: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process text content and add to collection."""
        print(f"📝 Processing text content from: {source}")
        
        if not content or not content.strip():
            raise ValueError("Text content cannot be empty")
        
        # Try to extract articles from text
        try:
            articles = extract_articles_from_text(content, source)
            if not articles:
                # If no articles found, treat the whole text as one article
                articles = [{
                    'title': f"Document: {source}",
                    'content': content,
                    'source': source
                }]
        except Exception as e:
            print(f"⚠️ Article extraction failed, using full text: {e}")
            articles = [{
                'title': f"Document: {source}",
                'content': content,
                'source': source
            }]
        
        return self._add_articles_to_collection(articles, source, metadata)
    
    def _add_articles_to_collection(self, articles: List[Dict], source: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add articles to the ChromaDB collection."""
        collection = self._get_collection()
        
        documents = []
        metadatas = []
        ids = []
        
        timestamp = datetime.now().isoformat()
        base_metadata = metadata or {}
        
        print(f"📊 Processing {len(articles)} articles from {source}")
        
        for i, article in enumerate(articles):
            # Generate unique ID
            doc_id = f"{uuid.uuid4().hex}_{i}"
            
            # Prepare document content (handle both 'content' and 'article_content' fields)
            article_content = article.get('content', '') or article.get('article_content', '')
            article_content = article_content.strip() if article_content else ''
            if not article_content:
                continue
            
            documents.append(article_content)
            ids.append(doc_id)
            
            # Prepare metadata (handle both 'title' and 'article_title' fields)
            article_title = article.get('title', '') or article.get('article_title', '') or f"Article {i+1}"
            article_metadata = {
                'source': source,
                'title': article_title,
                'document_type': 'pdf' if is_pdf_file(source) else 'text',
                'upload_date': timestamp,
                'article_index': i,
                'total_articles': len(articles),
                **base_metadata
            }
            metadatas.append(article_metadata)
        
        if not documents:
            raise ValueError("No valid content found to add")
        
        # Generate embeddings
        print("🔄 Generating embeddings...")
        try:
            embeddings = self.embedding_model.encode(documents).tolist()
        except Exception as e:
            raise RuntimeError(f"Error generating embeddings: {str(e)}")
        
        # Add to collection
        print("💾 Adding to ChromaDB collection...")
        try:
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
        except Exception as e:
            raise RuntimeError(f"Error adding to collection: {str(e)}")
        
        print(f"✅ Successfully added {len(documents)} documents to collection")
        
        return {
            "message": f"Successfully added {len(documents)} documents from {source}",
            "documents_added": len(documents),
            "source": source,
            "document_ids": ids,
            "status": "success"
        }
    
    def get_document(self, document_id: str) -> Dict[str, Any]:
        """Get a specific document by ID."""
        collection = self._get_collection()
        
        try:
            result = collection.get(
                ids=[document_id],
                include=["documents", "metadatas"]
            )
            
            if not result["ids"]:
                raise ValueError(f"Document with ID {document_id} not found")
            
            return {
                "id": result["ids"][0],
                "content": result["documents"][0],
                "metadata": result["metadatas"][0],
                "status": "success"
            }
        
        except Exception as e:
            raise RuntimeError(f"Error retrieving document: {str(e)}")
    
    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """Delete a specific document by ID."""
        collection = self._get_collection()
        
        try:
            # Check if document exists
            existing = collection.get(ids=[document_id])
            if not existing["ids"]:
                raise ValueError(f"Document with ID {document_id} not found")
            
            # Delete the document
            collection.delete(ids=[document_id])
            
            return {
                "message": f"Document {document_id} deleted successfully",
                "deleted_id": document_id,
                "status": "success"
            }
        
        except Exception as e:
            raise RuntimeError(f"Error deleting document: {str(e)}")
    
    def list_documents(self, limit: Optional[int] = None, offset: int = 0) -> Dict[str, Any]:
        """List all documents in the collection."""
        collection = self._get_collection()
        
        try:
            result = collection.get(
                include=["metadatas"],
                limit=limit,
                offset=offset
            )
            
            documents = []
            for i, doc_id in enumerate(result["ids"]):
                metadata = result["metadatas"][i]
                documents.append({
                    "id": doc_id,
                    "title": metadata.get("title", "Unknown"),
                    "source": metadata.get("source", "Unknown"),
                    "document_type": metadata.get("document_type", "Unknown"),
                    "upload_date": metadata.get("upload_date"),
                    "metadata": metadata
                })
            
            return {
                "documents": documents,
                "total_returned": len(documents),
                "offset": offset,
                "limit": limit,
                "status": "success"
            }
        
        except Exception as e:
            raise RuntimeError(f"Error listing documents: {str(e)}")
    
    def search_documents(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """Search documents by content."""
        collection = self._get_collection()
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Search in collection
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=num_results,
                include=["documents", "metadatas", "distances"]
            )
            
            search_results = []
            if results["ids"] and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    search_results.append({
                        "id": doc_id,
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "similarity_score": 1 - results["distances"][0][i]  # Convert distance to similarity
                    })
            
            return {
                "query": query,
                "results": search_results,
                "num_results": len(search_results),
                "status": "success"
            }
        
        except Exception as e:
            raise RuntimeError(f"Error searching documents: {str(e)}")
    
    def delete_multiple_documents(self, document_ids: List[str]) -> Dict[str, Any]:
        """Delete multiple documents by IDs with detailed results."""
        if not document_ids:
            raise ValueError("document_ids cannot be empty")
        
        if not isinstance(document_ids, list):
            raise ValueError("document_ids must be a list")
        
        deleted_ids = []
        failed_ids = []
        
        for doc_id in document_ids:
            try:
                # Use the existing delete_document method
                self.delete_document(doc_id)
                deleted_ids.append(doc_id)
            except Exception as e:
                failed_ids.append({"id": doc_id, "error": str(e)})
        
        # Determine overall status
        if not failed_ids:
            status = "success"
        elif not deleted_ids:
            status = "error"
        else:
            status = "partial_success"
        
        return {
            "message": f"Deleted {len(deleted_ids)} of {len(document_ids)} documents",
            "deleted_ids": deleted_ids,
            "failed_ids": failed_ids,
            "total_requested": len(document_ids),
            "total_deleted": len(deleted_ids),
            "total_failed": len(failed_ids),
            "status": status
        }


# Global document service instance
document_service: Optional[DocumentService] = None


def get_document_service() -> DocumentService:
    """Get the global document service instance."""
    global document_service
    if document_service is None:
        document_service = DocumentService()
    return document_service