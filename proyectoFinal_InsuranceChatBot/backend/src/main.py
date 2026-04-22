"""Main entry point for the Insurance Chatbot API."""

import os
from api.app import create_app

def main():
    """Main function to run the application."""
    print("🚀 Starting Enhanced Insurance Chatbot API with Hybrid Search...")
    
    # Get configuration environment
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create the application
    app = create_app(config_name)
    
    print("🌐 Starting Flask server...")
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config.get('DEBUG', False)
    )


if __name__ == '__main__':
    main()