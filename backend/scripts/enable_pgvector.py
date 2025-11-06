"""
Enable PGVector Extension in PostgreSQL
Run this once to enable vector operations in your database
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from services.database import db_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def enable_pgvector():
    """Enable PGVector extension in PostgreSQL"""
    
    logger.info("Enabling PGVector extension...")
    
    async with db_service.AsyncSessionLocal() as session:
        try:
            # Check if extension exists
            result = await session.execute(
                text("SELECT * FROM pg_extension WHERE extname = 'vector'")
            )
            if result.first():
                logger.info("✅ PGVector extension already enabled")
                return True
            
            # Enable the extension
            await session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            await session.commit()
            
            logger.info("✅ PGVector extension enabled successfully!")
            
            # Verify it's enabled
            result = await session.execute(
                text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
            )
            version = result.scalar()
            if version:
                logger.info(f"✅ PGVector version: {version}")
                return True
            else:
                logger.error("❌ Failed to enable PGVector extension")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error enabling PGVector: {e}")
            logger.info("\nMake sure you have:")
            logger.info("1. Installed PGVector extension in PostgreSQL")
            logger.info("2. Have superuser privileges on the database")
            logger.info("\nFor Docker: docker exec -it <container> psql -U <user> -d <database> -c 'CREATE EXTENSION vector;'")
            await session.rollback()
            return False

if __name__ == "__main__":
    success = asyncio.run(enable_pgvector())
    if success:
        print("\n🎉 PGVector is now enabled! Restart your server to use vector embeddings.")
    else:
        print("\n⚠️  Could not enable PGVector. See errors above.")
