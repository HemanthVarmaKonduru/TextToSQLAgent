import os
import sys

# Add project root to Python path for module import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

def test_configuration_component():
    """Test the Configuration Management Component."""
    print("🚀 Testing Component 1: Configuration Management")
    print("=" * 50)

    # Test 1: Missing required environment variables
    original_env = dict(os.environ)
    for key in list(os.environ.keys()):
        if key.startswith(('OPENAI_', 'DB_')):
            del os.environ[key]
    
    try:
        from config.settings import Settings, ConfigurationError
        Settings._instance = None  # Reset singleton
        Settings._initialized = False
        
        try:
            settings = Settings()
            print("❌ FAILED: Should have raised ConfigurationError for missing variables")
            test1_passed = False
        except ConfigurationError as e:
            if "Required environment variable" in str(e):
                print("✅ PASSED: Correctly detected missing environment variables")
                test1_passed = True
            else:
                print(f"❌ FAILED: Wrong error type: {e}")
                test1_passed = False
        finally:
            os.environ.clear()
            os.environ.update(original_env)
    except Exception as e:
        print(f"❌ Test 1 crashed: {e}")
        test1_passed = False

    # Test 2: Valid configuration loading
    test_env = {
        'OPENAI_API_KEY': 'sk-test-api-key-1234567890',
        'OPENAI_MODEL': 'gpt-4o-mini',
        'DB_NAME': 'bikes_db',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password'
    }
    original_env = dict(os.environ)
    os.environ.update(test_env)
    
    try:
        from config.settings import Settings
        Settings._instance = None  # Reset singleton
        Settings._initialized = False
        
        test_settings = Settings()
        assert test_settings.openai.api_key == test_env['OPENAI_API_KEY']
        assert test_settings.openai.model == test_env['OPENAI_MODEL']
        assert test_settings.database.name == test_env['DB_NAME']
        print("✅ PASSED: Configuration loaded correctly")
        print(f"   OpenAI Model: {test_settings.openai.model}")
        print(f"   Database Name: {test_settings.database.name}")
        test2_passed = True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        test2_passed = False
    finally:
        os.environ.clear()
        os.environ.update(original_env)

    # Test 3: Invalid API Key Detection
    test_env = {
        'OPENAI_API_KEY': 'short',  # Too short
        'OPENAI_MODEL': 'gpt-4o-mini',
        'DB_NAME': 'bikes_db',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password'
    }
    original_env = dict(os.environ)
    os.environ.update(test_env)
    
    try:
        from config.settings import Settings, ConfigurationError
        Settings._instance = None  # Reset singleton
        Settings._initialized = False
        
        try:
            settings = Settings()
            print("❌ FAILED: Should have detected invalid API key")
            test3_passed = False
        except ConfigurationError as e:
            if "API key appears to be invalid" in str(e):
                print("✅ PASSED: Correctly detected invalid API key")
                test3_passed = True
            else:
                print(f"❌ FAILED: Wrong error: {e}")
                test3_passed = False
        finally:
            os.environ.clear()
            os.environ.update(original_env)
    except Exception as e:
        print(f"❌ Test 3 crashed: {e}")
        test3_passed = False

    # Test 4: Configuration Summary
    test_env = {
        'OPENAI_API_KEY': 'sk-test-api-key-1234567890',
        'OPENAI_MODEL': 'gpt-4o-mini',
        'DB_NAME': 'bikes_db',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password'
    }
    original_env = dict(os.environ)
    os.environ.update(test_env)
    
    try:
        from config.settings import Settings
        Settings._instance = None  # Reset singleton
        Settings._initialized = False
        
        settings = Settings()
        summary = settings.get_summary()
        assert 'api_key_set' in summary['openai']
        assert 'password_set' in summary['database']
        assert summary['openai']['api_key_set'] is True
        assert summary['database']['password_set'] is True
        assert test_env['OPENAI_API_KEY'] not in str(summary)
        assert test_env['DB_PASSWORD'] not in str(summary)
        print("✅ PASSED: Configuration summary works correctly")
        print("   Sensitive data properly masked")
        test4_passed = True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        test4_passed = False
    finally:
        os.environ.clear()
        os.environ.update(original_env)

    passed_count = sum([test1_passed, test2_passed, test3_passed, test4_passed])
    total_count = 4

    print(f"\n📊 Component 1 Test Results:")
    print(f"   Tests Passed: {passed_count}/{total_count}")
    print(f"   Success Rate: {(passed_count/total_count*100):.1f}%")

    if passed_count == total_count:
        print("\n🎉 Component 1: Configuration Management - VALIDATED")
        print("✅ All tests passed")
        print("✅ Error handling works")
        print("✅ Security implemented")
        print("✅ Ready for approval and Component 2")
        return True
    else:
        print(f"\n💥 Component 1: Configuration Management - NEEDS FIXES")
        print(f"❌ {total_count - passed_count} tests failed")
        print("❌ Fix issues before proceeding to Component 2")
        return False

if __name__ == "__main__":
    success = test_configuration_component()
    sys.exit(0 if success else 1) 