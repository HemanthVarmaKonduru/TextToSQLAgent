"""
Environment Setup Helper for Supabase Authentication
This script helps you set up the required environment variables.
"""

import os

def setup_environment():
    """Interactive setup for Supabase environment variables."""
    print("🔧 Supabase Environment Setup")
    print("=" * 50)
    print()
    
    print("You need to set up two environment variables:")
    print("1. SUPABASE_URL - Your Supabase project URL")
    print("2. ANON_KEY - Your Supabase anonymous key")
    print()
    
    print("To get these values:")
    print("1. Go to https://supabase.com")
    print("2. Create a project or open an existing one")
    print("3. Go to Settings → API")
    print("4. Copy the 'URL' and 'anon public' key")
    print()
    
    # Get current values
    current_url = os.getenv("SUPABASE_URL")
    current_key = os.getenv("ANON_KEY")
    
    if current_url:
        print(f"Current SUPABASE_URL: {current_url[:30]}...")
    if current_key:
        print(f"Current ANON_KEY: {current_key[:20]}...")
    
    print()
    print("Choose how to set environment variables:")
    print("1. Export commands (for current session)")
    print("2. .env file (for persistent storage)")
    print("3. Both")
    print()
    
    choice = input("Enter your choice (1, 2, or 3): ").strip()
    
    print()
    supabase_url = input("Enter your SUPABASE_URL: ").strip()
    anon_key = input("Enter your ANON_KEY: ").strip()
    
    if not supabase_url or not anon_key:
        print("❌ Both URL and KEY are required!")
        return
    
    print()
    
    if choice in ["1", "3"]:
        print("📋 Export commands (run these in your terminal):")
        print(f"export SUPABASE_URL='{supabase_url}'")
        print(f"export ANON_KEY='{anon_key}'")
        print()
    
    if choice in ["2", "3"]:
        env_content = f"""# Supabase Configuration
SUPABASE_URL={supabase_url}
ANON_KEY={anon_key}
"""
        
        try:
            with open(".env", "w") as f:
                f.write(env_content)
            print("✅ .env file created successfully!")
            print("Note: Make sure to add .env to your .gitignore file!")
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
    
    print()
    print("🎉 Setup complete!")
    print("Now you can run: python test_auth.py to verify the setup")

if __name__ == "__main__":
    setup_environment()
