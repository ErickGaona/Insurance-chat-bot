"""Request models for API validation."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class ChatRequest(BaseModel):
    """Request model for chat endpoints."""
    message: str = Field(..., min_length=1, max_length=500, description="The user's message")
    verbose: bool = Field(False, description="Whether to include verbose response data")
    force_web_search: bool = Field(False, description="Whether to force web search in hybrid mode")
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty or whitespace only')
        return v.strip()


class SearchRequest(BaseModel):
    """Request model for search endpoints."""
    query: str = Field(..., min_length=1, max_length=200, description="The search query")
    num_results: int = Field(10, ge=1, le=50, description="Number of results to return")
    include_metadata: bool = Field(True, description="Whether to include metadata in results")
    force_web_search: bool = Field(False, description="Whether to force web search")
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty or whitespace only')
        return v.strip()


class DocumentUploadRequest(BaseModel):
    """Request model for document upload metadata."""
    title: Optional[str] = Field(None, max_length=200, description="Document title")
    description: Optional[str] = Field(None, max_length=1000, description="Document description")
    tags: Optional[str] = Field(None, max_length=500, description="Comma-separated tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class DocumentTextRequest(BaseModel):
    """Request model for direct text document creation."""
    text: str = Field(..., min_length=1, max_length=50000, description="The document text content")
    title: str = Field(..., min_length=1, max_length=200, description="Document title")
    description: Optional[str] = Field(None, max_length=1000, description="Document description")
    tags: Optional[List[str]] = Field(None, description="List of tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('Text content cannot be empty or whitespace only')
        return v.strip()
    
    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()


class DocumentSearchRequest(BaseModel):
    """Request model for document search."""
    query: str = Field(..., min_length=1, max_length=200, description="The search query")
    num_results: int = Field(10, ge=1, le=100, description="Number of results to return")
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty or whitespace only')
        return v.strip()


class DeleteMultipleDocumentsRequest(BaseModel):
    """Request model for deleting multiple documents."""
    document_ids: List[str] = Field(..., min_items=1, max_items=100, description="List of document IDs to delete")
    
    @validator('document_ids')
    def validate_document_ids(cls, v):
        # Remove duplicates while preserving order
        seen = set()
        unique_ids = []
        for doc_id in v:
            if doc_id not in seen:
                seen.add(doc_id)
                unique_ids.append(doc_id)
        
        # Validate each ID is not empty
        for doc_id in unique_ids:
            if not doc_id or not doc_id.strip():
                raise ValueError('Document IDs cannot be empty')
        
        return unique_ids


class PaginationRequest(BaseModel):
    """Request model for pagination parameters."""
    limit: Optional[int] = Field(None, ge=1, le=1000, description="Maximum number of items to return")
    offset: int = Field(0, ge=0, description="Number of items to skip")


class DocumentUpdateRequest(BaseModel):
    """Request model for document updates."""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="New document title")
    description: Optional[str] = Field(None, max_length=1000, description="New document description")
    tags: Optional[List[str]] = Field(None, description="New list of tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="New metadata")
    
    @validator('title')
    def validate_title(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip() if v else v