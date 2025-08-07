"""
Unit tests for the Configuration Management Component

This module tests all aspects of configuration loading, validation,
and error handling to ensure robust behavior.

Author: TextToSQL Agent v2
Created: 2025-01-06
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from .settings import (
    Settings, 
    ConfigurationError, 
    AzureOpenAIConfig, 
    DatabaseConfig, 
    AppConfig, 
    StreamlitConfig
)


class TestAzureOpenAIConfig:
    """Test Azure OpenAI configuration component."""
    
    def test_valid_config(self):
        """Test valid Azure OpenAI configuration."""
        config = AzureOpenAIConfig(
            endpoint="https://test.cognitiveservices.azure.com/",
            api_key="test-api-key-1234567890",
            api_version="2024-12-01-preview",
            deployment_name="gpt-4"
        )
        
        assert config.endpoint == "https://test.cognitiveservices.azure.com/"
        assert config.api_key == "test-api-key-1234567890"
        assert config.api_version == "2024-12-01-preview"
        assert config.deployment_name == "gpt-4"
    
    def test_empty_endpoint(self):
        """Test configuration with empty endpoint."""
        with pytest.raises(ConfigurationError, match="Azure OpenAI endpoint is required"):
            AzureOpenAIConfig(
                endpoint="",
                api_key="test-api-key-1234567890",
                api_version="2024-12-01-preview",
                deployment_name="gpt-4"
            )
    
    def test_invalid_endpoint_url(self):
        """Test configuration with invalid endpoint URL."""
        with pytest.raises(ConfigurationError, match="Azure OpenAI endpoint must be a valid URL"):
            AzureOpenAIConfig(
                endpoint="not-a-url",
                api_key="test-api-key-1234567890",
                api_version="2024-12-01-preview",
                deployment_name="gpt-4"
            )
    
    def test_empty_api_key(self):
        """Test configuration with empty API key."""
        with pytest.raises(ConfigurationError, match="Azure OpenAI API key is required"):
            AzureOpenAIConfig(
                endpoint="https://test.cognitiveservices.azure.com/",
                api_key="",
                api_version="2024-12-01-preview",
                deployment_name="gpt-4"
            )
    
    def test_short_api_key(self):
        """Test configuration with too short API key."""
        with pytest.raises(ConfigurationError, match="Azure OpenAI API key appears to be invalid"):
            AzureOpenAIConfig(
                endpoint="https://test.cognitiveservices.azure.com/",
                api_key="short",
                api_version="2024-12-01-preview",
                deployment_name="gpt-4"
            )
    
    def test_empty_api_version(self):
        """Test configuration with empty API version."""
        with pytest.raises(ConfigurationError, match="Azure OpenAI API version is required"):
            AzureOpenAIConfig(
                endpoint="https://test.cognitiveservices.azure.com/",
                api_key="test-api-key-1234567890",
                api_version="",
                deployment_name="gpt-4"
            )
    
    def test_empty_deployment_name(self):
        """Test configuration with empty deployment name."""
        with pytest.raises(ConfigurationError, match="Azure OpenAI deployment name is required"):
            AzureOpenAIConfig(
                endpoint="https://test.cognitiveservices.azure.com/",
                api_key="test-api-key-1234567890",
                api_version="2024-12-01-preview",
                deployment_name=""
            )


class TestDatabaseConfig:
    """Test database configuration component."""
    
    def test_valid_config(self):
        """Test valid database configuration."""
        config = DatabaseConfig(
            host="localhost",
            port=5432,
            name="test_db",
            user="test_user",
            password="test_password"
        )
        
        assert config.host == "localhost"
        assert config.port == 5432
        assert config.name == "test_db"
        assert config.user == "test_user"
        assert config.password == "test_password"
    
    def test_connection_string(self):
        """Test database connection string generation."""
        config = DatabaseConfig(
            host="localhost",
            port=5432,
            name="test_db",
            user="test_user",
            password="test_password"
        )
        
        expected = "postgresql://test_user:test_password@localhost:5432/test_db"
        assert config.get_connection_string() == expected
    
    def test_empty_host(self):
        """Test configuration with empty host."""
        with pytest.raises(ConfigurationError, match="Database host is required"):
            DatabaseConfig(
                host="",
                port=5432,
                name="test_db",
                user="test_user",
                password="test_password"
            )
    
    def test_invalid_port_negative(self):
        """Test configuration with negative port."""
        with pytest.raises(ConfigurationError, match="Database port must be a valid port number"):
            DatabaseConfig(
                host="localhost",
                port=-1,
                name="test_db",
                user="test_user",
                password="test_password"
            )
    
    def test_invalid_port_zero(self):
        """Test configuration with zero port."""
        with pytest.raises(ConfigurationError, match="Database port must be a valid port number"):
            DatabaseConfig(
                host="localhost",
                port=0,
                name="test_db",
                user="test_user",
                password="test_password"
            )
    
    def test_invalid_port_too_high(self):
        """Test configuration with port number too high."""
        with pytest.raises(ConfigurationError, match="Database port must be a valid port number"):
            DatabaseConfig(
                host="localhost",
                port=70000,
                name="test_db",
                user="test_user",
                password="test_password"
            )
    
    def test_empty_name(self):
        """Test configuration with empty database name."""
        with pytest.raises(ConfigurationError, match="Database name is required"):
            DatabaseConfig(
                host="localhost",
                port=5432,
                name="",
                user="test_user",
                password="test_password"
            )
    
    def test_empty_user(self):
        """Test configuration with empty user."""
        with pytest.raises(ConfigurationError, match="Database user is required"):
            DatabaseConfig(
                host="localhost",
                port=5432,
                name="test_db",
                user="",
                password="test_password"
            )
    
    def test_empty_password(self):
        """Test configuration with empty password."""
        with pytest.raises(ConfigurationError, match="Database password is required"):
            DatabaseConfig(
                host="localhost",
                port=5432,
                name="test_db",
                user="test_user",
                password=""
            )


class TestAppConfig:
    """Test application configuration component."""
    
    def test_valid_config(self):
        """Test valid application configuration."""
        config = AppConfig(
            name="Test App",
            debug=True,
            log_level="DEBUG"
        )
        
        assert config.name == "Test App"
        assert config.debug is True
        assert config.log_level == "DEBUG"
    
    def test_empty_name(self):
        """Test configuration with empty application name."""
        with pytest.raises(ConfigurationError, match="Application name is required"):
            AppConfig(
                name="",
                debug=False,
                log_level="INFO"
            )
    
    def test_invalid_log_level(self):
        """Test configuration with invalid log level."""
        with pytest.raises(ConfigurationError, match="Log level must be one of"):
            AppConfig(
                name="Test App",
                debug=False,
                log_level="INVALID"
            )
    
    def test_valid_log_levels(self):
        """Test all valid log levels."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        for level in valid_levels:
            config = AppConfig(
                name="Test App",
                debug=False,
                log_level=level
            )
            assert config.log_level == level


