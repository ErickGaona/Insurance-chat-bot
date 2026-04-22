@echo off
REM Insurance Chatbot Setup Script for Windows
REM This script sets up the complete development environment

echo 🏥 AnyoneAI Insurance Chatbot Setup (Windows)
echo ============================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed.
    echo Please install Python 3.8+ from https://python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found

REM Setup environment variables
echo ⚙️ Setting up environment...
if not exist "backend\.env" (
    copy "backend\.env.example" "backend\.env"
    echo 📝 Created backend\.env from template
    echo 🔑 Please edit backend\.env with your API keys:
    echo    - GOOGLE_API_KEY (required)
    echo    - BRAVE_API_KEY (required for web search)
    echo.
    notepad "backend\.env"
    pause
) else (
    echo ✅ Environment file already exists
)

REM Install dependencies
echo 📦 Installing Python dependencies...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    python -m venv venv
    echo ✅ Created virtual environment
)

REM Activate virtual environment and install dependencies
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo ✅ Dependencies installed

REM Build ChromaDB
echo 🗄️ Building ChromaDB knowledge base...
cd src
python chroma_db_builder.py
echo ✅ ChromaDB built successfully
cd ..\..

REM Ask if user wants to start services
echo.
set /p start_services="🚀 Start services now? (y/n): "
if /i "%start_services%"=="y" (
    echo 🚀 Starting services...
    
    REM Start backend
    echo Starting backend server...
    cd backend\src
    call ..\venv\Scripts\activate.bat
    start "Backend Server" python main.py
    cd ..\..
    
    REM Wait a moment for backend to start
    timeout /t 5 /nobreak >nul
    
    REM Start frontend
    echo Starting frontend server...
    cd frontend
    start "Frontend Server" python -m http.server 8080
    cd ..
    
    echo ✅ Services started!
    echo.
    echo 🌐 Application URLs:
    echo    Frontend: http://localhost:8080
    echo    Backend API: http://localhost:5000
    echo    Health Check: http://localhost:5000/api/v1/health
    echo.
    echo 🛑 Close the terminal windows to stop services
) else (
    echo ℹ️ Services not started. Run the following to start manually:
    echo    Backend: cd backend\src ^&^& call ..\venv\Scripts\activate.bat ^&^& python main.py
    echo    Frontend: cd frontend ^&^& python -m http.server 8080
)

echo.
echo 🎉 Setup complete! Enjoy your AI insurance assistant!
pause