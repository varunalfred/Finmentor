"""
Test Script: PGVector Installation Verification
Tests if PGVector is correctly installed and configured in your system
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

# ANSI color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(message):
    print(f"{GREEN}✅ {message}{RESET}")

def print_error(message):
    print(f"{RED}❌ {message}{RESET}")

def print_warning(message):
    print(f"{YELLOW}⚠️  {message}{RESET}")

def print_info(message):
    print(f"{BLUE}ℹ️  {message}{RESET}")

async def test_python_package():
    """Test 1: Check if pgvector Python package is installed"""
    print_info("Test 1: Checking pgvector Python package...")
    
    try:
        from pgvector.sqlalchemy import Vector
        import pgvector
        version = getattr(pgvector, '__version__', 'unknown')
        print_success(f"pgvector Python package installed (version: {version})")
        return True
    except ImportError as e:
        print_error(f"pgvector Python package not installed: {e}")
        print_info("Fix: pip install pgvector")
        return False

async def test_database_connection():
    """Test 2: Check database connection"""
    print_info("Test 2: Checking database connection...")
    
    try:
        async with db_service.AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT version()"))
            version = result.scalar()
            print_success(f"Database connected: {version.split(',')[0]}")
            return True
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        print_info("Check DATABASE_URL in .env file")
        return False

async def test_extension_installed():
    """Test 3: Check if PGVector extension is installed in PostgreSQL"""
    print_info("Test 3: Checking if PGVector extension is installed...")
    
    try:
        async with db_service.AsyncSessionLocal() as session:
            result = await session.execute(
                text("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector'")
            )
            ext = result.first()
            
            if ext:
                print_success(f"PGVector extension installed (version: {ext[1]})")
                return True
            else:
                print_error("PGVector extension not found in database")
                print_info("Run: python scripts/enable_pgvector.py")
                return False
    except Exception as e:
        print_error(f"Failed to check extension: {e}")
        return False

async def test_vector_operations():
    """Test 4: Test basic vector operations"""
    print_info("Test 4: Testing vector operations...")
    
    try:
        async with db_service.AsyncSessionLocal() as session:
            # Create test table
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS test_pgvector (
                    id SERIAL PRIMARY KEY,
                    embedding vector(3)
                )
            """))
            
            # Insert test vectors
            await session.execute(text("""
                INSERT INTO test_pgvector (embedding) VALUES 
                ('[1,2,3]'),
                ('[4,5,6]'),
                ('[7,8,9]')
                ON CONFLICT DO NOTHING
            """))
            await session.commit()
            
            # Test similarity search (L2 distance)
            result = await session.execute(text("""
                SELECT id, embedding, embedding <-> '[3,3,3]' AS distance
                FROM test_pgvector
                ORDER BY distance
                LIMIT 3
            """))
            
            rows = result.fetchall()
            if len(rows) == 3:
                print_success("Vector similarity search working!")
                print_info(f"  Closest vector: {rows[0][1]} (distance: {rows[0][2]:.4f})")
            
            # Clean up
            await session.execute(text("DROP TABLE test_pgvector"))
            await session.commit()
            
            return True
            
    except Exception as e:
        print_error(f"Vector operations failed: {e}")
        
        # Try to clean up
        try:
            async with db_service.AsyncSessionLocal() as session:
                await session.execute(text("DROP TABLE IF EXISTS test_pgvector"))
                await session.commit()
        except:
            pass
        
        return False

async def test_distance_operators():
    """Test 5: Test all distance operators"""
    print_info("Test 5: Testing distance operators (L2, cosine, inner product)...")
    
    try:
        async with db_service.AsyncSessionLocal() as session:
            # Test L2 distance
            result = await session.execute(text(
                "SELECT '[1,2,3]'::vector <-> '[4,5,6]'::vector AS l2_distance"
            ))
            l2 = result.scalar()
            print_success(f"L2 distance operator working: {l2:.4f}")
            
            # Test cosine distance
            result = await session.execute(text(
                "SELECT '[1,2,3]'::vector <=> '[4,5,6]'::vector AS cosine_distance"
            ))
            cosine = result.scalar()
            print_success(f"Cosine distance operator working: {cosine:.4f}")
            
            # Test inner product (negative)
            result = await session.execute(text(
                "SELECT '[1,2,3]'::vector <#> '[4,5,6]'::vector AS inner_product"
            ))
            inner = result.scalar()
            print_success(f"Inner product operator working: {inner:.4f}")
            
            return True
            
    except Exception as e:
        print_error(f"Distance operators test failed: {e}")
        return False

