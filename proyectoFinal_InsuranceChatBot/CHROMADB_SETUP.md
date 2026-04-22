# ChromaDB Insurance Chatbot Setup

## Overview
Successfully created a ChromaDB vector database for insurance policy documents and integrated it with a chatbot using DeepSeek via OpenRouter API.

## What Was Accomplished

### 1. ChromaDB Database Creation
- **File**: `chroma_db_builder.py`
- **Purpose**: Processes PDF documents and structured data, creates vector embeddings, and stores in ChromaDB
- **Features**:
  - Extracts articles from PDF files using existing `data_ingestion.py`
  - Processes structured CSV data from `polizas_estructuradas.csv`
  - Uses `all-MiniLM-L6-v2` sentence transformer for embeddings
  - Stores 180 documents total (171 from PDFs + 9 from structured data)

### 2. ChromaDB RAG Core
- **File**: `chroma_rag_core.py`
- **Purpose**: Provides search and retrieval functionality over the ChromaDB
- **Features**:
  - Semantic search with configurable number of results (default k=3)
  - Filter by source type (pdf_extraction vs structured_data)
  - Filter by specific policy files
  - Context formatting for RAG applications
  - Collection statistics and metadata management

### 3. Insurance Chatbot
- **File**: `insurance_chatbot.py`
- **Purpose**: Main chatbot that combines ChromaDB retrieval with DeepSeek generation
- **Features**:
  - Uses OpenRouter API with DeepSeek chat model (`deepseek/deepseek-chat-v3.1:free`)
  - Retrieval-Augmented Generation (RAG) architecture
  - Spanish language support
  - Interactive chat interface
  - Configurable context window (default 5 documents)
  - Proper citation of policy articles and files

### 4. API Server
- **File**: `chatbot_api.py`
- **Purpose**: Flask API for web integration
- **Endpoints**:
  - `POST /chat` - Main chatbot interaction
  - `POST /search` - Direct document search
  - `GET /stats` - Database statistics
  - `GET /health` - Health check

### 5. Demo Applications
- **File**: `demo_chroma_usage.py`
- **Purpose**: Interactive demo of ChromaDB functionality

## Database Statistics
- **Total Documents**: 180
- **PDF Extractions**: 171 articles
- **Structured Data**: 9 records
- **Files Processed**: 9 PDF files
- **Embedding Model**: all-MiniLM-L6-v2

## Configuration Details

### Embedding Model
- **Model**: `all-MiniLM-L6-v2`
- **Provider**: SentenceTransformers
- **Dimensions**: 384
- **Language**: Multilingual (supports Spanish)

### Search Configuration
- **Default Results**: k=3 (configurable)
- **Distance Metric**: L2 (Euclidean)
- **Search Types**: 
  - Semantic search
  - Filtered search (by source, file)
  - Article-specific search

### LLM Configuration
- **Provider**: OpenRouter
- **Model**: `deepseek/deepseek-chat-v3.1:free`
- **API Key**: Provided in code
- **Temperature**: 0.1 (for consistent responses)
- **Max Tokens**: 1000

## File Structure
```
backend/
├── src/
│   ├── chroma_db_builder.py      # Database creation
│   ├── chroma_rag_core.py        # RAG functionality
│   ├── insurance_chatbot.py      # Main chatbot
│   ├── chatbot_api.py           # Flask API
│   ├── demo_chroma_usage.py     # Demo application
│   ├── data_ingestion.py        # Existing PDF processing
│   └── rag_core.py              # Original FAISS implementation
├── chroma_db/                   # ChromaDB storage
└── requirements.txt             # Updated dependencies
```

## Installation

### Prerequisites
Install dependencies using `uv` (recommended for faster package management):
```bash
# Install uv if not already installed
pip install uv

# Install project dependencies
cd backend
uv pip install -r requirements.txt
```

Alternatively, use standard pip:
```bash
cd backend
pip install -r requirements.txt
```

### Environment Setup
1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` and add your OpenRouter API key:
```bash
OPENROUTER_API_KEY=your_actual_api_key_here
```

**⚠️ SECURITY NOTE:** Never commit your `.env` file to version control. The API key should be kept private.

## Usage Instructions

### 1. Build the Database
```bash
cd backend/src
python chroma_db_builder.py
```

### 2. Run Interactive Chatbot
```bash
python insurance_chatbot.py
```

### 3. Start API Server
```bash
python chatbot_api.py
```

### 4. Example API Usage
```bash
# Chat endpoint
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Qué gastos médicos están cubiertos?"}'

# Search endpoint
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "hospitalización", "num_results": 3}'
```

## Key Features

### Retrieval Quality
- Semantic search using state-of-the-art embeddings
- Metadata filtering for precise results
- Configurable result count
- Source attribution and article citation

### Generation Quality
- Context-aware responses using DeepSeek
- Professional insurance domain language
- Spanish language support
- Proper citation of policy sources
- Conservative responses (only answers based on available context)

### Scalability
- ChromaDB persistent storage
- Vector indexing for fast search
- Configurable batch processing
- API-ready architecture

## Next Steps
1. Fine-tune search parameters based on user feedback
2. Add more sophisticated filtering options
3. Implement conversation history
4. Add authentication to API
5. Create web frontend
6. Add monitoring and logging
7. Optimize embedding model for insurance domain