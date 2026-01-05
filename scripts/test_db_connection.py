"""
Test database connectivity for Django project.
Save this file as: test_db_connection.py in your project root
Run: python test_db_connection.py
"""
import os
import sys
from pathlib import Path
import django
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project directory to the Python path
# Get parent directory if running from scripts folder
SCRIPT_DIR = Path(__file__).resolve().parent
if SCRIPT_DIR.name == 'scripts':
    BASE_DIR = SCRIPT_DIR.parent
else:
    BASE_DIR = SCRIPT_DIR
sys.path.insert(0, str(BASE_DIR))

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from django.db import connections
from django.db.utils import OperationalError
from django.conf import settings


def test_database_connection():
    """Test the database connection."""
    print("=" * 60)
    print("DATABASE CONNECTION TEST")
    print("=" * 60)
    
    # Show which database we're testing
    use_local = os.getenv('USE_LOCAL_DB', 'False').lower() == 'true'
    print(f"\nUSE_LOCAL_DB: {use_local}")
    print(f"Testing: {'LOCAL DATABASE' if use_local else 'DEPLOYED DATABASE'}")
    print("-" * 60)
    
    # Get database configuration
    db_config = settings.DATABASES['default']
    print("\nDatabase Configuration:")
    print(f"  Engine: {db_config['ENGINE']}")
    print(f"  Name: {db_config['NAME']}")
    print(f"  User: {db_config['USER']}")
    print(f"  Host: {db_config['HOST']}")
    print(f"  Port: {db_config['PORT']}")
    
    if 'OPTIONS' in db_config:
        print(f"  SSL Mode: {db_config['OPTIONS'].get('sslmode', 'N/A')}")
        print(f"  Channel Binding: {db_config['OPTIONS'].get('channel_binding', 'N/A')}")
    
    print("-" * 60)
    
    # Test the connection
    db_conn = connections['default']
    try:
        print("\nAttempting to connect to database...")
        db_conn.cursor()
        print("✓ SUCCESS: Database connection established!")
        
        # Try to get database version
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"\nPostgreSQL Version:")
            print(f"  {version.split(',')[0]}")
        
        # Check if we can list tables
        with db_conn.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            print(f"\nTables in database: {len(tables)}")
            if tables:
                print("  Tables found:")
                for table in tables[:10]:  # Show first 10 tables
                    print(f"    - {table[0]}")
                if len(tables) > 10:
                    print(f"    ... and {len(tables) - 10} more")
            else:
                print("  No tables found (database might be empty)")
        
        print("\n" + "=" * 60)
        print("CONNECTION TEST PASSED ✓")
        print("=" * 60)
        return True
        
    except OperationalError as e:
        print(f"✗ FAILED: Could not connect to database")
        print(f"\nError Details:")
        print(f"  {str(e)}")
        print("\nCommon Issues:")
        print("  1. Check if database credentials are correct in .env")
        print("  2. Verify database host is accessible")
        print("  3. Ensure database server is running")
        print("  4. Check firewall/security group settings")
        print("  5. Verify SSL settings if using remote database")
        print("\n" + "=" * 60)
        print("CONNECTION TEST FAILED ✗")
        print("=" * 60)
        return False
        
    except Exception as e:
        print(f"✗ UNEXPECTED ERROR: {type(e).__name__}")
        print(f"\nError Details:")
        print(f"  {str(e)}")
        print("\n" + "=" * 60)
        print("CONNECTION TEST FAILED ✗")
        print("=" * 60)
        return False


if __name__ == "__main__":
    test_database_connection()