async def test_model_integration():
    """Test 6: Check if models use Vector type"""
    print_info("Test 6: Checking model integration...")
    
    try:
        from models.database import Message, EducationalContent, PGVECTOR_AVAILABLE
        
        if PGVECTOR_AVAILABLE:
            print_success("Models configured to use Vector type")
            
            # Check if columns are Vector type
            from pgvector.sqlalchemy import Vector
            
            if hasattr(Message, 'embedding'):
                embedding_type = Message.embedding.type.__class__.__name__
                if 'Vector' in embedding_type:
                    print_success(f"Message.embedding uses Vector type: {embedding_type}")
                else:
                    print_warning(f"Message.embedding uses {embedding_type} (expected Vector)")
            
            return True
        else:
            print_error("PGVECTOR_AVAILABLE is False in models")
            return False
            
    except Exception as e:
        print_error(f"Model integration check failed: {e}")
        return False

async def test_embedding_dimensions():
    """Test 7: Test different embedding dimensions"""
    print_info("Test 7: Testing different embedding dimensions (768, 1536)...")
    
    try:
        async with db_service.AsyncSessionLocal() as session:
            # Test 768 dims (Gemini)
            await session.execute(text("""
                CREATE TEMPORARY TABLE test_768 (
                    id SERIAL,
                    embedding vector(768)
                )
            """))
            
            # Create a 768-dim vector (all zeros)
            await session.execute(text("""
                INSERT INTO test_768 (embedding) 
                VALUES (array_fill(0, ARRAY[768])::vector)
            """))
            print_success("768-dimensional vectors supported (Gemini embeddings)")
            
            # Test 1536 dims (OpenAI)
            await session.execute(text("""
                CREATE TEMPORARY TABLE test_1536 (
                    id SERIAL,
                    embedding vector(1536)
                )
            """))
            
            # Create a 1536-dim vector (all zeros)
            await session.execute(text("""
                INSERT INTO test_1536 (embedding) 
                VALUES (array_fill(0, ARRAY[1536])::vector)
            """))
            print_success("1536-dimensional vectors supported (OpenAI embeddings)")
            
            return True
            
    except Exception as e:
        print_error(f"Embedding dimensions test failed: {e}")
        return False

async def run_all_tests():
    """Run all PGVector tests"""
    print("\n" + "="*70)
    print(f"{BLUE}PGVector Installation Test Suite{RESET}")
    print("="*70 + "\n")
    
    results = []
    
    # Test 1: Python package
    results.append(await test_python_package())
    print()
    
    # Test 2: Database connection
    results.append(await test_database_connection())
    print()
    
    # Test 3: Extension installed
    results.append(await test_extension_installed())
    print()
    
    # Test 4: Vector operations
    if results[2]:  # Only if extension is installed
        results.append(await test_vector_operations())
        print()
        
        # Test 5: Distance operators
        results.append(await test_distance_operators())
        print()
        
        # Test 6: Model integration
        results.append(await test_model_integration())
        print()
        
        # Test 7: Embedding dimensions
        results.append(await test_embedding_dimensions())
        print()
    
    # Summary
    print("="*70)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print_success(f"All tests passed! ({passed}/{total})")
        print_success("PGVector is correctly installed and configured! 🎉")
        print()
        print_info("Your system is ready for:")
        print("  • Semantic message search")
        print("  • Educational content recommendations")
        print("  • Portfolio similarity analysis")
        print("  • Vector-based AI features")
    else:
        print_error(f"Some tests failed ({passed}/{total} passed)")
        print_warning("Fix the issues above to enable full PGVector functionality")
    
    print("="*70 + "\n")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
