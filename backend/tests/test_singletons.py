"""
Test Singleton Implementation
Verify that services are properly implemented as singletons
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

async def test_database_singleton():
    """Test database service singleton"""
    from services.database import DatabaseService, db_service

    # Create multiple instances
    db1 = DatabaseService()
    db2 = DatabaseService()
    db3 = db_service

    # Verify they are the same instance
    assert db1 is db2, "Database service is not a singleton!"
    assert db2 is db3, "Database service instance mismatch!"
    assert id(db1) == id(db2) == id(db3), "Database service IDs don't match!"

    print("✅ Database service singleton: PASSED")
    print(f"   Instance ID: {id(db1)}")

async def test_rag_singleton():
    """Test RAG service singleton"""
    from services.agentic_rag import AgenticRAG, rag_service

    # Create multiple instances
    rag1 = AgenticRAG()
    rag2 = AgenticRAG()
    rag3 = rag_service

    # Verify they are the same instance
    assert rag1 is rag2, "RAG service is not a singleton!"
    assert rag2 is rag3, "RAG service instance mismatch!"
    assert id(rag1) == id(rag2) == id(rag3), "RAG service IDs don't match!"

    print("✅ RAG service singleton: PASSED")
    print(f"   Instance ID: {id(rag1)}")

async def test_embedding_service():
    """Test embedding service initialization"""
    from services.agentic_rag import rag_service

    # Check if embedding service is initialized
    assert rag_service.embedding_service is not None, "Embedding service not initialized!"

    # Check which embedding service is being used
    service_type = type(rag_service.embedding_service).__name__
    print(f"✅ Embedding service initialized: {service_type}")

async def test_hybrid_system_integration():
    """Test hybrid system integration with singletons"""
    from agents.hybrid_core import HybridFinMentorSystem
    from services.agentic_rag import rag_service

    # Create hybrid system
    config = {
        "model": "gemini-pro",
        "temperature": 0.7,
        "max_tokens": 1000
    }

    hybrid = HybridFinMentorSystem(config)

    # Verify RAG integration
    assert hybrid.agentic_rag is rag_service, "Hybrid system not using RAG singleton!"

    print("✅ Hybrid system integration: PASSED")

async def main():
    """Run all singleton tests"""
    print("\n" + "="*50)
    print("Testing Singleton Implementation")
    print("="*50 + "\n")

    try:
        # Test each singleton
        await test_database_singleton()
        await test_rag_singleton()
        await test_embedding_service()
        await test_hybrid_system_integration()

        print("\n" + "="*50)
        print("All singleton tests PASSED! ✅")
        print("="*50)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())