"""
RAG System Quick Start Script
Automated setup and testing for RAG system
"""

import asyncio
import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.database import db_service, init_db
from services.rag_service import get_rag_service
from config.rag_config import get_rag_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def check_database():
    """Check database connection"""
    logger.info("Checking database connection...")
    try:
        await init_db()
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


async def check_configuration():
    """Check RAG configuration"""
    logger.info("Checking RAG configuration...")
    try:
        config = get_rag_config()
        config.validate()
        
        config_dict = config.to_dict()
        logger.info(f"✅ Configuration valid")
        logger.info(f"   Embedding provider: {config_dict['embedding']['provider']}")
        logger.info(f"   Providers available:")
        for provider, available in config_dict['embedding']['providers_available'].items():
            status = "✅" if available else "❌"
            logger.info(f"      {status} {provider}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Configuration validation failed: {e}")
        return False


async def load_glossary():
    """Load financial glossary"""
    logger.info("Loading financial glossary...")
    session = await db_service.get_session()
    try:
        service = await get_rag_service(session)
        
        # Check if already loaded
        is_loaded = await service.check_knowledge_base_loaded()
        if is_loaded:
            logger.info("ℹ️  Knowledge base already loaded")
            stats = await service.get_statistics()
            logger.info(f"   Documents: {stats['total_documents']}")
            return True
        
        # Load glossary
        logger.info("Loading glossary (this may take a few minutes)...")
        stats = await service.load_glossary()
        
        logger.info(f"✅ Glossary loaded successfully")
        logger.info(f"   Total terms: {stats['total']}")
        logger.info(f"   Loaded: {stats['loaded']}")
        logger.info(f"   Updated: {stats['updated']}")
        logger.info(f"   Errors: {stats['errors']}")
        logger.info(f"   Skipped: {stats['skipped']}")
        
        return True

    except FileNotFoundError as e:
        logger.error(f"❌ Glossary file not found: {e}")
        logger.info("   Make sure glossary_clean.csv exists in RAG/ directory")
        return False
    except Exception as e:
        logger.error(f"❌ Glossary loading failed: {e}")
        return False
    finally:
        await session.close()


async def test_search():
    """Test search functionality"""
    logger.info("Testing search functionality...")
    session = await db_service.get_session()
    try:
        service = await get_rag_service(session)
        
        queries = [
            "What is P/E ratio?",
            "Explain diversification",
            "What is a stock?"
        ]
        
        for i, query in enumerate(queries, 1):
            logger.info(f"Test {i}: {query}")
            
            result = await service.search(query, top_k=3)
            
            if result['has_context']:
                logger.info(f"   ✅ Found {result['num_sources']} sources")
                logger.info(f"   Context length: {len(result['context'])} chars")
            else:
                logger.warning(f"   ⚠️  No context found")
        
        logger.info("✅ Search tests completed")
        return True

    except Exception as e:
        logger.error(f"❌ Search test failed: {e}")
        return False
    finally:
        await session.close()


async def show_status():
    """Show system status"""
    logger.info("Getting system status...")
    session = await db_service.get_session()
    try:
        service = await get_rag_service(session)
        
        status = await service.get_status()
        
        logger.info("=== System Status ===")
        logger.info(f"Embedding Provider: {status['embedding_provider']}")
        logger.info(f"Embedding Dimension: {status['embedding_dimension']}")
        logger.info(f"Total Documents: {status['total_documents']}")
        logger.info(f"Available Topics: {len(status['topics'])}")
        logger.info(f"Topics: {', '.join(status['topics'][:5])}...")
        
        return True

    except Exception as e:
        logger.error(f"❌ Status check failed: {e}")
        return False
    finally:
        await session.close()


async def main():
    """Main setup script"""
    logger.info("=" * 60)
    logger.info("RAG System Quick Start")
    logger.info("=" * 60)
    
    # Step 1: Check database
    if not await check_database():
        logger.error("Database check failed. Please fix database issues and try again.")
        return False
    
    # Step 2: Check configuration
    if not await check_configuration():
        logger.error("Configuration check failed. Please fix configuration and try again.")
        return False
    
    # Step 3: Load glossary
    if not await load_glossary():
        logger.error("Glossary loading failed. Please check glossary file and try again.")
        return False
    
    # Step 4: Test search
    if not await test_search():
        logger.error("Search test failed. Please check logs for details.")
        return False
    
    # Step 5: Show status
    await show_status()
    
    logger.info("=" * 60)
    logger.info("✅ RAG System Setup Complete!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Start the API server: uvicorn main:app --reload")
    logger.info("2. Test API endpoints: curl http://localhost:8000/api/rag/status")
    logger.info("3. Read full guide: backend/RAG_SETUP_GUIDE.md")
    logger.info("")
    
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Setup failed with error: {e}")
        sys.exit(1)