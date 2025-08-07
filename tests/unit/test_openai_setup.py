#!/usr/bin/env python3
"""
Test script to verify OpenAI configuration is working correctly.
"""

import os
import sys

def test_openai_configuration():
    """Test the OpenAI configuration setup."""
    print("🔧 Testing OpenAI Configuration Setup")
    print("=" * 50)
    
    # Test 1: Check environment variables
    print("\n1. Checking environment variables...")
    openai_key = os.getenv('OPENAI_API_KEY')
    openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    if openai_key and len(openai_key) > 20:
        print("✅ OPENAI_API_KEY is set")
        print(f"   Model: {openai_model}")
    else:
        print("❌ OPENAI_API_KEY not set or too short")
        print("   Please update your .env file with your actual OpenAI API key")
        return False
    
    # Test 2: Test settings import
    print("\n2. Testing settings import...")
    try:
        from src.config.settings import settings
        print("✅ Settings imported successfully")
        print(f"   OpenAI Model: {settings.OPENAI_MODEL}")
        print(f"   Database Name: {settings.DB_NAME}")
    except Exception as e:
        print(f"❌ Failed to import settings: {e}")
        return False
    
    # Test 3: Test configuration validation
    print("\n3. Testing configuration validation...")
    try:
        is_valid = settings.validate_config()
        if is_valid:
            print("✅ Configuration validation passed")
        else:
            print("❌ Configuration validation failed")
            return False
    except Exception as e:
        print(f"❌ Configuration validation error: {e}")
        return False
    
    # Test 4: Test TextToSQLAgent import
    print("\n4. Testing TextToSQLAgent import...")
    try:
        from src.core.text_to_sql_agent import TextToSQLAgent
        print("✅ TextToSQLAgent imported successfully")
    except Exception as e:
        print(f"❌ Failed to import TextToSQLAgent: {e}")
        return False
    
    print("\n🎉 All tests passed! OpenAI configuration is ready.")
    print("\n📝 Next steps:")
    print("   1. Update your .env file with your actual OpenAI API key")
    print("   2. Run: streamlit run app.py")
    print("   3. Test with bike-related queries")
    
    return True

if __name__ == "__main__":
    success = test_openai_configuration()
    sys.exit(0 if success else 1) 