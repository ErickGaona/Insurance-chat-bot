# Frontend API Migration Notes

## Updated Endpoints

### Chat API
- **Old**: `POST /chat`
- **New**: `POST /api/v1/chat`
- **Response**: Same format (answer, sources_used, local_sources, web_sources, etc.)

### Health Check
- **Old**: `GET /health`
- **New**: `GET /api/v1/health`
- **Response**: Same format

### Statistics
- **Old**: `GET /stats`
- **New**: `GET /api/v1/stats`
- **Response**: Same format

### Document Operations
- **Old**: `POST /add_document`
- **New**: `POST /api/v1/documents/`
- **Changes**: 
  - Text input now uses `{text, title, metadata}` instead of `{text, title, document_type, source}`
  - Response format changed from `{new_total_documents}` to `{documents_added}`

- **Old**: `GET /list_documents`
- **New**: `GET /api/v1/documents/`
- **Changes**:
  - Uses `limit` and `offset` instead of `page` and `per_page`
  - No longer returns pagination metadata
  - Simplified pagination in frontend

- **Old**: `POST /delete_documents`
- **New**: `DELETE /api/v1/documents/`
- **Changes**: Same request/response format

## Frontend Changes Made

1. Updated all API endpoints to use `/api/v1/` prefix
2. Modified document upload to use new request format
3. Simplified pagination due to API changes
4. Updated document count handling to use stats refresh instead of direct count
5. Maintained backward compatibility for all chat features

## Test Checklist

- [ ] Chat functionality works
- [ ] Health check displays server status
- [ ] Statistics load correctly
- [ ] Text document upload works
- [ ] PDF document upload works
- [ ] Document listing and pagination work
- [ ] Document deletion works
- [ ] Clear chat history button works