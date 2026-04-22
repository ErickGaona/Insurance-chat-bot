# 🏥 AnyoneAI Insurance Chatbot

> **Advanced RAG-powered Insurance Assistant with Modern Modular Architecture & Docker Support**

A sophisticated insurance policy chatbot that combines **ChromaDB vector search**, **Google Gemini 2.0 Flash**, and **semantic document processing** to provide accurate, context-aware responses about insurance policies and coverage. Features a fully modular **ES6 frontend architecture** and **containerized deployment**.

![AnyoneAI Logo](frontend/assets/anioneai.png)

## ✨ Features

### 🤖 **AI-Powered Responses**
- **Google Gemini 2.0 Flash**: Latest AI model for fast, accurate responses
- **Hybrid Search**: ChromaDB vector search + Brave web search for comprehensive coverage
- **Optimized Chunking**: 2000-character semantic chunks for better context preservation
- **Multi-language**: Spanish-optimized for insurance documents
- **Smart Context**: Automatically chooses between local DB and web search based on query type

### 🌐 **Hybrid Search Capabilities**
- **Local Knowledge**: 487+ optimized insurance document chunks with semantic search
- **Web Intelligence**: Real-time Brave Search API integration
- **Smart Routing**: Automatic detection of queries needing current information
- **Source Attribution**: Clear distinction between internal policies and web sources
- **Force Web Mode**: Option to manually trigger web search for any query

### 🎨 **Modern Modular Frontend**
- **ES6 Modules**: Fully refactored modular architecture (15+ organized modules)
- **Component System**: Reusable chat, document, stats, and UI components
- **Service Layer**: Centralized API communication and business logic
- **State Management**: Reactive state system with localStorage persistence
- **Error Handling**: Comprehensive error boundaries and user notifications
- **Real-time Updates**: Live statistics, document management, and chat functionality

### 🏗️ **Enterprise-Ready Architecture**
- **Modular Backend**: Clean Flask Blueprint architecture with service layers
- **RESTful API**: Versioned endpoints with proper error handling
- **Pydantic Validation**: Type-safe request/response models
- **Service Layer Pattern**: Separation of concerns for maintainability
- **Persistent Vector Database**: ChromaDB with 487+ optimized document chunks
- **Docker Support**: Full containerization with Docker Compose orchestration

## 🚀 Quick Start Options

### Option 1: Docker Deployment (Recommended)

**Prerequisites**: Docker and Docker Compose installed

1. **Clone the repository**:
```bash
git clone https://github.com/MichaelYnoa/proyectoFinal_InsuranceChatBot.git
cd proyectoFinal_InsuranceChatBot
```

2. **Set up environment variables**:
```bash
# Copy environment template
cp backend/.env.example backend/.env

# Edit with your API keys
GOOGLE_API_KEY=your_google_api_key_here
BRAVE_API_KEY=your_brave_api_key_here
```

3. **Start with Docker Compose**:
```bash
docker-compose up -d
```

4. **Access the application**:
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/v1/health

### Option 2: Local Development Setup

**Prerequisites**: Python 3.8+, Node.js (optional for advanced frontend dev)

#### Backend Setup

```bash
1. **Clone the repository**:
```bash
git clone https://github.com/MichaelYnoa/proyectoFinal_InsuranceChatBot.git
cd proyectoFinal_InsuranceChatBot
```

2. **Set up environment variables**:
```bash
# Create environment file in backend directory
cd backend
cp .env.example .env

# Edit .env with your API keys
GOOGLE_API_KEY=your_google_api_key_here
BRAVE_API_KEY=your_brave_api_key_here
```

3. **Install dependencies**:
```bash
# Install Python dependencies
pip install -r requirements.txt
```

4. **Build the knowledge base**:
```bash
# Navigate to source directory
cd src

# Build ChromaDB from insurance documents
python chroma_db_builder.py
```

5. **Start the backend**:
```bash
# Run the Flask API server
python main.py
```

6. **Start the frontend** (in a new terminal):
```bash
# Navigate to frontend directory
cd ../../frontend

