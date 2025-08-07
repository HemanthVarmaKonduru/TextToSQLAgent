"""
Component 1 Validation Script
Validates the Configuration Management Component

This script tests the configuration component with various scenarios
to ensure it meets all requirements before moving to Component 2.
"""

import os
import sys
from typing import Dict, Any

# Test scenarios for configuration validation


def test_scenario_1_missing_env_vars():
    """Test: Missing required environment variables"""
    print("\n🧪 Test 1: Missing Required Environment Variables")
    print("-" * 50)
    
    # Clear environment
    original_env = dict(os.environ)
    for key in list(os.environ.keys()):
        if key.startswith(('AZURE_', 'DB_')):
            del os.environ[key]
    
    try:
        # This should fail because required vars are missing
        from config.settings import Settings
        
        # Reset singleton for testing
        Settings._instance = None
        Settings._initialized = False
        
        try:
            settings = Settings()
            print("❌ FAILED: Should have raised ConfigurationError for missing variables")
            return False
        except Exception as e:
            if "Required environment variable" in str(e):
                print("✅ PASSED: Correctly detected missing environment variables")
                return True
            else:
                print(f"❌ FAILED: Wrong error type: {e}")
                return False
    
    finally:
        # Restore environment
        os.environ.clear()
        os.environ.update(original_env)


def test_scenario_2_valid_config():
    """Test: Valid configuration loading"""
    print("\n🧪 Test 2: Valid Configuration Loading")
    print("-" * 50)
    
    # Set up valid environment
    test_env = {
        'AZURE_OPENAI_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
        'AZURE_OPENAI_API_KEY': 'test-api-key-1234567890',
        'AZURE_OPENAI_DEPLOYMENT_NAME': 'gpt-4',
        'DB_NAME': 'test_db',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password'
    }
    
    original_env = dict(os.environ)
    os.environ.update(test_env)
    
    try:
        from config.settings import Settings, settings
        
        # Reset singleton for testing
        Settings._instance = None
        Settings._initialized = False
        
        # This should work
        test_settings = Settings()
        
        # Validate settings
        assert test_settings.azure_openai.endpoint == test_env['AZURE_OPENAI_ENDPOINT']
        assert test_settings.azure_openai.api_key == test_env['AZURE_OPENAI_API_KEY']
        assert test_settings.database.name == test_env['DB_NAME']
        
        print("✅ PASSED: Configuration loaded correctly")
        print(f"   Azure OpenAI Endpoint: {test_settings.azure_openai.endpoint}")
        print(f"   Database Name: {test_settings.database.name}")
        print(f"   App Name: {test_settings.app.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False
    
    finally:
        # Restore environment
        os.environ.clear()
        os.environ.update(original_env)


def test_scenario_3_invalid_values():
    """Test: Invalid configuration values"""
    print("\n🧪 Test 3: Invalid Configuration Values")
    print("-" * 50)
    
    # Set up invalid environment (short API key)
    test_env = {
        'AZURE_OPENAI_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
        'AZURE_OPENAI_API_KEY': 'short',  # Too short
        'AZURE_OPENAI_DEPLOYMENT_NAME': 'gpt-4',
        'DB_NAME': 'test_db',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password'
    }
    
    original_env = dict(os.environ)
    os.environ.update(test_env)
    
    try:
        from config.settings import Settings
        
        # Reset singleton for testing
        Settings._instance = None
        Settings._initialized = False
        
        try:
            settings = Settings()
            print("❌ FAILED: Should have detected invalid API key")
            return False
        except Exception as e:
            if "API key appears to be invalid" in str(e):
                print("✅ PASSED: Correctly detected invalid API key")
                return True
            else:
                print(f"❌ FAILED: Wrong error: {e}")
                return False
    
    finally:
        # Restore environment
        os.environ.clear()
        os.environ.update(original_env)


def test_scenario_4_config_summary():
    """Test: Configuration summary (without sensitive data)"""
    print("\n🧪 Test 4: Configuration Summary")
    print("-" * 50)
    
    # Set up valid environment
    test_env = {
        'AZURE_OPENAI_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
        'AZURE_OPENAI_API_KEY': 'test-api-key-1234567890',
        'AZURE_OPENAI_DEPLOYMENT_NAME': 'gpt-4',
        'DB_NAME': 'test_db',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password'
    }
    
    original_env = dict(os.environ)
    os.environ.update(test_env)
    
    try:
        from config.settings import Settings
        
        # Reset singleton for testing
        Settings._instance = None
        Settings._initialized = False
        
        settings = Settings()
        summary = settings.get_summary()
        
        # Check that sensitive data is masked
        assert 'api_key_set' in summary['azure_openai']
        assert 'password_set' in summary['database']
        assert summary['azure_openai']['api_key_set'] is True
        assert summary['database']['password_set'] is True
        
        # Check that actual keys/passwords are not exposed
        assert test_env['AZURE_OPENAI_API_KEY'] not in str(summary)
        assert test_env['DB_PASSWORD'] not in str(summary)
        
        print("✅ PASSED: Configuration summary works correctly")
        print("   Sensitive data is properly masked")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False
    
    finally:
        # Restore environment
        os.environ.clear()
        os.environ.update(original_env)


def main():
    """Run all validation tests for Component 1"""
    print("🚀 Component 1 Validation: Configuration Management")
    print("=" * 60)
    
    tests = [
        test_scenario_1_missing_env_vars,
        test_scenario_2_valid_config,
        test_scenario_3_invalid_values,
        test_scenario_4_config_summary
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
    
    print(f"\n📊 Component 1 Validation Results:")
    print(f"   Tests Passed: {passed}/{total}")
    print(f"   Success Rate: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n🎉 Component 1: Configuration Management - READY FOR APPROVAL")
        print("✅ All validation tests passed")
        print("✅ Error handling works correctly")
        print("✅ Security features implemented")
        print("✅ Ready to move to Component 2")
        return True
    else:
        print(f"\n💥 Component 1: Configuration Management - NEEDS FIXES")
        print(f"❌ {total - passed} tests failed")
        print("❌ Fix issues before proceeding to Component 2")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 