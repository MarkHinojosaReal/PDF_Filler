"""
Configuration module for PDF Filler application.
Handles environment variables and API key management.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


# Load environment variables from .env file
def load_environment():
    """Load environment variables from .env file."""
    # Look for .env file in the project root
    project_root = Path(__file__).parent.parent
    env_path = project_root / ".env"
    
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Try to load from current directory as fallback
        load_dotenv()

# Load environment variables when module is imported
load_environment()

class Config:
    """Configuration class for the application."""
    
    # Google GenAI API Configuration
    GOOGLE_GENAI_API_KEY = os.getenv("GOOGLE_GENAI_API_KEY")
    
    # OpenAI API Configuration (if needed)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    @classmethod
    def validate_google_genai_key(cls):
        """Validate that Google GenAI API key is set."""
        if not cls.GOOGLE_GENAI_API_KEY:
            raise ValueError(
                "Google GenAI API key not found. Please set GOOGLE_GENAI_API_KEY "
                "in your .env file or environment variables."
            )
        return cls.GOOGLE_GENAI_API_KEY
    
    @classmethod
    def get_google_genai_key(cls):
        """Get the Google GenAI API key."""
        return cls.validate_google_genai_key()
    
    @classmethod
    def is_google_genai_configured(cls):
        """Check if Google GenAI is properly configured."""
        try:
            cls.validate_google_genai_key()
            return True
        except ValueError:
            return False 