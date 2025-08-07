import psycopg2
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.config.settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test the database connection"""
    
    print("🔍 Testing Database Connection...")
    print(f"Database: {settings.DB_NAME}")
    print(f"Host: {settings.DB_HOST}")
    print(f"Port: {settings.DB_PORT}")
    print(f"User: {settings.DB_USER}")
    
    try:
        # Test connection
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Database connected successfully!")
        print(f"PostgreSQL version: {version[0]}")
        
        # Check if tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"📋 Found {len(tables)} tables:")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("📋 No tables found in database")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check if the database 'airlines_db' exists")
        print("3. Verify username and password")
        print("4. Check if port 5432 is available")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def create_database_if_not_exists():
    """Create the database if it doesn't exist"""
    
    print("\n🔧 Attempting to create database if it doesn't exist...")
    
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="test_password",  # Use test password for tests
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if bikes_database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'bikes_database'")
        exists = cursor.fetchone()
        
        if not exists:
            print("📝 Creating bikes_database...")
            cursor.execute("CREATE DATABASE bikes_database")
            print("✅ Database 'bikes_database' created successfully!")
        else:
            print("✅ Database 'bikes_database' already exists!")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Database Connection Test")
    print("=" * 40)
    
    # First try to create database if it doesn't exist
    create_database_if_not_exists()
    
    # Then test connection
    success = test_database_connection()
    
    if success:
        print("\n🎉 Database is ready! You can now run:")
        print("   python database_setup.py")
        print("   streamlit run streamlit_app.py")
    else:
        print("\n⚠️  Please fix the database connection before proceeding") 