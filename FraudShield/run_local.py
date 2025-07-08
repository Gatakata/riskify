#!/usr/bin/env python3
"""
Local development server for Fraud Detection App
Runs without PostgreSQL database dependencies for easy VS Code development
"""

import os
import sys
from flask import Flask

# Set environment variables for local development
os.environ['SESSION_SECRET'] = 'local-development-secret-key-change-in-production'
os.environ['USE_DATABASE'] = 'false'  # Disable database for local development
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = 'true'

# Import the main app
try:
    from app import app
    
    if __name__ == '__main__':
        print("=" * 60)
        print("🔍 FRAUD DETECTION SYSTEM - LOCAL DEVELOPMENT")
        print("=" * 60)
        print("🌐 Starting Flask development server...")
        print("📍 Application will be available at: http://localhost:5000")
        print("🗄️  Database: In-memory storage (no PostgreSQL required)")
        print("🔧 Debug mode: Enabled")
        print("=" * 60)
        
        # Run the Flask development server
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
        
except ImportError as e:
    print("❌ Error importing the application:")
    print(f"   {str(e)}")
    print("\n🔧 Make sure you have installed all required packages:")
    print("   pip install Flask Flask-WTF WTForms XGBoost numpy pandas scikit-learn")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting the application: {str(e)}")
    sys.exit(1)