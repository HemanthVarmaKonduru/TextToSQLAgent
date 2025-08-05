"""
Setup script for the Airlines Text-to-SQL Agent.
Helps with initial configuration and setup.
"""

import os
import sys
import shutil
from pathlib import Path

def create_env_file():
    """Create .env file from template if it doesn't exist."""
    if not os.path.exists('.env'):
        if os.path.exists('env.example'):
            shutil.copy('env.example', '.env')
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file with your actual credentials")
        else:
            print("❌ env.example not found")
    else:
        print("✅ .env file already exists")

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = ['data', 'docs', 'tests', 'logs']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'streamlit',
        'pandas',
        'psycopg2-binary',
        'openai',
        'plotly',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'psycopg2-binary':
                __import__('psycopg2')
            elif package == 'python-dotenv':
                __import__('dotenv')
            else:
                __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages are installed")
        return True

def validate_structure():
    """Validate the project structure."""
    required_files = [
        'src/__init__.py',
        'src/config/__init__.py',
        'src/config/settings.py',
        'src/core/__init__.py',
        'src/core/text_to_sql_agent.py',
        'src/utils/__init__.py',
        'src/utils/database.py',
        'src/utils/visualization.py',
        'app.py',
        'requirements.txt',
        'README.md'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ Project structure is valid")
        return True

def main():
    """Main setup function."""
    print("🚀 Airlines Text-to-SQL Agent Setup")
    print("=" * 40)
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Validate structure
    structure_ok = validate_structure()
    
    print("\n" + "=" * 40)
    
    if deps_ok and structure_ok:
        print("✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env file with your credentials")
        print("2. Set up your PostgreSQL database")
        print("3. Run: python database_setup.py")
        print("4. Start the app: streamlit run app.py")
    else:
        print("❌ Setup incomplete. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 