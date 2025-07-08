#!/usr/bin/env python3
"""
Riskify Deployment Setup Script
This script prepares the project for GitHub and Render deployment.
"""

import os
import shutil
import subprocess
import sys

def create_requirements_txt():
    """Create requirements.txt from deploy-requirements.txt"""
    try:
        if os.path.exists('deploy-requirements.txt'):
            shutil.copy('deploy-requirements.txt', 'requirements.txt')
            print("✅ Created requirements.txt from deploy-requirements.txt")
        else:
            print("❌ deploy-requirements.txt not found")
            return False
    except Exception as e:
        print(f"❌ Error creating requirements.txt: {e}")
        return False
    return True

def check_essential_files():
    """Check if all essential files exist"""
    essential_files = [
        'main.py',
        'app.py', 
        'Procfile',
        'runtime.txt',
        'README.md',
        '.gitignore',
        'DEPLOYMENT.md'
    ]
    
    missing_files = []
    for file in essential_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"✅ {file}")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    return True

def check_ml_models():
    """Check if ML model files exist"""
    model_files = [
        'attached_assets/xgb_model_1751364025628.pkl',
        'attached_assets/loan_xgb_model.pkl',
        'attached_assets/stock_rf_model.pkl'
    ]
    
    for model_file in model_files:
        if os.path.exists(model_file):
            print(f"✅ {model_file}")
        else:
            print(f"⚠️  {model_file} not found")

def generate_session_secret():
    """Generate a secure session secret"""
    import secrets
    secret = secrets.token_hex(32)
    print(f"\n🔑 Generated SESSION_SECRET for deployment:")
    print(f"SESSION_SECRET={secret}")
    print("\n📋 Copy this to your Render environment variables!")
    return secret

def main():
    """Main deployment setup function"""
    print("🚀 Riskify Deployment Setup")
    print("=" * 40)
    
    print("\n1. Checking essential files...")
    if not check_essential_files():
        sys.exit(1)
    
    print("\n2. Creating requirements.txt...")
    if not create_requirements_txt():
        sys.exit(1)
    
    print("\n3. Checking ML model files...")
    check_ml_models()
    
    print("\n4. Generating session secret...")
    generate_session_secret()
    
    print("\n✅ Deployment setup complete!")
    print("\nNext steps:")
    print("1. Copy the SESSION_SECRET above")
    print("2. Create GitHub repository")
    print("3. Push code to GitHub")
    print("4. Deploy on Render with the session secret")
    print("5. Add PostgreSQL database in Render")
    print("\nSee DEPLOYMENT.md for detailed instructions.")

if __name__ == "__main__":
    main()