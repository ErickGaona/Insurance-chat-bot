# 🚀 Quick Start Guide

## 30-Second Docker Setup (Recommended)

```bash
# 1. Clone and navigate
git clone https://github.com/MichaelYnoa/proyectoFinal_InsuranceChatBot.git
cd proyectoFinal_InsuranceChatBot

# 2. Set up environment
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# 3. Start with Docker
docker-compose up -d

# 4. Open browser
open http://localhost:8080
```

## 2-Minute Local Setup

### Windows
```cmd
# 1. Clone and run setup
git clone https://github.com/MichaelYnoa/proyectoFinal_InsuranceChatBot.git
cd proyectoFinal_InsuranceChatBot
setup.bat
```

### Linux/macOS
```bash
# 1. Clone and run setup
git clone https://github.com/MichaelYnoa/proyectoFinal_InsuranceChatBot.git
cd proyectoFinal_InsuranceChatBot
chmod +x setup.sh
./setup.sh
```

## Manual Setup (5 minutes)

```bash
# 1. Clone
git clone https://github.com/MichaelYnoa/proyectoFinal_InsuranceChatBot.git
cd proyectoFinal_InsuranceChatBot

# 2. Environment
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# 3. Backend
cd backend
pip install -r requirements.txt
cd src
python chroma_db_builder.py
python main.py &

# 4. Frontend (new terminal)
cd ../../frontend
python -m http.server 8080
```

## Required API Keys

Get these free API keys:

1. **Google API Key**: https://makersuite.google.com/app/apikey
2. **Brave Search API**: https://api.search.brave.com/

Add to `backend/.env`:
```env
GOOGLE_API_KEY=your_google_api_key_here
BRAVE_API_KEY=your_brave_api_key_here
```

## Test the Setup

Visit http://localhost:8080 and try:
- "¿Qué tipos de seguros tienes?"
- "¿Hay cobertura para COVID-19?"
- Upload a PDF document

## Troubleshooting

**Port conflicts**: Change ports in docker-compose.yml or use different ports
**API errors**: Verify API keys in backend/.env
**Database issues**: Run `python chroma_db_builder.py` to rebuild

## Next Steps

- Explore the modular frontend architecture in `frontend/js/`
- Check API documentation at http://localhost:5000/api/v1/health
- Upload your own insurance documents
- Customize the chat responses and UI

## Architecture

- **Frontend**: Modern ES6 modules, component-based
- **Backend**: Flask REST API with service layers
- **Database**: ChromaDB vector database (487+ documents)
- **AI**: Google Gemini 2.0 Flash + Brave Search
- **Deployment**: Docker Compose orchestration