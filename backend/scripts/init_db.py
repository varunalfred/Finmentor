"""
Database initialization script
Sets up PostgreSQL with PGVector extension
"""

import asyncio
import logging
from sqlalchemy import text
from services.database import engine, init_db
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_pgvector():
    """Enable PGVector extension in PostgreSQL"""
    try:
        async with engine.connect() as conn:
            # Create extension if not exists
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            await conn.commit()
            logger.info("PGVector extension enabled")

            # Verify extension
            result = await conn.execute(
                text("SELECT * FROM pg_extension WHERE extname = 'vector'")
            )
            if result.fetchone():
                logger.info("PGVector extension verified")
            else:
                logger.error("PGVector extension not found")

    except Exception as e:
        logger.error(f"Failed to setup PGVector: {e}")
        logger.info("Make sure PostgreSQL has pgvector installed:")
        logger.info("  Ubuntu/Debian: sudo apt install postgresql-14-pgvector")
        logger.info("  macOS: brew install pgvector")
        logger.info("  Docker: Use image ankane/pgvector")
        raise

async def create_indexes():
    """Create optimized indexes for vector search"""
    try:
        async with engine.connect() as conn:
            # Create HNSW index for messages (better for similarity search)
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS messages_embedding_hnsw_idx
                ON messages USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """))

            # Create HNSW index for educational content
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS education_embedding_hnsw_idx
                ON educational_content USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """))

            # Create regular indexes for filtering
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_messages_user_created
                ON messages(user_id, created_at DESC);
            """))

            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_conversations_user_updated
                ON conversations(user_id, updated_at DESC);
            """))

            await conn.commit()
            logger.info("Indexes created successfully")

    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")
        # Non-fatal error, continue

async def insert_sample_educational_content():
    """Insert sample educational content for testing"""
    try:
        from models.database import EducationalContent
        from services.database import AsyncSessionLocal

        async with AsyncSessionLocal() as session:
            # Check if content already exists
            result = await session.execute(
                text("SELECT COUNT(*) FROM educational_content")
            )
            count = result.scalar()

            if count == 0:
                # Add sample content
                samples = [
                    {
                        "title": "Understanding P/E Ratio",
                        "topic": "investing",
                        "level": "beginner",
                        "content": """The Price-to-Earnings (P/E) ratio is a key metric used to value stocks.
                        It compares a company's stock price to its earnings per share.
                        A high P/E might indicate the stock is overvalued or investors expect high growth.""",
                        "summary": "P/E ratio helps evaluate if a stock is overvalued or undervalued"
                    },
                    {
                        "title": "What is Diversification?",
                        "topic": "portfolio",
                        "level": "beginner",
                        "content": """Diversification means spreading your investments across different assets
                        to reduce risk. Don't put all your eggs in one basket.
                        Mix stocks, bonds, and other assets from different sectors and regions.""",
                        "summary": "Diversification reduces investment risk by spreading across assets"
                    },
                    {
                        "title": "Understanding Market Volatility",
                        "topic": "risk",
                        "level": "intermediate",
                        "content": """Market volatility refers to the rate at which stock prices move up and down.
                        High volatility means prices change rapidly, creating both opportunities and risks.
                        Use volatility indicators like VIX to gauge market sentiment.""",
                        "summary": "Volatility measures how much and how quickly prices change"
                    }
                ]

                for sample in samples:
                    content = EducationalContent(
                        title=sample["title"],
                        topic=sample["topic"],
                        level=sample["level"],
                        content=sample["content"],
                        summary=sample["summary"],
                        content_type="article",
                        difficulty_score=3 if sample["level"] == "beginner" else 5
                    )
                    session.add(content)

                await session.commit()
                logger.info(f"Added {len(samples)} sample educational content items")
            else:
                logger.info(f"Educational content already exists ({count} items)")

    except Exception as e:
        logger.error(f"Failed to insert sample content: {e}")

async def main():
    """Main initialization function"""
    try:
        logger.info("Starting database initialization...")

        # Step 1: Setup PGVector extension
        logger.info("Setting up PGVector extension...")
        await setup_pgvector()

        # Step 2: Create tables
        logger.info("Creating database tables...")
        await init_db()

        # Step 3: Create optimized indexes
        logger.info("Creating indexes...")
        await create_indexes()

        # Step 4: Insert sample data
        logger.info("Inserting sample data...")
        await insert_sample_educational_content()

        logger.info("✅ Database initialization completed successfully!")

    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        sys.exit(1)

    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())