# Start simple HTTP server
python -m http.server 8080
```

7. **Access the application**:
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:5000

#### Frontend Development Setup

The frontend uses modern ES6 modules with the following architecture:

```
frontend/js/
├── main.js              # Application entry point
├── config/
│   └── api-config.js    # API configuration
├── services/            # Business logic layer
│   ├── api-service.js   # HTTP client
│   ├── chat-service.js  # Chat functionality
│   ├── document-service.js # Document management
│   └── stats-service.js # Statistics
├── components/          # UI components
│   ├── chat-component.js
│   ├── document-component.js
│   ├── stats-component.js
│   ├── ui-component.js
│   └── error-component.js
├── utils/              # Utility functions
│   ├── dom-utils.js
│   ├── format-utils.js
│   ├── storage-utils.js
│   └── animation-utils.js
└── state/
    └── app-state.js    # Application state management
```

## 🐳 Docker Commands

### Development
```bash
# Build and start all services
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production
```bash
# Build for production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale services
docker-compose up --scale backend=2 frontend=1
```

### Maintenance
```bash
# Rebuild specific service
docker-compose build backend
docker-compose up -d backend

# Access container shell
docker-compose exec backend bash
docker-compose exec frontend sh

# View container stats
docker stats insurance-chatbot-backend insurance-chatbot-frontend
```

## 🔧 Configuration

### Environment Variables

**Backend (.env file)**:
```env
# AI Model Configuration
GOOGLE_API_KEY=your_google_api_key_here
BRAVE_API_KEY=your_brave_api_key_here
OPENROUTER_API_KEY=optional_fallback_key

# Application Settings
FLASK_ENV=development
CHROMA_DB_PATH=./chroma_db
UPLOAD_FOLDER=./uploads

# API Settings
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=pdf,txt,docx
```

**Frontend (js/config/api-config.js)**:
```javascript
export const API_CONFIG = {
    baseUrl: 'http://localhost:5000',
    endpoints: {
        chat: '/api/v1/chat',
        health: '/api/v1/health',
        stats: '/api/v1/stats',
        documents: '/api/v1/documents'
    },
    timeout: 30000
};
```

ChromaDB Collection Stats:
Total Documents: 692
Database Path: ../chroma_db
```

**What this does:**
- Processes all PDF files in `/data` directory
- Uses semantic chunking for optimal text segmentation
- Creates persistent ChromaDB with 692 total documents
- Generates embeddings using `all-MiniLM-L6-v2`
- Removes duplicate content automatically

### Step 5: Start the Backend API

```bash
# From backend/src directory
python main.py
```

**Expected output:**
```
🚀 Starting Enhanced Insurance Chatbot API with Hybrid Search...
🔍 Looking for ChromaDB at: C:\Projects\GitHub\proyectoFinal_InsuranceChatBot\backend\chroma_db
Connected to ChromaDB collection 'insurance_policies' with 692 documents.
✅ Connected to ChromaDB with 692 documents
✅ Standard chatbot initialized successfully
✅ Hybrid chatbot initialized successfully
🌐 Starting Flask server...
 * Running on http://127.0.0.1:5000
```

**API Endpoints available:**
- `POST /api/v1/chat` - Main chat endpoint with hybrid search
- `GET /api/v1/health` - System health check and capabilities
- `GET /api/v1/stats` - Database and usage statistics
- `POST /api/v1/documents/upload` - Upload new documents
- `GET /api/v1/documents` - List all documents
- `DELETE /api/v1/documents/{id}` - Delete specific document
- `POST /api/v1/search` - Direct document search

### Step 6: Start the Frontend Server

**Open a new terminal** and run:

```bash
# Navigate to frontend directory
cd frontend

