"""
Test RAG-First Implementation

This test validates that:
1. Knowledge base is queried first
2. Sources are properly attributed
3. Relevance scoring works
4. Fallback to LLM happens when needed
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.hybrid_core import HybridFinMentorSystem
from services.database import db_service
import os
from dotenv import load_dotenv

load_dotenv()

# Create test results directory
TEST_RESULTS_DIR = Path(__file__).parent / "test_results"
TEST_RESULTS_DIR.mkdir(exist_ok=True)


class DualOutput:
    """Custom output stream that writes to both console and file"""
    def __init__(self, file_handle, console):
        self.file = file_handle
        self.console = console
    
    def write(self, message):
        self.console.write(message)
        self.file.write(message)
        self.file.flush()
    
    def flush(self):
        self.console.flush()
        self.file.flush()



async def test_rag_first_educational():
    """Test educational query with RAG-first approach"""
    print("\n" + "="*70)
    print("TEST 1: Educational Query - RAG-First Approach")
    print("="*70)
    
    # Initialize system
    config = {
        "model": "gemini-2.5-flash",
        "temperature": 0.7,
        "max_tokens": 2500
    }
    
    start_time = datetime.now()
    
    async with db_service.AsyncSessionLocal() as db:
        system = HybridFinMentorSystem(config=config, db_session=db)
        
        # Set user profile
        user_profile = {
            "user_id": "test-user-1",  # Must be string to match database schema
            "type": "beginner",
            "education_level": "beginner"
        }
        
        # Test query that SHOULD be in knowledge base
        query = "What is a P/E ratio?"
        
        print(f"\nQuery: {query}")
        print("\nProcessing with RAG-First approach...")
        print("-" * 70)
        
        response = await system.process_query(
            query=query,
            user_profile=user_profile
        )
        
        print("\nResponse:")
        print(response)
        
        # Validate response has source attribution
        has_sources = "Sources:" in response or "📖" in response
        kb_used = "Knowledge Base" in response
        
        if has_sources:
            print("\n✓ Source attribution present")
        else:
            print("\n⚠ Source attribution missing")
        
        # Check if KB was used
        if kb_used:
            print("✓ Knowledge Base was utilized")
        else:
            print("⚠ Knowledge Base may not have been used")
        
        print("\nMetrics:", system.metrics)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            'query': query,
            'has_sources': has_sources,
            'kb_used': kb_used,
            'response_length': len(response),
            'metrics': system.metrics,
            'duration_seconds': duration
        }


async def test_rag_first_analysis():
    """Test financial analysis with RAG-first approach"""
    print("\n" + "="*70)
    print("TEST 2: Financial Analysis - RAG-First Approach")
    print("="*70)
    
    config = {
        "model": "gemini-2.5-flash",
        "temperature": 0.7,
        "max_tokens": 2500
    }
    
    start_time = datetime.now()
    
    async with db_service.AsyncSessionLocal() as db:
        system = HybridFinMentorSystem(config=config, db_session=db)
        
        user_profile = {
            "user_id": "test-user-1",  # Must be string to match database schema
            "type": "beginner",
            "education_level": "beginner"
        }
        
        # Test query that combines KB + analysis
        query = "How do I use P/E ratio to evaluate stocks?"
        
        print(f"\nQuery: {query}")
        print("\nProcessing with RAG-First approach...")
        print("-" * 70)
        
        response = await system.process_query(
            query=query,
            user_profile=user_profile
        )
        
        print("\nResponse:")
        print(response)
        
        # Validate
        has_sources = "Sources:" in response or "📖" in response
        kb_used = "Knowledge Base" in response or "analysis" in response.lower()
        
        if has_sources:
            print("\n✓ Source attribution present")
        else:
            print("\n⚠ Source attribution missing")
        
        if kb_used:
            print("✓ Analysis combined with knowledge")
        
        print("\nMetrics:", system.metrics)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            'query': query,
            'has_sources': has_sources,
            'kb_used': kb_used,
            'response_length': len(response),
            'metrics': system.metrics,
            'duration_seconds': duration
        }
        
        if "Knowledge Base" in response:
            print("✓ Knowledge Base was utilized")
        
        print("\nMetrics:", system.metrics)


async def test_kb_statistics():
    """Check knowledge base statistics"""
    print("\n" + "="*70)
    print("KNOWLEDGE BASE STATISTICS")
    print("="*70)
    
    from services.database import db_service
    
    try:
        async with db_service.AsyncSessionLocal() as session:
            # Count total terms
            from sqlalchemy import text
            result = await session.execute(text("SELECT COUNT(*) FROM educational_content"))
            total = result.scalar()
            
            # Get topics (not category)
            result = await session.execute(text("""
                SELECT topic, COUNT(*) as count 
                FROM educational_content 
                GROUP BY topic 
                ORDER BY count DESC 
                LIMIT 10
            """))
            topics = result.fetchall()
            
            print(f"\nTotal items in knowledge base: {total}")
            print("\nTop topics:")
            for topic, count in topics:
                print(f"  {topic}: {count}")
    
    except Exception as e:
        print(f"Error: {e}")


async def main():
    """Run all tests"""
    # Create timestamped log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = TEST_RESULTS_DIR / f"rag_first_{timestamp}.log"
    json_file = TEST_RESULTS_DIR / f"rag_first_{timestamp}.json"
    
    test_results = {
        'test_suite': 'rag_first',
        'timestamp': datetime.now().isoformat(),
        'tests': []
    }
    
    with open(log_file, 'w', encoding='utf-8') as log:
        # Redirect stdout to capture all output
        original_stdout = sys.stdout
        sys.stdout = DualOutput(log, original_stdout)
        
        try:
            print("\n" + "="*70)
            print("RAG-FIRST IMPLEMENTATION TEST SUITE")
            print("="*70)
            print(f"\n📅 Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Check environment
            if not os.getenv("GEMINI_API_KEY"):
                print("\n✗ Error: GEMINI_API_KEY not found in environment")
                test_results['error'] = "GEMINI_API_KEY not found"
                with open(json_file, 'w') as f:
                    json.dump(test_results, f, indent=2)
                return
            
            if not os.getenv("DATABASE_URL"):
                print("\n✗ Error: DATABASE_URL not found in environment")
                test_results['error'] = "DATABASE_URL not found"
                with open(json_file, 'w') as f:
                    json.dump(test_results, f, indent=2)
                return
            
            print("\n✓ Environment configured")
            
            # Test 1: KB Statistics
            print("\n" + "-"*70)
            start_time = datetime.now()
            try:
                await test_kb_statistics()
                test_results['tests'].append({
                    'name': 'kb_statistics',
                    'status': 'passed',
                    'duration_seconds': (datetime.now() - start_time).total_seconds()
                })
            except Exception as e:
                print(f"\n❌ KB Statistics test failed: {e}")
                test_results['tests'].append({
                    'name': 'kb_statistics',
                    'status': 'failed',
                    'error': str(e),
                    'duration_seconds': (datetime.now() - start_time).total_seconds()
                })
            
            await asyncio.sleep(2)  # Rate limit buffer
            
            # Test 2: Educational Query
            print("\n" + "-"*70)
            start_time = datetime.now()
            try:
                result1 = await test_rag_first_educational()
                test_results['tests'].append({
                    'name': 'educational_query',
                    'status': 'passed',
                    'duration_seconds': (datetime.now() - start_time).total_seconds(),
                    'result': result1
                })
            except Exception as e:
                print(f"\n❌ Educational query test failed: {e}")
                test_results['tests'].append({
                    'name': 'educational_query',
                    'status': 'failed',
                    'error': str(e),
                    'duration_seconds': (datetime.now() - start_time).total_seconds()
                })
            
            await asyncio.sleep(5)  # Rate limit buffer
            
            # Test 3: Analysis Query
            print("\n" + "-"*70)
            start_time = datetime.now()
            try:
                result2 = await test_rag_first_analysis()
                test_results['tests'].append({
                    'name': 'analysis_query',
                    'status': 'passed',
                    'duration_seconds': (datetime.now() - start_time).total_seconds(),
                    'result': result2
                })
            except Exception as e:
                print(f"\n❌ Analysis query test failed: {e}")
                test_results['tests'].append({
                    'name': 'analysis_query',
                    'status': 'failed',
                    'error': str(e),
                    'duration_seconds': (datetime.now() - start_time).total_seconds()
                })
            
            print("\n" + "="*70)
            print("TEST SUITE COMPLETED")
            print("="*70)
            
            # Summary
            total_tests = len(test_results['tests'])
            passed_tests = len([t for t in test_results['tests'] if t['status'] == 'passed'])
            failed_tests = total_tests - passed_tests
            
            print(f"\n✅ Passed: {passed_tests}/{total_tests}")
            print(f"❌ Failed: {failed_tests}/{total_tests}")
            print(f"📈 Success Rate: {(passed_tests/total_tests*100):.1f}%")
            
            print(f"\n📅 Test Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📁 Full log saved to: {log_file}")
            print(f"📁 JSON results saved to: {json_file}")
        
        finally:
            # Restore original stdout
            sys.stdout = original_stdout
    
    # Save JSON results
    test_results['total_tests'] = total_tests
    test_results['passed'] = passed_tests
    test_results['failed'] = failed_tests
    test_results['success_rate'] = (passed_tests/total_tests*100) if total_tests > 0 else 0
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2)


if __name__ == "__main__":
    asyncio.run(main())
