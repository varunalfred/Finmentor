"""Quick database connection test"""
import asyncio
import asyncpg
from dotenv import load_dotenv
import os

load_dotenv()

async def test_connection():
    database_url = os.getenv('DATABASE_URL')
    print(f"Testing connection to: {database_url.replace(database_url.split('@')[0].split(':')[-1], '****')}")
    
    try:
        # Convert to asyncpg format
        conn_url = database_url.replace('postgresql://', 'postgresql://').replace('?connect_timeout=10&sslmode=prefer', '')
        conn = await asyncpg.connect(conn_url)
        
        print("✅ Database connection successful!")
        
        # Test basic query
        version = await conn.fetchval('SELECT version()')
        print(f"PostgreSQL version: {version[:50]}...")
        
        # Check if pgvector is installed
        try:
            pgvector = await conn.fetchval("SELECT * FROM pg_extension WHERE extname = 'vector'")
            if pgvector:
                print("✅ PGVector extension is installed")
            else:
                print("⚠️  PGVector extension is NOT installed (required for vector embeddings)")
        except:
            print("⚠️  PGVector extension is NOT installed (required for vector embeddings)")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())
