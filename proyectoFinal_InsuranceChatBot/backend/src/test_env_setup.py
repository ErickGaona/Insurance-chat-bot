"""
Test script to verify environment variable setup
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_env_setup():
    """Test that environment variables are properly configured"""
    
    print("Testing environment variable setup...")
    print("=" * 50)
    
    # Check if API key is available
    api_key = os.getenv('OPENROUTER_API_KEY')
    
    if api_key:
        # Only show first and last 4 characters for security
        masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***"
        print(f"✅ OPENROUTER_API_KEY found: {masked_key}")
    else:
        print("❌ OPENROUTER_API_KEY not found!")
        print("   Please:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your OpenRouter API key to the .env file")
        return False
    
    # Test optional environment variables
    model = os.getenv('OPENROUTER_MODEL', 'deepseek/deepseek-chat-v3.1:free')
    db_path = os.getenv('CHROMA_DB_PATH', './chroma_db')
    
    print(f"📋 Model: {model}")
    print(f"📁 ChromaDB path: {db_path}")
    
    # Test chatbot initialization
    try:
        from insurance_chatbot import InsuranceChatbot
        print("🧪 Testing chatbot initialization...")
        
        # This should work without hardcoded API key
        chatbot = InsuranceChatbot()
        print("✅ Chatbot initialized successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Chatbot initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = test_env_setup()
    if success:
        print("\n🎉 Environment setup test passed!")
    else:
        print("\n💥 Environment setup test failed!")
        exit(1)