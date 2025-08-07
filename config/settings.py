"""
Configuration Management Component

This module handles all application configuration settings, environment variable loading,
and validation. It provides a clean interface for accessing configuration values
with proper error handling and type validation.

Author: TextToSQL Agent v2
Created: 2025-01-06
"""

import os
from typing import Optional, Any, Dict
from dataclasses import dataclass
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""
    pass


@dataclass
class OpenAIConfig:
    """Configuration for OpenAI service."""
    api_key: str
    model: str
    
    def __post_init__(self):
        """Validate OpenAI configuration after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate all OpenAI configuration values."""
        if not self.api_key:
            raise ConfigurationError("OpenAI API key is required")
        
        if len(self.api_key) < 10:
            raise ConfigurationError("OpenAI API key appears to be invalid (too short)")
        
        if not self.model:
            raise ConfigurationError("OpenAI model is required")
        
        if not self.model.startswith(('gpt-', 'dall-e-', 'whisper-')):
            raise ConfigurationError("OpenAI model must be a valid model name")


@dataclass
class DatabaseConfig:
    """Configuration for PostgreSQL database."""
    host: str
    port: int
    name: str
    user: str
    password: str
    
    def __post_init__(self):
        """Validate database configuration after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate all database configuration values."""
        if not self.host:
            raise ConfigurationError("Database host is required")
        
        if not isinstance(self.port, int) or self.port <= 0 or self.port > 65535:
            raise ConfigurationError("Database port must be a valid port number (1-65535)")
        
        if not self.name:
            raise ConfigurationError("Database name is required")
        
        if not self.user:
            raise ConfigurationError("Database user is required")
        
        if not self.password:
            raise ConfigurationError("Database password is required")
    
    def get_connection_string(self) -> str:
        """Generate PostgreSQL connection string."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass
class AppConfig:
    """General application configuration."""
    name: str
    debug: bool
    log_level: str
    
    def __post_init__(self):
        """Validate application configuration after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate application configuration values."""
        if not self.name:
            raise ConfigurationError("Application name is required")
        
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level not in valid_log_levels:
            raise ConfigurationError(f"Log level must be one of: {valid_log_levels}")


@dataclass
class StreamlitConfig:
    """Configuration for Streamlit application."""
    title: str
    description: str
    
    def __post_init__(self):
        """Validate Streamlit configuration after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate Streamlit configuration values."""
        if not self.title:
            raise ConfigurationError("Streamlit title is required")
        
        if not self.description:
            raise ConfigurationError("Streamlit description is required")


class Settings:
    """
    Main settings class that loads and manages all application configuration.
    
    This class follows the Singleton pattern to ensure consistent configuration
    throughout the application.
    """
    
    _instance: Optional['Settings'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'Settings':
        """Ensure only one instance of Settings exists (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize settings by loading environment variables."""
        if not self._initialized:
            self._load_environment()
            self._load_configurations()
            self._initialized = True
            logger.info("Configuration loaded successfully")
    
    def _load_environment(self):
        """Load environment variables from .env file."""
        try:
            # Try to load from .env file
            env_loaded = load_dotenv()
            if env_loaded:
                logger.info("Loaded environment variables from .env file")
            else:
                logger.info("No .env file found, using system environment variables")
        except Exception as e:
            logger.warning(f"Error loading .env file: {e}")
    
    def _get_env_var(self, key: str, default: Any = None, required: bool = True) -> Any:
        """
        Get environment variable with validation.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            required: Whether the variable is required
            
        Returns:
            Environment variable value
            
        Raises:
            ConfigurationError: If required variable is missing
        """
        value = os.getenv(key, default)
        
        if required and value is None:
            raise ConfigurationError(f"Required environment variable '{key}' is not set")
        
        return value
    
    def _get_bool_env_var(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable."""
        value = self._get_env_var(key, str(default), required=False)
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def _get_int_env_var(self, key: str, default: int, required: bool = True) -> int:
        """Get integer environment variable with validation."""
        value = self._get_env_var(key, str(default), required)
        try:
            return int(value)
        except ValueError:
            raise ConfigurationError(f"Environment variable '{key}' must be an integer, got: {value}")
    
    def _load_configurations(self):
        """Load all configuration components."""
        try:
            # Load OpenAI configuration
            self.openai = OpenAIConfig(
                api_key=self._get_env_var('OPENAI_API_KEY'),
                model=self._get_env_var('OPENAI_MODEL', 'gpt-4o-mini', False)
            )
            
            # Load database configuration
            self.database = DatabaseConfig(
                host=self._get_env_var('DB_HOST', 'localhost', False),
                port=self._get_int_env_var('DB_PORT', 5432, False),
                name=self._get_env_var('DB_NAME'),
                user=self._get_env_var('DB_USER'),
                password=self._get_env_var('DB_PASSWORD')
            )
            
            # Load application configuration
            self.app = AppConfig(
                name=self._get_env_var('APP_NAME', 'Bikes TextToSQL Agent', False),
                debug=self._get_bool_env_var('APP_DEBUG'),
                log_level=self._get_env_var('LOG_LEVEL', 'INFO', False)
            )
            
            # Load Streamlit configuration
            self.streamlit = StreamlitConfig(
                title=self._get_env_var('STREAMLIT_TITLE', '🏍️ Bikes TextToSQL Agent', False),
                description=self._get_env_var('STREAMLIT_DESCRIPTION', 'Ask questions about motorcycles in natural language', False)
            )
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def validate_all(self) -> Dict[str, bool]:
        """
        Validate all configuration components.
        
        Returns:
            Dictionary with validation results for each component
        """
        results = {}
        
        try:
            self.openai._validate()
            results['openai'] = True
        except ConfigurationError as e:
            results['openai'] = False
            logger.error(f"OpenAI configuration invalid: {e}")
        
        try:
            self.database._validate()
            results['database'] = True
        except ConfigurationError as e:
            results['database'] = False
            logger.error(f"Database configuration invalid: {e}")
        
        try:
            self.app._validate()
            results['app'] = True
        except ConfigurationError as e:
            results['app'] = False
            logger.error(f"App configuration invalid: {e}")
        
        try:
            self.streamlit._validate()
            results['streamlit'] = True
        except ConfigurationError as e:
            results['streamlit'] = False
            logger.error(f"Streamlit configuration invalid: {e}")
        
        return results
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current configuration (without sensitive data).
        
        Returns:
            Dictionary with configuration summary
        """
        return {
            'openai': {
                'model': self.openai.model,
                'api_key_set': bool(self.openai.api_key)
            },
            'database': {
                'host': self.database.host,
                'port': self.database.port,
                'name': self.database.name,
                'user': self.database.user,
                'password_set': bool(self.database.password)
            },
            'app': {
                'name': self.app.name,
                'debug': self.app.debug,
                'log_level': self.app.log_level
            },
            'streamlit': {
                'title': self.streamlit.title,
                'description': self.streamlit.description
            }
        }


# No global instance - create when needed 