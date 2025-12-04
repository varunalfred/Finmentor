"""
Simple migration runner for renaming metadata columns
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def run_migration():
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return
    
    # Parse the URL to get connection params
    # Format: postgresql://user:password@host:port/database
    url = database_url.replace("postgresql://", "").replace("postgresql+asyncpg://", "")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(database_url.replace("postgresql+asyncpg://", "postgresql://"))
        
        print("✅ Connected to database")
        
        # Read migration file
        with open("migrations/002_rename_metadata_column.sql", "r") as f:
            migration_sql = f.read()
        
        print("📄 Running migration: 002_rename_metadata_column.sql")
        
        # Execute migration
        await conn.execute(migration_sql)
        
        print("✅ Migration completed successfully!")
        
        # Verify the changes
        print("\n📊 Verifying changes...")
        
        # Check user_documents columns
        result = await conn.fetch("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'user_documents' 
            AND column_name IN ('metadata', 'doc_metadata')
        """)
        print(f"user_documents columns: {[r['column_name'] for r in result]}")
        
        # Check document_chunks columns
        result = await conn.fetch("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'document_chunks' 
            AND column_name IN ('metadata', 'doc_metadata')
        """)
        print(f"document_chunks columns: {[r['column_name'] for r in result]}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_migration())
