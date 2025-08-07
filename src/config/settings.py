"""
Configuration settings for the Bikes Text-to-SQL Agent.
All sensitive information is loaded from environment variables.
"""

import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Database Configuration
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "bikes_database")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    
    # Application Configuration
    APP_NAME = os.getenv("APP_NAME", "Bikes TextToSQL Agent")
    APP_DEBUG = os.getenv("APP_DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Streamlit Configuration
    STREAMLIT_TITLE = os.getenv("STREAMLIT_TITLE", "🏍️ Bikes TextToSQL Agent")
    STREAMLIT_DESCRIPTION = os.getenv("STREAMLIT_DESCRIPTION", 
                                    "Ask questions about motorcycles in natural language")
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get the database connection URL with properly encoded password."""
        if not cls.DB_PASSWORD:
            raise ValueError("Database password not found in environment variables")
        
        encoded_password = quote_plus(cls.DB_PASSWORD)
        return f"postgresql://{cls.DB_USER}:{encoded_password}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required configuration is present."""
        required_vars = [
            "OPENAI_API_KEY",
            "DB_PASSWORD"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True

# Create a global settings instance
settings = Settings() 