class TestStreamlitConfig:
    """Test Streamlit configuration component."""
    
    def test_valid_config(self):
        """Test valid Streamlit configuration."""
        config = StreamlitConfig(
            title="Test App",
            description="Test Description"
        )
        
        assert config.title == "Test App"
        assert config.description == "Test Description"
    
    def test_empty_title(self):
        """Test configuration with empty title."""
        with pytest.raises(ConfigurationError, match="Streamlit title is required"):
            StreamlitConfig(
                title="",
                description="Test Description"
            )
    
    def test_empty_description(self):
        """Test configuration with empty description."""
        with pytest.raises(ConfigurationError, match="Streamlit description is required"):
            StreamlitConfig(
                title="Test App",
                description=""
            )


class TestSettings:
    """Test main Settings class."""
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
        'AZURE_OPENAI_API_KEY': 'test-api-key-1234567890',
        'AZURE_OPENAI_DEPLOYMENT_NAME': 'gpt-4',
        'DB_NAME': 'test_db',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password'
    }, clear=True)
    def test_valid_settings_loading(self):
        """Test loading valid settings from environment variables."""
        # Reset singleton
        Settings._instance = None
        Settings._initialized = False
        
        settings = Settings()
        
        assert settings.azure_openai.endpoint == "https://test.cognitiveservices.azure.com/"
        assert settings.azure_openai.api_key == "test-api-key-1234567890"
        assert settings.azure_openai.deployment_name == "gpt-4"
        assert settings.database.name == "test_db"
        assert settings.database.user == "test_user"
        assert settings.database.password == "test_password"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_required_env_vars(self):
        """Test behavior when required environment variables are missing."""
        # Reset singleton
        Settings._instance = None
        Settings._initialized = False
        
        with pytest.raises(ConfigurationError, match="Required environment variable"):
            Settings()
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
        'AZURE_OPENAI_API_KEY': 'test-api-key-1234567890',
        'AZURE_OPENAI_DEPLOYMENT_NAME': 'gpt-4',
        'DB_NAME': 'test_db',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password',
        'DB_PORT': 'invalid'
    }, clear=True)
    def test_invalid_integer_env_var(self):
        """Test behavior with invalid integer environment variable."""
        # Reset singleton
        Settings._instance = None
        Settings._initialized = False
        
        with pytest.raises(ConfigurationError, match="must be an integer"):
            Settings()
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
        'AZURE_OPENAI_API_KEY': 'test-api-key-1234567890',
        'AZURE_OPENAI_DEPLOYMENT_NAME': 'gpt-4',
        'DB_NAME': 'test_db',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password',
        'APP_DEBUG': 'true'
    }, clear=True)
    def test_boolean_env_var_parsing(self):
        """Test boolean environment variable parsing."""
        # Reset singleton
        Settings._instance = None
        Settings._initialized = False
        
        settings = Settings()
        assert settings.app.debug is True
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
        'AZURE_OPENAI_API_KEY': 'test-api-key-1234567890',
        'AZURE_OPENAI_DEPLOYMENT_NAME': 'gpt-4',
        'DB_NAME': 'test_db',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password'
    }, clear=True)
    def test_singleton_pattern(self):
        """Test that Settings follows singleton pattern."""
        # Reset singleton
        Settings._instance = None
        Settings._initialized = False
        
        settings1 = Settings()
        settings2 = Settings()
        
        assert settings1 is settings2
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
        'AZURE_OPENAI_API_KEY': 'test-api-key-1234567890',
        'AZURE_OPENAI_DEPLOYMENT_NAME': 'gpt-4',
        'DB_NAME': 'test_db',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password'
    }, clear=True)
    def test_validate_all_success(self):
        """Test validation of all components when valid."""
        # Reset singleton
        Settings._instance = None
        Settings._initialized = False
        
        settings = Settings()
        results = settings.validate_all()
        
        assert all(results.values())
        assert set(results.keys()) == {'azure_openai', 'database', 'app', 'streamlit'}
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
        'AZURE_OPENAI_API_KEY': 'test-api-key-1234567890',
        'AZURE_OPENAI_DEPLOYMENT_NAME': 'gpt-4',
        'DB_NAME': 'test_db',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password'
    }, clear=True)
    def test_get_summary(self):
        """Test configuration summary generation."""
        # Reset singleton
        Settings._instance = None
        Settings._initialized = False
        
        settings = Settings()
        summary = settings.get_summary()
        
        assert 'azure_openai' in summary
        assert 'database' in summary
        assert 'app' in summary
        assert 'streamlit' in summary
        
        # Check that sensitive data is not exposed
        assert 'api_key_set' in summary['azure_openai']
        assert 'password_set' in summary['database']
        assert summary['azure_openai']['api_key_set'] is True
        assert summary['database']['password_set'] is True
    
    @patch('config.settings.load_dotenv')
    def test_dotenv_loading_error(self, mock_load_dotenv):
        """Test behavior when .env file loading fails."""
        mock_load_dotenv.side_effect = Exception("File error")
        
        # Reset singleton
        Settings._instance = None
        Settings._initialized = False
        
        # Should not raise exception, just log warning
        with patch.dict(os.environ, {
            'AZURE_OPENAI_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
            'AZURE_OPENAI_API_KEY': 'test-api-key-1234567890',
            'AZURE_OPENAI_DEPLOYMENT_NAME': 'gpt-4',
            'DB_NAME': 'test_db',
            'DB_USER': 'test_user',
            'DB_PASSWORD': 'test_password'
        }, clear=True):
            settings = Settings()
            assert settings is not None


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_multiple_validation_errors(self):
        """Test handling of multiple validation errors."""
        with pytest.raises(ConfigurationError):
            AzureOpenAIConfig(
                endpoint="",  # Invalid
                api_key="",   # Invalid
                api_version="",  # Invalid
                deployment_name=""  # Invalid
            )
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
        'AZURE_OPENAI_API_KEY': 'short',  # Invalid API key
        'AZURE_OPENAI_DEPLOYMENT_NAME': 'gpt-4',
        'DB_NAME': 'test_db',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password'
    }, clear=True)
    def test_partial_validation_failure(self):
        """Test validation when some components are invalid."""
        # Reset singleton
        Settings._instance = None
        Settings._initialized = False
        
        with pytest.raises(ConfigurationError):
            Settings()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"]) 