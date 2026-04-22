"""Response models for API serialization."""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime


class BaseResponse(BaseModel):
    """Base response model with common fields."""
    status: str = Field(..., description="Response status (success, error, partial_success)")


class ErrorResponse(BaseResponse):
    """Response model for errors."""
    error: str = Field(..., description="Error message")
    status: str = Field("error", description="Always 'error' for error responses")


class HealthResponse(BaseResponse):
    """Response model for health check."""
    chatbot_ready: bool = Field(..., description="Whether the standard chatbot is ready")
    hybrid_chatbot_ready: bool = Field(..., description="Whether the hybrid chatbot is ready")
    chatbot_type: str = Field(..., description="Type of chatbot available (hybrid, standard, none)")
    status: str = Field("healthy", description="Health status")


class DetailedHealthResponse(HealthResponse):
    """Detailed health response with additional information."""
    service_initialized: bool = Field(..., description="Whether the service is initialized")
    chroma_db_path: str = Field(..., description="Path to ChromaDB")


class ChatResponse(BaseResponse):
    """Response model for chat endpoints."""
    question: str = Field(..., description="The user's question")
    answer: str = Field(..., description="The chatbot's answer")
    sources_used: int = Field(..., description="Number of sources used in the response")
    local_sources: int = Field(..., description="Number of local sources used")
    web_sources: int = Field(..., description="Number of web sources used")
    search_strategy: str = Field(..., description="Search strategy used (local_only, hybrid, web_only)")
    used_web_search: bool = Field(..., description="Whether web search was used")
    chatbot_type: str = Field(..., description="Type of chatbot used (hybrid, standard)")
    status: str = Field("success", description="Response status")
    
    # Optional verbose fields
    search_results: Optional[List[Dict[str, Any]]] = Field(None, description="Detailed search results (verbose mode)")
    search_metadata: Optional[Dict[str, Any]] = Field(None, description="Search metadata (verbose mode)")
    context_docs: Optional[List[Dict[str, Any]]] = Field(None, description="Context documents (verbose mode)")


class SearchResponse(BaseResponse):
    """Response model for search endpoints."""
    query: str = Field(..., description="The search query")
    results: List[Dict[str, Any]] = Field(..., description="Search results")
    num_results: int = Field(..., description="Number of results returned")
    search_type: str = Field(..., description="Type of search performed (hybrid, local_only)")
    status: str = Field("success", description="Response status")


class HybridSearchResponse(SearchResponse):
    """Response model for hybrid search endpoints."""
    search_metadata: Dict[str, Any] = Field(..., description="Hybrid search metadata")
    forced_web_search: bool = Field(..., description="Whether web search was forced")


class DocumentMetadata(BaseModel):
    """Model for document metadata."""
    source: str = Field(..., description="Document source")
    title: str = Field(..., description="Document title")
    document_type: str = Field(..., description="Document type (pdf, text)")
    upload_date: Optional[str] = Field(None, description="Upload date")
    article_index: Optional[int] = Field(None, description="Article index within document")
    total_articles: Optional[int] = Field(None, description="Total articles in document")


class DocumentInfo(BaseModel):
    """Model for document information."""
    id: str = Field(..., description="Document ID")
    title: str = Field(..., description="Document title")
    source: str = Field(..., description="Document source")
    document_type: str = Field(..., description="Document type")
    upload_date: Optional[str] = Field(None, description="Upload date")
    metadata: DocumentMetadata = Field(..., description="Full document metadata")


class DocumentResponse(BaseResponse):
    """Response model for single document operations."""
    id: str = Field(..., description="Document ID")
    content: str = Field(..., description="Document content")
    metadata: Dict[str, Any] = Field(..., description="Document metadata")
    status: str = Field("success", description="Response status")


class DocumentListResponse(BaseResponse):
    """Response model for document listing."""
    documents: List[DocumentInfo] = Field(..., description="List of documents")
    total_returned: int = Field(..., description="Number of documents returned")
    offset: int = Field(..., description="Pagination offset")
    limit: Optional[int] = Field(None, description="Pagination limit")
    status: str = Field("success", description="Response status")


class DocumentCreationResponse(BaseResponse):
    """Response model for document creation."""
    message: str = Field(..., description="Success message")
    documents_added: int = Field(..., description="Number of documents added")
    source: str = Field(..., description="Document source")
    document_ids: List[str] = Field(..., description="List of created document IDs")
    status: str = Field("success", description="Response status")


class DocumentDeletionResponse(BaseResponse):
    """Response model for single document deletion."""
    message: str = Field(..., description="Success message")
    deleted_id: str = Field(..., description="ID of deleted document")
    status: str = Field("success", description="Response status")


class FailedOperation(BaseModel):
    """Model for failed operations in batch requests."""
    id: str = Field(..., description="Document ID that failed")
    error: str = Field(..., description="Error message")


class BatchDeletionResponse(BaseResponse):
    """Response model for batch document deletion."""
    message: str = Field(..., description="Summary message")
    deleted_ids: List[str] = Field(..., description="Successfully deleted document IDs")
    failed_ids: List[FailedOperation] = Field(..., description="Failed deletions with errors")
    total_requested: int = Field(..., description="Total number of documents requested for deletion")
    total_deleted: int = Field(..., description="Total number successfully deleted")
    total_failed: int = Field(..., description="Total number that failed")
    status: str = Field(..., description="Response status (success, partial_success, error)")


class DocumentSearchResult(BaseModel):
    """Model for document search results."""
    id: str = Field(..., description="Document ID")
    content: str = Field(..., description="Document content")
    metadata: Dict[str, Any] = Field(..., description="Document metadata")
    similarity_score: float = Field(..., description="Similarity score (0-1)")


class DocumentSearchResponse(BaseResponse):
    """Response model for document search."""
    query: str = Field(..., description="Search query")
    results: List[DocumentSearchResult] = Field(..., description="Search results")
    num_results: int = Field(..., description="Number of results returned")
    status: str = Field("success", description="Response status")


class CollectionStats(BaseModel):
    """Model for collection statistics."""
    collection_name: str = Field(..., description="Collection name")
    total_docs: int = Field(..., description="Total number of documents")
    database_path: str = Field(..., description="Database path")
    hybrid_search_available: bool = Field(..., description="Whether hybrid search is available")
    web_search_available: bool = Field(..., description="Whether web search is available")


class StatsResponse(BaseResponse):
    """Response model for statistics."""
    stats: CollectionStats = Field(..., description="Collection statistics")
    chatbot_type: str = Field(..., description="Chatbot type")
    status: str = Field("success", description="Response status")


class DetailedStats(BaseModel):
    """Model for detailed document statistics."""
    collection_name: str = Field(..., description="Collection name")
    total_docs: int = Field(..., description="Total number of documents")
    database_path: str = Field(..., description="Database path")
    source_breakdown: Dict[str, int] = Field(..., description="Breakdown by source")
    document_type_breakdown: Dict[str, int] = Field(..., description="Breakdown by document type")
    file_extension_breakdown: Dict[str, int] = Field(..., description="Breakdown by file extension")
    total_unique_sources: int = Field(..., description="Total unique sources")
    upload_dates: List[str] = Field(..., description="List of upload dates")
    latest_upload: Optional[str] = Field(None, description="Latest upload date")
    earliest_upload: Optional[str] = Field(None, description="Earliest upload date")


class DetailedStatsResponse(BaseResponse):
    """Response model for detailed statistics."""
    detailed_stats: DetailedStats = Field(..., description="Detailed statistics")
    status: str = Field("success", description="Response status")