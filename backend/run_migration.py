"""
Run database migration: Add document storage tables
"""
import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Execute the migration SQL file"""
    
    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    # Parse database URL
    # Format: postgresql://postgres:postgres@localhost:5432/FinAI
    parts = database_url.replace("postgresql://", "").split("@")
    user_pass = parts[0].split(":")
    host_db = parts[1].split("/")
    host_port = host_db[0].split(":")
    
    conn_params = {
        "user": user_pass[0],
        "password": user_pass[1],
        "host": host_port[0],
        "port": host_port[1],
        "database": host_db[1]
    }
    
    print(f"🔗 Connecting to database: {conn_params['database']}")
    print(f"   Host: {conn_params['host']}:{conn_params['port']}")
    print(f"   User: {conn_params['user']}")
    
    try:
        # Connect to database
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = False  # We'll commit manually
        cursor = conn.cursor()
        
        print("\n📋 Reading migration file...")
        
        # Read migration SQL
        migration_file = "migrations/001_add_document_storage.sql"
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        print(f"✅ Migration file loaded: {len(migration_sql)} characters")
        
        # Execute migration
        print("\n🚀 Executing migration...")
        print("=" * 60)
        
        cursor.execute(migration_sql)
        
        # Commit transaction
        conn.commit()
        
        print("=" * 60)
        print("✅ Migration completed successfully!")
        
        # Verify tables were created
        print("\n🔍 Verifying new tables...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('user_documents', 'document_chunks', 'user_storage_usage')
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        if len(tables) == 3:
            print("✅ All 3 new tables created:")
            for table in tables:
                print(f"   • {table[0]}")
        else:
            print(f"⚠️  Expected 3 tables, found {len(tables)}")
        
        # Verify new columns in conversations table
        print("\n🔍 Verifying new conversation columns...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'conversations' 
            AND column_name IN ('is_public', 'visibility', 'shared_at', 'view_count', 'upvote_count')
            ORDER BY column_name;
        """)
        
        columns = cursor.fetchall()
        if len(columns) == 5:
            print("✅ All 5 new columns added to conversations:")
            for col in columns:
                print(f"   • {col[0]}")
        else:
            print(f"⚠️  Expected 5 columns, found {len(columns)}")
        
        # Check PGVector indexes
        print("\n🔍 Verifying PGVector indexes...")
        cursor.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'document_chunks' 
            AND indexname LIKE '%embedding%';
        """)
        
        indexes = cursor.fetchall()
        print(f"✅ Found {len(indexes)} PGVector indexes:")
        for idx in indexes:
            print(f"   • {idx[0]}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("🎉 MIGRATION SUCCESSFUL!")
        print("=" * 60)
        print("\n✅ Ready to proceed with:")
        print("   1. Document storage service")
        print("   2. Enhanced RAG search")
        print("   3. API endpoints")
        print("   4. Frontend components")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        if conn:
            conn.rollback()
            print("🔄 Transaction rolled back")
        return False

if __name__ == "__main__":
    print("🗄️  Database Migration: Document Storage System")
    print("=" * 60)
    success = run_migration()
    exit(0 if success else 1)
