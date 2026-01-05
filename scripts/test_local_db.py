#!/usr/bin/env python
"""
Quick local database connection test.
Run: python scripts/test_local_db.py
"""
import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def quick_local_test():
    """Quick test for local PostgreSQL connection."""
    print("🔧 QUICK LOCAL DATABASE TEST")
    print("===========================\n")
    
    # Check if USE_LOCAL_DB is True
    use_local = os.getenv('USE_LOCAL_DB', 'False').lower() == 'true'
    if not use_local:
        print("⚠️ WARNING: USE_LOCAL_DB is set to False in .env")
        print("   This script tests LOCAL database. To enable:")
        print("   Set USE_LOCAL_DB=True in your .env file\n")
    
    # Local database credentials
    config = {
        'dbname': os.getenv('LOCAL_DB_NAME', 'Initiativly'),
        'user': os.getenv('LOCAL_DB_USER', 'postgres'),
        'password': os.getenv('LOCAL_DB_PASSWORD', 'postgres'),
        'host': os.getenv('LOCAL_DB_HOST', 'localhost'),
        'port': os.getenv('LOCAL_DB_PORT', '5432'),
    }
    
    print("Testing connection with:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    try:
        # Test connection
        conn = psycopg2.connect(**config)
        cur = conn.cursor()
        
        # Get version
        cur.execute("SELECT version();")
        version = cur.fetchone()[0].split(',')[0]
        print(f"\n✅ Connected! PostgreSQL: {version}")
        
        # Get database info
        cur.execute("SELECT current_database(), current_user;")
        db_info = cur.fetchone()
        print(f"   Database: {db_info[0]}")
        print(f"   User: {db_info[1]}")
        
        # Count tables
        cur.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        table_count = cur.fetchone()[0]
        print(f"   Tables: {table_count}")
        
        cur.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Connection failed: {e}")
        
        # Troubleshooting tips
        print("\n💡 Troubleshooting:")
        print("1. Is PostgreSQL running?")
        print("   Windows: Check Services for 'postgresql'")
        print("   Mac/Linux: Run 'pg_isready'")
        print("\n2. Try connecting with psql:")
        print(f"   psql -h {config['host']} -p {config['port']} -U {config['user']} -d {config['dbname']}")
        print("\n3. Create database if it doesn't exist:")
        print(f"   createdb -h {config['host']} -p {config['port']} -U {config['user']} {config['dbname']}")
        
        return False

if __name__ == "__main__":
    quick_local_test()