# Tools Assessment for Multi-Agent System

## Current Tools Available

### 1. **In LangChain (hybrid_core.py)**
- `analyze_financial_query` - Uses DSPy for analysis
- `explain_concept` - Educational explanations
- `assess_risk` - Risk assessment
- `fetch_market_data` - **⚠️ PLACEHOLDER** (needs implementation)
- `calculate_returns` - **⚠️ PLACEHOLDER** (needs implementation)

### 2. **In Data Sources Manager**
- Yahoo Finance API (working)
- DuckDuckGo Search (working)
- Google Search (optional, with API key)
- Alpha Vantage (optional, with API key)
- NewsAPI (optional, with API key)

### 3. **Available Through DSPy Signatures**
All 13 specialized agents have reasoning capabilities but limited external data access

## 🔧 Tools We Should Add

### Priority 1: **Financial Calculations** ✅ NEEDED
```python
# Tools for actual calculations
- portfolio_calculator: Calculate portfolio metrics (Sharpe ratio, beta, alpha)
- position_sizer: Calculate optimal position sizes
- rebalancing_calculator: Calculate rebalancing needs
- compound_interest: Calculate future values
- option_pricing: Black-Scholes calculations
- tax_calculator: Estimate tax implications
```

### Priority 2: **Real-Time Data Access** ✅ NEEDED
```python
# Connect to actual data sources
- get_stock_quote: Real-time prices from Yahoo Finance
- get_historical_data: Historical prices and volumes
- get_company_fundamentals: P/E, EPS, revenue, etc.
- get_economic_indicators: GDP, inflation, unemployment
- get_crypto_prices: Cryptocurrency data
- get_forex_rates: Currency exchange rates
```

### Priority 3: **Portfolio Management** ✅ NEEDED
```python
# Portfolio tracking and analysis
- add_to_portfolio: Track user positions
- get_portfolio_value: Current portfolio valuation
- calculate_performance: Returns, drawdown, etc.
- generate_report: PDF/Excel reports
- set_alerts: Price/news alerts
```

### Priority 4: **Research Tools** ⚠️ NICE TO HAVE
```python
# Advanced research capabilities
- sentiment_analyzer: Analyze news/social sentiment
- earnings_calendar: Upcoming earnings
- insider_trading: Track insider transactions
- analyst_ratings: Get analyst recommendations
- sec_filings: Access 10-K, 10-Q documents
```

### Priority 5: **Visualization Tools** ⚠️ NICE TO HAVE
```python
# Chart and visualization generation
- create_chart: Generate price/volume charts
- correlation_matrix: Visualize correlations
- portfolio_pie_chart: Asset allocation visual
- performance_graph: Returns over time
```

## Implementation Plan

### Step 1: Create Essential Financial Tools
```python
# agents/financial_tools.py
class FinancialTools:
    @staticmethod
    async def calculate_portfolio_metrics(holdings: Dict) -> Dict:
        """Calculate Sharpe ratio, beta, volatility"""
        pass

    @staticmethod
    async def calculate_position_size(
        capital: float,
        risk_percent: float,
        stop_loss: float
    ) -> float:
        """Kelly criterion or fixed fractional position sizing"""
        pass

    @staticmethod
    async def calculate_compound_interest(
        principal: float,
        rate: float,
        time: float,
        frequency: int = 12
    ) -> float:
        """Future value calculations"""
        pass
```

### Step 2: Connect Real Data Sources
```python
# Enhance data_sources.py
async def get_real_stock_data(symbol: str) -> Dict:
    """Actually fetch from Yahoo Finance"""
    ticker = yf.Ticker(symbol)
    return {
        "current_price": ticker.info.get('currentPrice'),
        "volume": ticker.info.get('volume'),
        "market_cap": ticker.info.get('marketCap'),
        "pe_ratio": ticker.info.get('forwardPE'),
        "dividend_yield": ticker.info.get('dividendYield')
    }
```

### Step 3: Add Tools to LangChain
```python
# In hybrid_core.py _create_tools()
additional_tools = [
    StructuredTool(
        name="calculate_portfolio_metrics",
        func=financial_tools.calculate_portfolio_metrics
    ),
    StructuredTool(
        name="get_real_stock_data",
        func=data_sources.get_real_stock_data
    ),
    # ... more tools
]
```

## Current Gaps Analysis

### ❌ **Critical Missing Tools:**
1. **Real market data fetching** - Currently placeholder
2. **Portfolio calculations** - No actual math tools
3. **Position sizing** - No risk management calculations
4. **Tax calculations** - No tax estimation tools

### ⚠️ **Important but not Critical:**
1. **Charting/Visualization** - Can use external services
2. **PDF/Excel generation** - Nice for reports
3. **Backtesting** - For strategy validation
4. **Options pricing** - For derivatives traders

### ✅ **What We Have Working:**
1. **Reasoning** - DSPy signatures handle logic
2. **Basic search** - DuckDuckGo works
3. **Yahoo Finance** - Library imported but not fully used
4. **Database** - Store and retrieve data

## Recommendation

**YES, we need more tools!** Specifically:

### Immediate Priority:
1. **Financial calculation tools** - Core functionality
2. **Real data fetching tools** - Connect Yahoo Finance properly
3. **Portfolio tracking tools** - Track user positions

### Can Wait:
1. Visualization (users can use TradingView)
2. Advanced research (SEC filings, etc.)
3. Backtesting (complex to implement)

### Quick Wins:
- Connect Yahoo Finance properly (we have it imported!)
- Add basic math calculations (compound interest, returns)
- Create portfolio value tracker

Without these tools, our agents are like expert advisors without calculators or real data!