#!/bin/bash

# Insurance Chatbot Setup Script
# This script sets up the complete development environment

set -e  # Exit on any error

echo "🏥 AnyoneAI Insurance Chatbot Setup"
echo "===================================="

# Check if required tools are installed
check_requirements() {
    echo "📋 Checking requirements..."
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required but not installed."
        exit 1
    fi
    
    if ! command -v git &> /dev/null; then
        echo "❌ Git is required but not installed."
        exit 1
    fi
    
    echo "✅ Requirements satisfied"
}

# Setup environment variables
setup_environment() {
    echo "⚙️ Setting up environment..."
    
    if [ ! -f "backend/.env" ]; then
        cp backend/.env.example backend/.env
        echo "📝 Created backend/.env from template"
        echo "🔑 Please edit backend/.env with your API keys:"
        echo "   - GOOGLE_API_KEY (required)"
        echo "   - BRAVE_API_KEY (required for web search)"
        echo ""
        read -p "Press Enter to continue after updating API keys..."
    else
        echo "✅ Environment file already exists"
    fi
}

# Install Python dependencies
install_dependencies() {
    echo "📦 Installing Python dependencies..."
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo "✅ Created virtual environment"
    fi
    
    # Activate virtual environment
    source venv/bin/activate || . venv/Scripts/activate
    
    # Install dependencies
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo "✅ Dependencies installed"
    cd ..
}

# Build ChromaDB
build_database() {
    echo "🗄️ Building ChromaDB knowledge base..."
    cd backend/src
    
    # Activate virtual environment
    source ../venv/bin/activate || . ../venv/Scripts/activate
    
    python chroma_db_builder.py
    
    echo "✅ ChromaDB built successfully"
    cd ../..
}

# Start services
start_services() {
    echo "🚀 Starting services..."
    
    # Start backend in background
    echo "Starting backend server..."
    cd backend/src
    source ../venv/bin/activate || . ../venv/Scripts/activate
    python main.py &
    BACKEND_PID=$!
    cd ../..
    
    # Wait for backend to start
    echo "⏳ Waiting for backend to start..."
    sleep 5
    
    # Start frontend
    echo "Starting frontend server..."
    cd frontend
    python3 -m http.server 8080 &
    FRONTEND_PID=$!
    cd ..
    
    echo "✅ Services started!"
    echo ""
    echo "🌐 Application URLs:"
    echo "   Frontend: http://localhost:8080"
    echo "   Backend API: http://localhost:5000"
    echo "   Health Check: http://localhost:5000/api/v1/health"
    echo ""
    echo "🛑 To stop services:"
    echo "   kill $BACKEND_PID $FRONTEND_PID"
    echo ""
    echo "📝 Backend PID: $BACKEND_PID"
    echo "📝 Frontend PID: $FRONTEND_PID"
}

# Main setup flow
main() {
    check_requirements
    setup_environment
    install_dependencies
    build_database
    
    echo ""
    read -p "🚀 Start services now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_services
    else
        echo "ℹ️ Services not started. Run the following to start manually:"
        echo "   Backend: cd backend/src && source ../venv/bin/activate && python main.py"
        echo "   Frontend: cd frontend && python3 -m http.server 8080"
    fi
    
    echo ""
    echo "🎉 Setup complete! Enjoy your AI insurance assistant!"
}

# Run main function
main "$@"