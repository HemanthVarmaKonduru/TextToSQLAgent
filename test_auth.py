"""
Test script to verify Supabase authentication setup.
Run this to check if your SUPABASE_URL and ANON_KEY are configured correctly.
"""

import os
from auth_service import get_supabase_auth

def test_supabase_config():
    """Test Supabase configuration."""
    print("🔍 Testing Supabase Configuration...")
    print("-" * 50)
    
    # Check environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("ANON_KEY")
    
    print(f"SUPABASE_URL: {'✅ Set' if supabase_url else '❌ Not set'}")
    if supabase_url:
        print(f"  URL: {supabase_url[:30]}..." if len(supabase_url) > 30 else f"  URL: {supabase_url}")
    
    print(f"ANON_KEY: {'✅ Set' if anon_key else '❌ Not set'}")
    if anon_key:
        print(f"  Key: {anon_key[:20]}..." if len(anon_key) > 20 else f"  Key: {anon_key}")
    
    print("-" * 50)
    
    if not supabase_url or not anon_key:
        print("❌ Missing environment variables!")
        print("\nTo fix this:")
        print("1. Set environment variables:")
        print("   export SUPABASE_URL='your_supabase_url'")
        print("   export ANON_KEY='your_anon_key'")
        print("\n2. Or create a .env file with:")
        print("   SUPABASE_URL=your_supabase_url")
        print("   ANON_KEY=your_anon_key")
        return False
    
    # Test Supabase client initialization
    try:
        auth = get_supabase_auth()
        print("✅ Supabase client initialized successfully!")
        
        # Test basic functionality
        user_response = auth.get_current_user()
        if user_response["success"]:
            print("✅ User authentication check works!")
            print(f"Current user: {user_response['user'].email if user_response['user'] else 'Not logged in'}")
        else:
            print("✅ Authentication check works (no user logged in)")
        
        print("\n🎉 Supabase configuration is working correctly!")
        print("You can now run: python -m streamlit run login.py")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing Supabase client: {e}")
        print("\nPossible issues:")
        print("- Invalid SUPABASE_URL or ANON_KEY")
        print("- Network connectivity problems")
        print("- Supabase project not properly configured")
        return False

if __name__ == "__main__":
    test_supabase_config()
