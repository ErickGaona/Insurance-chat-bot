# Development Notes

## Package Management

### Use UV for Package Installation
For faster and more reliable package management, use `uv` instead of regular pip:

```bash
# Install uv (if not already installed)
pip install uv

# Install packages from requirements.txt
uv pip install -r requirements.txt

# Install individual packages
uv pip install chromadb sentence-transformers

# Install in development mode
uv pip install -e .
```

### Benefits of UV
- **Faster installation**: Up to 10-100x faster than pip
- **Better dependency resolution**: More reliable conflict resolution
- **Drop-in replacement**: Compatible with existing pip workflows
- **Better caching**: Reduces redundant downloads

## Current Dependencies
```
pandas
PyMuPDF
sentence-transformers
faiss-cpu
openai
numpy
chromadb
flask
flask-cors
```

## Environment Setup
```bash
# 1. Set up Python environment
pyenv shell 3.12.10

# 2. Install UV
pip install uv

# 3. Install project dependencies
cd backend
uv pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env file and add your OpenRouter API key

# 5. Verify installation
python -c "import chromadb; import openai; print('All packages installed successfully')"
```

## Security Notes
- **Never commit API keys** to version control
- Use `.env` file for local development
- Use environment variables in production
- The `.env` file is already in `.gitignore`

## Quick Start with UV
```bash
# Clone and setup project
git clone <repo-url>
cd proyectoFinal_InsuranceChatBot

# Install UV and dependencies
pip install uv
cd backend && uv pip install -r requirements.txt

# Build ChromaDB
cd src && python chroma_db_builder.py

# Run chatbot
python insurance_chatbot.py
```

## Performance Tips
- Use `uv pip sync requirements.txt` for reproducible installs
- Consider `uv pip compile` for generating lock files
- Use virtual environments for isolation
- Cache embeddings model downloads for faster startup

## Troubleshooting
- If UV installation fails, ensure you have the latest pip: `pip install --upgrade pip`
- For Windows, ensure PowerShell execution policy allows scripts
- For dependency conflicts, use `uv pip install --upgrade-strategy eager`