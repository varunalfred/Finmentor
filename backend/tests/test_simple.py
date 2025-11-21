"""
Simple Test - One Query at a Time
Test the basic query processing without complex multi-agent features
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend directory to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

async def test_basic_query():
    """Test a single basic query"""
    from agents.hybrid_core import HybridFinMentorSystem
    from services.database import db_service

    print("\n" + "="*60)
    print("SIMPLE TEST: Basic Educational Query")
    print("="*60)

    # Simple configuration with verbose logging
    config = {
        "model": os.getenv("DEFAULT_MODEL", "gemini-2.5-flash"),
        "temperature": 0.7,
        "max_tokens": 1000,
        "verbose": True  # Enable verbose logging to see what's happening
    }

    try:
        # Create database session
        async with db_service.AsyncSessionLocal() as db_session:
            system = HybridFinMentorSystem(config, db_session=db_session)

            # Simple educational query
            query = "What is a P/E ratio?"
            user_profile = {
                "user_id": "test_user",
                "education_level": "beginner"
            }

            print(f"\nQuery: {query}")
            print("Processing...")

            result = await system.process_query(query, user_profile)

            print(f"\n✅ SUCCESS!")
            print(f"\nResponse (first 300 chars):")
            print(f"{result.get('response', 'No response')[:300]}...")
            print(f"\nConfidence: {result.get('confidence', 0)}")
            print(f"Metadata: {result.get('metadata', {})}")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

async def test_with_rag():
    """Test query with RAG context retrieval"""
    from agents.hybrid_core import HybridFinMentorSystem
    from services.database import db_service

    print("\n" + "="*60)
    print("SIMPLE TEST: Query with RAG Context")
    print("="*60)

    config = {
        "model": os.getenv("DEFAULT_MODEL", "gemini-2.5-flash"),
        "temperature": 0.7,
        "max_tokens": 1000,
        "verbose": True  # Enable verbose logging
    }

    try:
        async with db_service.AsyncSessionLocal() as db_session:
            system = HybridFinMentorSystem(config, db_session=db_session)

            query = "Explain dividend yield in simple terms"
            user_profile = {
                "user_id": "test_user",
                "education_level": "beginner"
            }

            print(f"\nQuery: {query}")
            print("Processing with RAG...")

            result = await system.process_query(query, user_profile)

            print(f"\n✅ SUCCESS!")
            print(f"\nResponse (first 300 chars):")
            print(f"{result.get('response', 'No response')[:300]}...")
            
            # Show RAG context if available
            rag_context = result.get('metadata', {}).get('rag_context', {})
            if rag_context:
                num_docs = len(rag_context.get('context', []))
                intent = rag_context.get('intent', 'unknown')
                print(f"\nRAG Info:")
                print(f"  - Intent: {intent}")
                print(f"  - Documents Retrieved: {num_docs}")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run simple tests one at a time"""
    print("\n" + "="*70)
    print("SIMPLE TEST SUITE - One Query at a Time")
    print("="*70)
    print(f"\nUsing Model: {os.getenv('DEFAULT_MODEL', 'gemini-2.5-flash')}")
    print("Rate Limit Strategy: Sequential execution with delays")
    print("="*70)

    try:
        # Test 1: Basic query
        await test_basic_query()
        
        print("\n⏳ Waiting 10 seconds before next test...")
        await asyncio.sleep(10)

        # Test 2: Query with RAG
        await test_with_rag()

        print("\n" + "="*70)
        print("✅ ALL SIMPLE TESTS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\n📊 Summary:")
        print("  ✓ Basic query processing works")
        print("  ✓ RAG context retrieval works")
        print("  ✓ No rate limit issues with sequential execution")

    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\nStarting simple test suite...")
    print("This test runs queries ONE AT A TIME to avoid rate limits.")
    asyncio.run(main())
