import asyncio
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.hybrid_core import HybridFinMentorSystem
from agents.financial_tools import FinancialTools
from agents.langchain_tools import FinancialToolkit

# Load environment variables
load_dotenv()

# Mock DataSourcesManager for FinancialToolkit
class MockDataSourcesManager:
    async def get_stock_data(self, symbol): 
        return {
            "symbol": symbol, 
            "price": {"current": 150.0, "change": 1.5, "change_percent": 1.0, "low": 145.0, "high": 155.0},
            "52_week": {"low": 100.0, "high": 200.0},
            "market_cap": 1000000000,
            "pe_ratio": 25.0,
            "volume": 1000000,
            "dividend_yield": 0.01,
            "company": {"name": "Test Corp", "sector": "Technology", "industry": "Software"},
            "technical": {"rsi": 50, "moving_avg": {"ma_20": 148.0}},
            "recommendation": "buy"
        }
    # search_web returns a dict with "results" key
    async def search_web(self, query, search_type): 
        return {
            "results": [{"title": "Result", "snippet": "Test snippet", "link": "http://test.com"}],
            "sources": ["Test Source"]
        }
    async def get_market_news(self, topic, limit): return [{"title": "News", "summary": "Test news"}]
    async def get_economic_indicators(self): return {"GDP": "2%"}
    async def search_educational_content(self, topic): return [{"title": "Learn", "content": "Content"}]

# Configuration
config = {
    "model": "gemini-2.5-flash",
    "temperature": 0.7,
    "max_tokens": 4000,
    "verbose": True
}

async def test_financial_tools_direct():
    print("\n" + "="*50)
    print("🧪 TESTING FINANCIAL_TOOLS.PY (Direct)")
    print("="*50)
    ft = FinancialTools()
    
    # Test calculate_compound_interest
    try:
        # AWAIT the async method
        res = await ft.calculate_compound_interest(1000, 5, 10)
        print(f"✅ calculate_compound_interest: {res}")
    except Exception as e: print(f"❌ calculate_compound_interest failed: {e}")

    # Test calculate_loan_payment
    try:
        # AWAIT the async method
        res = await ft.calculate_loan_payment(100000, 5, 30)
        print(f"✅ calculate_loan_payment: {res}")
    except Exception as e: print(f"❌ calculate_loan_payment failed: {e}")
    
    # Test calculate_position_size
    try:
        # AWAIT the async method
        res = await ft.calculate_position_size(10000, 2, 100, 90)
        print(f"✅ calculate_position_size: {res}")
    except Exception as e: print(f"❌ calculate_position_size failed: {e}")

async def test_langchain_tools_direct():
    print("\n" + "="*50)
    print("🧪 TESTING LANGCHAIN_TOOLS.PY (Direct)")
    print("="*50)
    mock_dm = MockDataSourcesManager()
    toolkit = FinancialToolkit(mock_dm)
    
    # Test get_stock_data
    try:
        res = await toolkit.get_stock_data("AAPL")
        print(f"✅ get_stock_data: {res}")
    except Exception as e: print(f"❌ get_stock_data failed: {e}")

    # Test search_financial_web
    try:
        res = await toolkit.search_financial_web("inflation")
        print(f"✅ search_financial_web: {res}")
    except Exception as e: print(f"❌ search_financial_web failed: {e}")

async def test_hybrid_system_tools():
    print("\n" + "="*50)
    print("🧪 TESTING HYBRID_CORE.PY (System Integration)")
    print("="*50)

    try:
        # Initialize system (without DB for now)
        system = HybridFinMentorSystem(config)
        # SET USER PROFILE MANUALLY for tests
        system.user_profile = {"user_id": "test_user", "user_type": "beginner", "education_level": "beginner"}
        print("✅ System initialized")
        
        tools = system.tools
        print(f"📋 Found {len(tools)} tools in Hybrid System")

        # Define test cases
        test_cases = [
            {
                "tool": "calculate_compound_interest",
                "input": "10000", # String input to test robustness
                "desc": "Calculate compound interest"
            },
            {
                "tool": "get_stock_data",
                "input": "AAPL",
                "desc": "Get AAPL stock data"
            },
            {
                "tool": "explain_concept",
                "input": "compound interest",
                "desc": "Explain compound interest"
            },
            {
                "tool": "analyze_financial_query",
                "input": "Should I buy Apple stock right now?",
                "desc": "Analyze AAPL buy query"
            },
            # NEW TESTS
            {
                "tool": "assess_risk",
                "input": "Bitcoin",
                "desc": "Assess risk of Bitcoin"
            },
            {
                "tool": "get_historical_prices",
                "input": "AAPL",
                "desc": "Get historical prices for AAPL"
            },
            {
                "tool": "calculate_technical_indicators",
                "input": "AAPL",
                "desc": "Calculate technical indicators for AAPL"
            },
            {
                "tool": "calculate_portfolio_metrics",
                "input": {"holdings": {"AAPL": 10, "GOOG": 5}, "prices": {"AAPL": 150, "GOOG": 2800}},
                "desc": "Calculate portfolio metrics"
            },
            {
                "tool": "calculate_position_size",
                "input": "10000",
                "desc": "Calculate position size"
            },
            {
                "tool": "calculate_loan_payment",
                "input": "200000",
                "desc": "Calculate loan payment"
            },
            {
                "tool": "compare_stocks",
                "input": ["AAPL", "MSFT"],
                "desc": "Compare AAPL and MSFT"
            }
        ]

        # Run tests
        for i, test in enumerate(test_cases):
            tool_name = test["tool"]
            tool_input = test["input"]
            desc = test["desc"]
            
            print(f"\n🔹 Test {i+1}: {desc} ({tool_name})")
            
            # Find the tool
            tool = next((t for t in tools if t.name == tool_name), None)
            
            if not tool:
                print(f"❌ Tool '{tool_name}' not found!")
                continue
                
            try:
                # Run the tool
                print(f"   Input: {tool_input}")
                start_time = datetime.now()
                # Use .func() which is the synchronous wrapper
                result = tool.func(tool_input)
                duration = (datetime.now() - start_time).total_seconds()
                
                print(f"   ✅ Result ({duration:.2f}s):")
                print(f"   {str(result)[:200]}...") # Truncate output
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")

    except Exception as e:
        print(f"❌ System initialization failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_financial_tools_direct())
    asyncio.run(test_langchain_tools_direct())
    asyncio.run(test_hybrid_system_tools())
