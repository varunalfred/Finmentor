"""
Individual Agent Testing Suite
Tests each of the 13 specialized agents in DSPyFinancialReasoner individually
to validate their functionality before testing multi-agent orchestration.
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import json
from io import StringIO
from contextlib import redirect_stdout

# Load environment variables
load_dotenv()

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from agents.hybrid_core import HybridFinMentorSystem
from services.database import db_service

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


# Test queries for each agent
AGENT_TEST_QUERIES = {
    "explain_agent": {
        "query": "What is a P/E ratio?",
        "query_type": "explain",
        "expected_keywords": ["price", "earnings", "valuation", "stock"],
        "description": "Educational concept explanation"
    },
    "analyze_agent": {
        "query": "Analyze the current market trend for technology stocks",
        "query_type": "analyze",
        "expected_keywords": ["technology", "market", "trend", "stocks"],
        "description": "General financial analysis"
    },
    "risk_assessment_agent": {
        "query": "What are the risks of investing in cryptocurrency?",
        "query_type": "risk",
        "expected_keywords": ["risk", "volatility", "cryptocurrency", "investment"],
        "description": "Risk assessment and mitigation"
    },
    "technical_analysis_agent": {
        "query": "Perform technical analysis on AAPL stock",
        "query_type": "technical",
        "expected_keywords": ["technical", "chart", "indicator", "AAPL"],
        "description": "Technical market analysis"
    },
    "sentiment_analysis_agent": {
        "query": "What is the market sentiment around Tesla stock?",
        "query_type": "sentiment",
        "expected_keywords": ["sentiment", "Tesla", "market", "investor"],
        "description": "Market sentiment analysis"
    },
    "portfolio_optimization_agent": {
        "query": "How should I optimize my portfolio with 60% stocks and 40% bonds?",
        "query_type": "portfolio",
        "expected_keywords": ["portfolio", "optimize", "allocation", "diversification"],
        "description": "Portfolio optimization"
    },
    "dividend_analysis_agent": {
        "query": "Which stocks have the best dividend yield?",
        "query_type": "dividend",
        "expected_keywords": ["dividend", "yield", "income", "stocks"],
        "description": "Dividend analysis"
    },
    "tax_implications_agent": {
        "query": "What are the tax implications of selling stocks at a profit?",
        "query_type": "tax",
        "expected_keywords": ["tax", "capital gains", "profit", "implications"],
        "description": "Tax planning and implications"
    },
    "earnings_analysis_agent": {
        "query": "Analyze Apple's latest earnings report",
        "query_type": "earnings",
        "expected_keywords": ["earnings", "revenue", "profit", "Apple"],
        "description": "Earnings report analysis"
    },
    "economic_analysis_agent": {
        "query": "How does inflation affect the stock market?",
        "query_type": "economic",
        "expected_keywords": ["inflation", "economy", "stock market", "impact"],
        "description": "Economic indicator analysis"
    },
    "personalized_learning_agent": {
        "query": "I'm a beginner investor. What should I learn first?",
        "query_type": "learning",
        "expected_keywords": ["beginner", "learn", "investing", "basics"],
        "description": "Personalized educational content"
    },
    "bias_detection_agent": {
        "query": "Am I showing confirmation bias in my investment decisions?",
        "query_type": "bias",
        "expected_keywords": ["bias", "confirmation", "decision", "behavioral"],
        "description": "Behavioral bias detection"
    },
    "psychological_profiling_agent": {
        "query": "What is my investor risk tolerance based on my behavior?",
        "query_type": "psychology",
        "expected_keywords": ["risk tolerance", "psychology", "investor", "profile"],
        "description": "Psychological profiling"
    }
}


async def test_single_agent(agent_name: str, test_config: dict, system: HybridFinMentorSystem):
    """
    Test a single agent with its specific query
    
    Args:
        agent_name: Name of the agent being tested
        test_config: Configuration containing query, expected keywords, etc.
        system: HybridFinMentorSystem instance
    
    Returns:
        dict: Test results with success status and details
    """
    print(f"\n{'='*80}")
    print(f"🧪 Testing Agent: {agent_name.upper()}")
    print(f"📋 Description: {test_config['description']}")
    print(f"❓ Query: {test_config['query']}")
    print(f"{'='*80}\n")
    
    try:
        # Get query parameters
        query = test_config['query']
        query_type = test_config['query_type']
        expected_keywords = test_config['expected_keywords']
        
        # Create user profile (required for process_query)
        user_profile = {
            "user_id": "test-user-1",
            "type": "beginner",
            "education_level": "beginner"
        }
        
        # Execute the agent's tool directly
        # IMPORTANT: Skip orchestration for individual agent testing
        result = await system.process_query(
            query, 
            user_profile, 
            skip_orchestration=True  # Test individual agents, not orchestration
        )
        
        # Validate response
        response_text = result.get('response', '').lower()
        
        # Check for expected keywords (case-insensitive)
        keywords_found = []
        keywords_missing = []
        
        for keyword in expected_keywords:
            if keyword.lower() in response_text:
                keywords_found.append(keyword)
            else:
                keywords_missing.append(keyword)
        
        # Calculate keyword match rate
        match_rate = len(keywords_found) / len(expected_keywords) if expected_keywords else 0
        
        # Check for knowledge base usage (RAG-first validation)
        kb_used = "knowledge base" in response_text or "📖" in result.get('response', '')
        
        # Get sources from rag_context (new structure)
        rag_context = result.get('rag_context', {})
        if rag_context:
            sources = rag_context.get('sources_used', [])
            kb_used = kb_used or len(sources) > 0
        else:
            sources = result.get('sources', [])  # Fallback to old structure
        
        # Determine success (at least 50% keywords matched or KB used)
        success = match_rate >= 0.5 or kb_used
        
        # Print results
        print("✅ RESPONSE RECEIVED:")
        print(f"   Length: {len(result.get('response', ''))} characters")
        print(f"\n📝 Response Preview:")
        preview = result.get('response', '')[:500]
        print(f"   {preview}...")
        
        print(f"\n🔍 VALIDATION RESULTS:")
        print(f"   Keywords Found: {keywords_found} ({len(keywords_found)}/{len(expected_keywords)})")
        if keywords_missing:
            print(f"   Keywords Missing: {keywords_missing}")
        print(f"   Match Rate: {match_rate*100:.1f}%")
        print(f"   Knowledge Base Used: {'✅' if kb_used else '❌'}")
        print(f"   Sources: {sources if sources else 'None'}")
        
        if success:
            print(f"\n✅ TEST PASSED for {agent_name}")
        else:
            print(f"\n⚠️  TEST WARNING for {agent_name}: Low keyword match and no KB usage")
        
        return {
            "agent": agent_name,
            "success": success,
            "match_rate": match_rate,
            "kb_used": kb_used,
            "response_length": len(result.get('response', '')),
            "keywords_found": keywords_found,
            "keywords_missing": keywords_missing,
            "sources": sources,
            "query_type": query_type
        }
        
    except Exception as e:
        print(f"\n❌ TEST FAILED for {agent_name}")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            "agent": agent_name,
            "success": False,
            "error": str(e),
            "query_type": query_type
        }


async def test_all_agents_individually():
    """
    Test all 13 agents individually
    """
    global _log_file_handle
    
    # Create timestamped log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = TEST_RESULTS_DIR / f"individual_agents_{timestamp}.log"
    json_file = TEST_RESULTS_DIR / f"individual_agents_{timestamp}.json"
    
    with open(log_file, 'w', encoding='utf-8') as log:
        # Redirect stdout to capture ALL output including LangChain verbose traces
        original_stdout = sys.stdout
        sys.stdout = DualOutput(log, original_stdout)
        
        try:
            print("="*80)
            print("🚀 INDIVIDUAL AGENT TESTING SUITE")
            print("="*80)
            print(f"\n📅 Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📊 Testing {len(AGENT_TEST_QUERIES)} specialized agents individually\n")
            
            # Initialize system with database session (like test_simple.py)
            print("🔧 Initializing HybridFinMentorSystem with database session...")
            
            config = {
                "model": os.getenv("DEFAULT_MODEL", "gemini-2.5-flash"),
                "temperature": 0.7,
                "max_tokens": 2500,
                "verbose": True
            }
            
            # Create database session
            async with db_service.AsyncSessionLocal() as db_session:
                system = HybridFinMentorSystem(config, db_session=db_session)
                print("✅ System initialized\n")
                
                # Store results
                all_results = []
                
                # Test each agent
                for agent_name, test_config in AGENT_TEST_QUERIES.items():
                    # Capture result with timestamp
                    start_time = datetime.now()
                    result = await test_single_agent(agent_name, test_config, system)
                    end_time = datetime.now()
                    
                    # Add timing information
                    result['start_time'] = start_time.isoformat()
                    result['end_time'] = end_time.isoformat()
                    result['duration_seconds'] = (end_time - start_time).total_seconds()
                    
                    all_results.append(result)
                    
                    # Free Tier: 10 RPM limit per PROJECT (not per API key)
                    # Each query may make 2-3 LLM calls (RAG + Agent + Tools)
                    # Conservative delay: 10 seconds ensures we stay well under 10 RPM
                    print(f"   ⏳ Waiting 10s before next agent (Free Tier: 10 RPM limit)...")
                    await asyncio.sleep(10)
                
                # Print summary
                print("\n" + "="*80)
                print("📊 INDIVIDUAL AGENT TEST SUMMARY")
                print("="*80 + "\n")
                
                successful_tests = [r for r in all_results if r.get('success', False)]
                failed_tests = [r for r in all_results if not r.get('success', False)]
                
                print(f"✅ Successful Tests: {len(successful_tests)}/{len(all_results)}")
                print(f"❌ Failed Tests: {len(failed_tests)}/{len(all_results)}")
                print(f"📈 Success Rate: {len(successful_tests)/len(all_results)*100:.1f}%\n")
                
                # Detailed results table
                print("┌─────────────────────────────────┬──────────┬───────────┬──────────────┐")
                print("│ Agent Name                      │ Status   │ Match %   │ KB Used      │")
                print("├─────────────────────────────────┼──────────┼───────────┼──────────────┤")
                
                for result in all_results:
                    agent_name = result['agent'][:31].ljust(31)
                    status = "✅ PASS" if result.get('success') else "❌ FAIL"
                    match_rate = f"{result.get('match_rate', 0)*100:.1f}%" if 'match_rate' in result else "N/A"
                    kb_used = "✅" if result.get('kb_used', False) else "❌"
                    
                    print(f"│ {agent_name} │ {status}   │ {match_rate:>7}   │ {kb_used:>11}  │")
                
                print("└─────────────────────────────────┴──────────┴───────────┴──────────────┘\n")
                
                # Agent-specific insights
                print("🔍 AGENT INSIGHTS:")
                for result in all_results:
                    if result.get('success'):
                        agent = result['agent']
                        query_type = result.get('query_type', 'N/A')
                        sources = result.get('sources', [])
                        duration = result.get('duration_seconds', 0)
                        print(f"   • {agent}: Query Type '{query_type}' | Sources: {sources if sources else 'LLM Knowledge'} | Duration: {duration:.1f}s")
                
                # Failed tests details
                if failed_tests:
                    print("\n⚠️  FAILED TEST DETAILS:")
                    for result in failed_tests:
                        print(f"\n   Agent: {result['agent']}")
                        if 'error' in result:
                            print(f"   Error: {result['error']}")
                        else:
                            print(f"   Keywords Missing: {result.get('keywords_missing', [])}")
                            print(f"   Match Rate: {result.get('match_rate', 0)*100:.1f}%")
                            print(f"   KB Used: {result.get('kb_used', False)}")
                
                print("\n" + "="*80)
                print("✅ INDIVIDUAL AGENT TESTING COMPLETE")
                print("="*80)
                print(f"\n📅 Test Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"📁 Full log saved to: {log_file}")
                print(f"📁 JSON results saved to: {json_file}")
                
                # Check success threshold
                success_rate = len(successful_tests) / len(all_results)
                if success_rate < 0.7:
                    print(f"\n❌ Only {len(successful_tests)}/{len(all_results)} tests passed (below 70% threshold)\n")
                else:
                    print(f"\n✅ {len(successful_tests)}/{len(all_results)} tests passed (above 70% threshold)\n")
        
        finally:
            # Restore original stdout
            sys.stdout = original_stdout
        
        # Save JSON results for programmatic access
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'test_suite': 'individual_agents',
                'timestamp': datetime.now().isoformat(),
                'total_agents': len(all_results),
                'successful': len(successful_tests),
                'failed': len(failed_tests),
                'success_rate': success_rate * 100,
                'results': all_results
            }, f, indent=2)
        
        return all_results
if __name__ == "__main__":
    print("\n🎯 Starting Individual Agent Test Suite...\n")
    
    # Run all individual agent tests
    results = asyncio.run(test_all_agents_individually())
    
    # Exit with appropriate code
    success_count = len([r for r in results if r.get('success', False)])
    if success_count == len(results):
        print("\n✅ All individual agent tests passed!")
        sys.exit(0)
    elif success_count >= len(results) * 0.7:  # 70% threshold
        print(f"\n⚠️  {success_count}/{len(results)} tests passed (70%+ threshold met)")
        sys.exit(0)
    else:
        print(f"\n❌ Only {success_count}/{len(results)} tests passed (below 70% threshold)")
        sys.exit(1)
