
import asyncio
import logging
from agents.financial_tools import FinancialTools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_financial_tools():
    print("\n" + "="*50)
    print("TESTING FINANCIAL TOOLS (DIRECT EXECUTION)")
    print("="*50)
    
    tools = FinancialTools()
    
    # 1. Test Real Stock Data
    print("\n1. Testing get_real_stock_data('AAPL')...")
    try:
        data = await tools.get_real_stock_data('AAPL')
        if "error" in data:
            print(f"[ERROR] {data['error']}")
        else:
            print(f"[SUCCESS] {data.get('symbol')} Price: ${data.get('current_price')}")
            print(f"   Details: {list(data.keys())[:5]}...")
    except Exception as e:
        print(f"[EXCEPTION] {e}")

    # 2. Test Technical Indicators
    print("\n2. Testing calculate_technical_indicators('MSFT')...")
    try:
        data = await tools.calculate_technical_indicators('MSFT')
        if "error" in data:
            print(f"[ERROR] {data['error']}")
        else:
            print(f"[SUCCESS] RSI: {data.get('rsi')}, Signal: {data.get('rsi_signal')}")
    except Exception as e:
        print(f"[EXCEPTION] {e}")

    # 3. Test Portfolio Metrics
    print("\n3. Testing calculate_portfolio_metrics...")
    try:
        holdings = {'AAPL': 10, 'GOOGL': 5}
        prices = {'AAPL': 150.0, 'GOOGL': 2800.0}
        data = await tools.calculate_portfolio_metrics(holdings, prices)
        if "error" in data:
            print(f"[ERROR] {data['error']}")
        else:
            print(f"[SUCCESS] Portfolio Value: ${data.get('portfolio_value'):,.2f}")
    except Exception as e:
        print(f"[EXCEPTION] {e}")

    # 4. Test Compound Interest
    print("\n4. Testing calculate_compound_interest...")
    try:
        data = await tools.calculate_compound_interest(10000, 7, 10)
        if "error" in data:
            print(f"[ERROR] {data['error']}")
        else:
            print(f"[SUCCESS] Future Value: ${data.get('future_value')}")
    except Exception as e:
        print(f"[EXCEPTION] {e}")

    print("\n" + "="*50)

if __name__ == "__main__":
    asyncio.run(test_financial_tools())