# Start HTTP server for static files
python -m http.server 8080
```

**Expected output:**
```
Serving HTTP on :: port 8080 (http://[::]:8080/) ...
```

### Step 7: Open and Test

1. **Open your browser** and navigate to: **http://localhost:8080**
2. **Test the interface** with sample questions:
   - *"¿Qué tipos de seguros tienes?"*
   - *"¿Hay cobertura para COVID-19?"*
   - *"¿Qué coberturas tiene la póliza POL320190074?"*
   - *"¿Cuáles son los requisitos para hacer un reclamo?"*

### Step 8: Verify Everything Works

**Test the API directly** (optional):

```bash
# Test chat endpoint (new versioned API)
curl -X POST http://localhost:5000/api/v1/chat \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"message": "¿Qué tipos de seguros tienes?"}'

# Check system health and capabilities
curl http://localhost:5000/api/v1/health

# Check database statistics
curl http://localhost:5000/api/v1/stats
```

**Expected response:**
```json
{
  "answer": "Basándome en la información disponible, ofrezco seguros de...",
  "chatbot_type": "hybrid",
  "local_sources": 10,
  "web_sources": 3,
  "sources_used": 13,
  "status": "success",
  "used_web_search": true
}
```
  "question": "¿Hay cobertura para COVID-19?",
  "answer": "Sí, hay cobertura para COVID-19 según la información...",
  "sources_used": 5,
  "status": "success"
}
```

## 🛠️ Development Setup

### For Development Mode

If you want to modify the code and see changes in real-time:

```bash
# Backend with auto-reload
cd backend/src
export FLASK_ENV=development  # On Windows: set FLASK_ENV=development
python main.py

# Frontend with live reload (optional)
cd frontend
npx live-server --port=8080  # If you have Node.js
# Or use Python's built-in server (no auto-reload)
python -m http.server 8080
```

### Project Structure Overview

```
proyectoFinal_InsuranceChatBot/
├── .env                       # 🔒 Your API keys (create this)
├── backend/
│   ├── src/
│   │   ├── main.py           # 🚀 Application entry point
│   │   ├── api/              # 🌐 Modern Flask API architecture
│   │   │   ├── app.py        # Flask application factory
│   │   │   ├── config.py     # Configuration management
│   │   │   ├── extensions.py # CORS and extensions
│   │   │   └── routes/       # RESTful API endpoints
│   │   │       ├── health.py # Health check endpoint
│   │   │       ├── chat.py   # Chat functionality
│   │   │       ├── search.py # Search endpoints
│   │   │       ├── stats.py  # Statistics endpoints
│   │   │       └── documents.py # Document management
│   │   ├── services/         # 🎯 Business logic layer
│   │   │   ├── chatbot_service.py # Chatbot orchestration
│   │   │   └── document_service.py # Document operations
│   │   ├── models/           # 📋 Pydantic models
│   │   │   ├── request_models.py # API request validation
│   │   │   └── response_models.py # API response formatting
│   │   ├── utils/            # 🛠️ Utility functions
│   │   └── [legacy files]    # � To be refactored
│   ├── chroma_db/            # 💾 Persistent vector database
│   └── requirements.txt      # 📦 Python dependencies
├── frontend/
│   ├── index.html            # 🎨 Main web interface
│   ├── styles.css            # ✨ 3D styling & animations
│   ├── script.js             # ⚡ Chat functionality
│   └── assets/anioneai.png   # 🏷️ AnyoneAI logo
└── data/                     # 📁 Insurance documents
    ├── POL*.pdf              # Insurance policy PDFs
    └── structure_data/       # CSV data files
```

## ⚡ Quick Start (One-Liner)

For experienced developers, here's the quick setup:

```bash
git clone https://github.com/MichaelYnoa/proyectoFinal_InsuranceChatBot.git && \
cd proyectoFinal_InsuranceChatBot && \
echo "GOOGLE_API_KEY=your_key_here" > .env && \
echo "BRAVE_API_KEY=your_brave_key_here" >> .env && \
cd backend && pip install -r requirements.txt && \
cd src && python chroma_db_builder.py && \
python main.py &
cd ../../frontend && python -m http.server 8080
```

**Remember to replace the API keys with your actual keys!**

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Frontend (Port 8080)                 │
│  • Modern HTML/CSS/JS interface                            │
│  • 3D animations & AnyoneAI branding                       │
│  • Real-time chat with typing indicators                   │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP REST API
┌─────────────────────▼───────────────────────────────────────┐
│             Flask API Server (Port 5000)                   │
│  • /api/v1/chat - Main chat endpoint                       │
│  • /api/v1/health - System health check                    │
│  • /api/v1/stats - Database statistics                     │
│  • /api/v1/documents/* - Document management               │
│  • Modern Blueprint architecture with service layers       │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Service Layer (Business Logic)                │
│  • ChatbotService - Orchestrates chatbot instances         │
│  • DocumentService - Handles document operations           │
│  • Pydantic models for request/response validation         │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│         Hybrid Insurance Chatbot Core                      │
│  • Standard Chatbot (ChromaDB only)                        │
│  • Hybrid Chatbot (ChromaDB + Brave Search)                │
│  • Google Gemini 2.0 Flash integration                     │
│  • Smart search strategy selection                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                ChromaDB Vector Database                     │
│  • 692+ documents with semantic embeddings                 │
│  • Sentence-transformers embeddings                        │
│  • Persistent storage with duplicate removal               │
│  • Optimized retrieval for 1000-char chunks                │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
proyectoFinal_InsuranceChatBot/
├── 🌐 frontend/                    # Modern web interface
│   ├── index.html                  # Main HTML file
│   ├── styles.css                  # 3D styling & animations  
│   ├── script.js                   # Chat functionality
│   └── assets/anioneai.png         # AnyoneAI logo
├── 🔧 backend/                     # Modular backend architecture
│   ├── src/
│   │   ├── main.py                 # Application entry point
│   │   ├── api/                    # Flask Blueprint architecture
│   │   │   ├── app.py              # Application factory
│   │   │   ├── config.py           # Configuration management
│   │   │   ├── extensions.py       # CORS and extensions
│   │   │   └── routes/             # API endpoints
│   │   │       ├── health.py       # Health check
│   │   │       ├── chat.py         # Chat functionality
│   │   │       ├── stats.py        # Statistics
│   │   │       └── documents.py    # Document management
│   │   ├── services/               # Business logic layer
│   │   │   ├── chatbot_service.py  # Chatbot orchestration
│   │   │   └── document_service.py # Document operations
│   │   ├── models/                 # Pydantic models
│   │   │   ├── request_models.py   # Request validation
│   │   │   └── response_models.py  # Response formatting
│   │   ├── utils/                  # Utility functions
│   │   └── [legacy files]          # To be refactored
│   ├── chroma_db/                  # Persistent vector DB
│   └── requirements.txt            # Python dependencies
├── 📄 data/                        # Insurance documents
│   ├── POL*.pdf                    # Policy PDF files
│   └── structure_data/             # CSV data
├── 🔒 .env                         # Environment variables
├── 📋 refactor backend.md          # Backend refactoring guide
├── 📋 frontend/refactor frontend.md # Frontend refactoring guide
└── 📖 readme.md                    # This file
```

## 🔧 Technical Details

### Database Performance
- **Documents Indexed**: 692 total (after duplicate removal)
- **Content Strategy**: 1000-character semantic chunking
- **Embedding Model**: `all-MiniLM-L6-v2` (384 dimensions)
- **Storage**: Persistent ChromaDB on disk
- **Retrieval**: Optimized for smaller chunks (10-15 documents per query)

### AI Model Configuration
- **Primary**: Google Gemini 2.0 Flash Experimental
- **Hybrid Search**: ChromaDB + Brave Search API
- **Temperature**: 0.1 (factual responses)
- **Max Output**: 1000 tokens
- **Context Window**: Up to 10 local + 3 web sources per query

### Modern Architecture Features
- **API Versioning**: `/api/v1/*` endpoints for future compatibility
- **Request Validation**: Pydantic models for type safety
- **Error Handling**: Centralized error management with user-friendly messages
- **Service Layer**: Clean separation between API routes and business logic
- **Blueprint Pattern**: Modular Flask architecture for scalability
- **CORS Configuration**: Proper headers for frontend communication

### Frontend Features
- **Real-time Chat**: Seamless user experience
- **3D Animations**: Perspective transforms and shadows
- **Loading States**: Animated typing dots
- **Statistics Tracking**: Questions, sources, response times
- **Chat History**: Local storage persistence
- **UTF-8 Support**: Proper handling of Spanish characters

## 🎯 Key Improvements Made

### ✅ **Complete Backend Refactoring**
- **From**: Monolithic 1212-line `chatbot_api.py`
- **To**: Modular Flask Blueprint architecture
- **Benefits**: Maintainable, scalable, testable code structure
- **Features**: Service layers, Pydantic models, proper error handling

### ✅ **Database Optimization**
- **Content**: Rebuilt ChromaDB with 692 documents
- **Deduplication**: Removed 24 duplicate documents
- **Chunking**: 1000-character semantic boundaries
- **Retrieval**: Optimized for smaller chunks (10-15 docs vs 3-5)

### ✅ **Frontend-Backend Integration**
- **API Versioning**: `/api/v1/*` endpoints
- **CORS Fixes**: Resolved preflight redirect issues
- **UTF-8 Support**: Proper Spanish character encoding
- **Error Handling**: User-friendly error messages

### ✅ **Enhanced Search Capabilities**
- **Hybrid Mode**: ChromaDB + Brave Search integration
- **Smart Routing**: Automatic search strategy selection
- **Web Fallback**: External sources when local knowledge insufficient
- **Source Attribution**: Clear distinction between local and web sources

### ✅ **Developer Experience**
- **Documentation**: Comprehensive refactoring guides
- **Testing**: API endpoint validation
- **Debugging**: Enhanced error logging and troubleshooting
- **Architecture**: Clean separation of concerns

## 🧪 Testing

Test the system with these sample questions:

```bash
# Basic insurance inquiry
curl -X POST http://localhost:5000/api/v1/chat \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"message": "¿Qué tipos de seguros tienes?"}'

# COVID-19 Coverage
curl -X POST http://localhost:5000/api/v1/chat \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"message": "¿Hay cobertura para COVID-19?"}'

# Policy Coverage
curl -X POST http://localhost:5000/api/v1/chat \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"message": "¿Qué coberturas tiene la póliza POL320190074?"}'

# System Health Check
curl http://localhost:5000/api/v1/health

# Database Statistics  
curl http://localhost:5000/api/v1/stats
```

**Expected Response Format:**
```json
{
  "answer": "Detailed response based on insurance documents...",
  "chatbot_type": "hybrid",
  "local_sources": 10,
  "web_sources": 3,
  "sources_used": 13,
  "status": "success",
  "used_web_search": true,
  "search_strategy": "hybrid"
}
```

## 🌟 Future Enhancements

## 📡 API Documentation

### Chat Endpoint
```http
POST /api/v1/chat
Content-Type: application/json

{
    "message": "¿Qué coberturas tiene la póliza?",
    "verbose": false,
    "force_web_search": false
}
```

**Response:**
```json
{
    "question": "¿Qué coberturas tiene la póliza?",
    "answer": "Las pólizas incluyen coberturas para...",
    "sources_used": 3,
    "local_sources": 3,
    "web_sources": 0,
    "search_strategy": "local_only",
    "used_web_search": false,
    "chatbot_type": "hybrid",
    "status": "success"
}
```

### Health Check
```http
GET /api/v1/health
```

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "1.0.0",
    "database": {
        "status": "connected",
        "documents": 487,
        "last_updated": "2024-01-15T09:00:00Z"
    },
    "services": {
        "chatbot": "ready",
        "hybrid_search": "ready",
        "web_search": "ready"
    }
}
```

### Statistics
```http
GET /api/v1/stats
```

**Response:**
```json
{
    "total_documents": 487,
    "total_interactions": 1250,
    "avg_response_time": 0.85,
    "web_searches_count": 45,
    "local_searches_count": 1205,
    "status": "success"
}
```

### Document Management
```http
POST /api/v1/documents/
Content-Type: multipart/form-data

file: [PDF file]
title: "Policy Document"
```

```http
GET /api/v1/documents/?limit=20&offset=0
```

```http
DELETE /api/v1/documents/{document_id}
```

## 🏗️ Architecture Overview

### System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                   Web Frontend (Port 8080)                 │
│  🎨 Modern ES6 Modular Architecture                        │
│  📱 Responsive design with 3D effects                      │
│  ⚡ Real-time updates and chat functionality               │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP REST API
┌─────────────────────▼───────────────────────────────────────┐
│            Flask API Server (Port 5000)                    │
│  🔌 RESTful endpoints with proper error handling           │
│  📋 Pydantic validation and Blueprint architecture         │
│  🛡️ Service layer pattern for business logic              │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│           Hybrid Insurance Chatbot Core                    │
│  🤖 Google Gemini 2.0 Flash integration                   │
│  🔍 ChromaDB + Brave Search hybrid approach                │
│  🧠 Smart search strategy selection                        │
│  📊 Source attribution and response quality                │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              ChromaDB Vector Database                       │
│  📚 487+ optimized document chunks (2000 chars each)       │
│  🔢 Sentence-transformers embeddings (all-MiniLM-L6-v2)    │
│  💾 Persistent storage with duplicate prevention           │
│  ⚡ Fast semantic search and retrieval                     │
└─────────────────────────────────────────────────────────────┘
```

### Modular Frontend Architecture
```
frontend/js/
├── 🚀 main.js              # Application bootstrap
├── ⚙️ config/
│   └── api-config.js       # Centralized configuration
├── 🔧 services/            # Business logic layer
│   ├── api-service.js      # HTTP client with error handling
│   ├── chat-service.js     # Chat functionality and history
│   ├── document-service.js # Document upload/management
│   └── stats-service.js    # Real-time statistics
├── 🧩 components/          # UI component system
│   ├── chat-component.js   # Chat interface and messaging
│   ├── document-component.js # Document management UI
│   ├── stats-component.js  # Statistics dashboard
│   ├── ui-component.js     # Common UI elements
│   └── error-component.js  # Error handling and display
├── 🛠️ utils/              # Utility functions
│   ├── dom-utils.js        # DOM manipulation helpers
│   ├── format-utils.js     # Text and data formatting
│   ├── storage-utils.js    # LocalStorage management
│   └── animation-utils.js  # Animation and transition helpers
└── 📊 state/
    └── app-state.js        # Reactive state management
```

## 🚀 Roadmap

- [x] **✅ Complete Backend Refactoring**: Modern Flask Blueprint architecture with service layers
- [x] **✅ Frontend Modularization**: ES6 modules replacing 1400-line monolithic script
- [x] **✅ Optimized Document Chunking**: Better semantic chunking with 2000-char chunks
- [x] **✅ Docker Support**: Full containerization with Docker Compose
- [ ] **Multi-modal Support**: Image and document upload capabilities
- [ ] **Advanced Analytics**: Usage tracking and performance insights
- [ ] **API Rate Limiting**: Production-ready scalability and throttling
- [ ] **Authentication System**: User management and access control
- [ ] **Real-time Updates**: WebSocket integration for live chat
- [ ] **Testing Suite**: Comprehensive unit and integration tests

## 🧪 Testing

### Manual Testing Checklist
- [ ] **Chat functionality**: Send messages and receive responses
- [ ] **Document upload**: Upload PDF files and see them in document list
- [ ] **Text document creation**: Create documents via text input
- [ ] **Document management**: Edit and delete documents
- [ ] **Statistics updates**: Verify real-time counter updates
- [ ] **Error handling**: Test invalid inputs and network errors
- [ ] **Responsive design**: Test on different screen sizes

### API Testing
```bash
# Test health endpoint
curl http://localhost:5000/api/v1/health

# Test chat endpoint
curl -X POST http://localhost:5000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Qué tipos de seguros tienes?"}'

# Test statistics
curl http://localhost:5000/api/v1/stats
```

## 🐳 Production Deployment

### Docker Compose Production
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
    
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

### Environment Variables for Production
```env
# Production settings
FLASK_ENV=production
DEBUG=False
CORS_ORIGINS=https://yourdomain.com

# Security
SECRET_KEY=your-secret-key-here
SSL_REDIRECT=True

# Performance
WORKERS=4
TIMEOUT=30
```

- [ ] **Complete Backend Refactoring**: Consolidate legacy components into service modules
- [ ] **Frontend Modularization**: Break 1400-line script.js into ES6 modules
- [ ] **Multi-modal Support**: Image and document upload capabilities
- [ ] **Advanced Analytics**: Usage tracking and performance insights
- [ ] **API Rate Limiting**: Production-ready scalability and throttling
- [ ] **Authentication System**: User management and access control
- [ ] **Real-time Updates**: WebSocket integration for live chat
- [ ] **Testing Suite**: Comprehensive unit and integration tests

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is part of a final project for educational purposes.

## 🆘 Support

If you encounter any issues:

1. **Check Environment Variables**: Ensure API keys are properly set in `.env` file
2. **Verify Database**: Run `chroma_db_builder.py` if search results are missing
3. **Port Conflicts**: Use different ports if 8080/5000 are occupied
4. **Dependencies**: Update packages with `pip install -r requirements.txt`
5. **API Endpoints**: Ensure you're using the new `/api/v1/*` endpoints
6. **CORS Issues**: Verify frontend and backend are running on correct ports
7. **UTF-8 Encoding**: Check that Spanish characters are properly encoded

### Common Issues:

**"Error al comunicarse con el servidor"**
- Check that backend is running on port 5000
- Verify frontend is accessing correct API endpoints
- Ensure CORS is properly configured

**"No documents found"**
- Rebuild ChromaDB with `python chroma_db_builder.py`
- Check that PDF files exist in `/data` directory
- Verify ChromaDB path configuration

**"API key errors"**
- Confirm `.env` file exists in project root
- Verify API keys are valid and properly formatted
- Check API key permissions and quotas

---

**Built with ❤️ by AnyoneAI** | **Powered by Google Gemini 2.0 Flash & ChromaDB** | **Modern Flask Architecture**