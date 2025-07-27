#!/usr/bin/env python3
"""
Setup script to create .env file with API keys.
"""

import os
from pathlib import Path


def create_env_file():
    """Create .env file with the Google GenAI API key."""
    env_content = """# Google GenAI API Configuration
GOOGLE_GENAI_API_KEY=AIzaSyBTqxQjfaTHxzbzAno7ZtsPfu0vVqxNXsw

# Other API keys can be added here
# OPENAI_API_KEY=your_openai_api_key_here
"""
    
    env_path = Path(".env")
    
    if env_path.exists():
        print(f".env file already exists at {env_path}")
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f"✅ Successfully created .env file at {env_path}")
        print("🔒 Your API key has been added to the .env file")
        print("📝 The .env file is already in .gitignore to keep it secure")
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

def test_config():
    """Test the configuration by importing the config module."""
    try:
        from src.config import Config
        if Config.is_google_genai_configured():
            print("✅ Google GenAI API key is properly configured!")
            return True
        else:
            print("❌ Google GenAI API key is not configured")
            return False
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        return False

if __name__ == "__main__":
    print("Setting up environment variables for PDF Filler...")
    print("=" * 50)
    
    create_env_file()
    print()
    
    print("Testing configuration...")
    test_config()
    
    print("\nSetup complete! You can now use Google GenAI in your PDF Filler application.") 