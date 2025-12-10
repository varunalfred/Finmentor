"""
LangChain Tools with Real Data Sources
Connects our data sources to LangChain agents
"""

from typing import Dict, Any, List, Optional
from langchain.tools import Tool, StructuredTool
from langchain.tools.base import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
from services.data_sources import DataSourcesManager
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

# ============= Tool Input Schemas =============

class StockQueryInput(BaseModel):
    """Input schema for stock queries"""
    symbol: str = Field(description="Stock ticker symbol (e.g., AAPL, GOOGL)")

class SearchQueryInput(BaseModel):
    """Input schema for web search"""
    query: str = Field(description="Search query")
    search_type: str = Field(
        default="financial",
        description="Type of search: financial, news, educational, general"
    )

class NewsQueryInput(BaseModel):
    """Input schema for news queries"""
    topic: str = Field(description="News topic to search")
    limit: int = Field(default=5, description="Number of news items")

class EducationQueryInput(BaseModel):
    """Input schema for educational content"""
    topic: str = Field(description="Financial topic to learn about")

# ============= Tool Functions =============

class FinancialToolkit:
    """
    Toolkit providing LangChain tools backed by real data sources
    """

    def __init__(self, data_manager: DataSourcesManager):
        self.data_manager = data_manager

    def get_tools(self) -> List[BaseTool]:
        """Get all available tools"""

        tools = [
            StructuredTool(
                name="get_stock_data",
                description="Get real-time stock data including price, volume, PE ratio, and technical indicators",
                func=self._sync_wrapper(self.get_stock_data),
                args_schema=StockQueryInput
            ),
            StructuredTool(
                name="search_financial_web",
                description="Search the web for financial information, analysis, and advice",
                func=self._sync_wrapper(self.search_financial_web),
                args_schema=SearchQueryInput
            ),
            StructuredTool(
                name="get_market_news",
                description="Get latest financial and market news",
                func=self._sync_wrapper(self.get_market_news),
                args_schema=NewsQueryInput
            ),
            StructuredTool(
                name="get_economic_indicators",
                description="Get major economic indicators like S&P 500, inflation, interest rates",
                func=self._sync_wrapper(self.get_economic_indicators),
                args_schema=None
            ),
            StructuredTool(
                name="search_educational_content",
                description="Find educational resources to learn about financial topics",
                func=self._sync_wrapper(self.search_educational_content),
                args_schema=EducationQueryInput
            ),
            Tool(
                name="calculate_investment_returns",
                description="Calculate investment returns and compound interest",
                func=self.calculate_investment_returns
            ),
            Tool(
                name="analyze_portfolio_allocation",
                description="Analyze and recommend portfolio allocation based on risk profile",
                func=self.analyze_portfolio_allocation
            )
        ]

        return tools

    # ============= Async to Sync Wrapper =============

    def _sync_wrapper(self, async_func):
        """Wrapper to run async functions in sync context for LangChain"""
        def wrapper(*args, **kwargs):
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is already running (in Jupyter/async context)
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, async_func(*args, **kwargs))
                        return future.result()
                else:
                    # Normal execution
                    return loop.run_until_complete(async_func(*args, **kwargs))
            except Exception as e:
                logger.error(f"Error in sync wrapper: {e}")
                return f"Error: {str(e)}"
        return wrapper

    # ============= Tool Implementation Functions =============

    async def get_stock_data(self, symbol: str) -> str:
        """Get comprehensive stock data"""
        try:
            data = await self.data_manager.get_stock_data(symbol.upper())

            if "error" in data:
                return f"Error fetching data for {symbol}: {data['error']}"

            # Format response for LLM
            response = f"""
📊 Stock Data for {data['symbol']} - {data['company']['name']}

💰 Price Information:
- Current: ${data['price']['current']:.2f}
- Change: {data['price']['change']:.2f} ({data['price']['change_percent']:.2f}%)
- Day Range: ${data['price']['low']:.2f} - ${data['price']['high']:.2f}
- 52 Week Range: ${data['52_week']['low']:.2f} - ${data['52_week']['high']:.2f}

📈 Key Metrics:
- Market Cap: ${data['market_cap']:,.0f}
- P/E Ratio: {f"{data['pe_ratio']:.2f}" if data['pe_ratio'] else 'N/A'}
- Volume: {data['volume']:,}
- Dividend Yield: {f"{data['dividend_yield']*100:.2f}%" if data['dividend_yield'] else 'None'}

🏢 Company:
- Sector: {data['company']['sector']}
- Industry: {data['company']['industry']}

📊 Technical Indicators:
- RSI: {f"{data['technical']['rsi']:.2f}" if data['technical']['rsi'] else 'N/A'}
- 20-Day MA: ${f"{data['technical']['moving_avg']['ma_20']:.2f}" if data['technical']['moving_avg']['ma_20'] else 'N/A'}

💡 Recommendation: {data['recommendation'].upper()}
"""
            return response

        except Exception as e:
            logger.error(f"Error getting stock data: {e}")
            return f"Error fetching stock data: {str(e)}"

    async def search_financial_web(self, query: str, search_type: str = "financial") -> str:
        """Search the web for financial information"""
        try:
            results = await self.data_manager.search_web(query, search_type)

            if not results.get("results"):
                return f"No search results found for: {query}"

            response = f"🔍 Search Results for: {query}\n\n"

            for i, result in enumerate(results["results"][:5], 1):
                response += f"{i}. {result['title']}\n"
                response += f"   {result['snippet'][:200]}...\n"
                if result.get('link'):
                    response += f"   Source: {result['link']}\n"
                response += "\n"

            response += f"\nSources used: {', '.join(results['sources'])}"
            return response

        except Exception as e:
            logger.error(f"Error in web search: {e}")
            return f"Error performing search: {str(e)}"

    async def get_market_news(self, topic: str = "stock market", limit: int = 5) -> str:
        """Get latest market news"""
        try:
            news = await self.data_manager.get_market_news(topic, limit)

            if not news:
                return f"No recent news found for: {topic}"

            response = f"📰 Latest News on {topic}:\n\n"

            for i, article in enumerate(news, 1):
                response += f"{i}. {article['title']}\n"
                response += f"   {article['description'][:150]}...\n"
                response += f"   Source: {article['source']} | {article['published']}\n\n"

            return response

        except Exception as e:
            logger.error(f"Error getting news: {e}")
            return f"Error fetching news: {str(e)}"

    async def get_economic_indicators(self) -> str:
        """Get key economic indicators"""
        try:
            indicators = await self.data_manager.get_economic_indicators()

            response = "📊 Economic Indicators:\n\n"

            for name, data in indicators["data"].items():
                if isinstance(data, dict) and "value" in data:
                    response += f"{name.replace('_', ' ')}:\n"
                    response += f"  Value: {data['value']:.2f}\n"
                    if data.get('change_percent'):
                        response += f"  Change: {data['change_percent']:.2f}%\n"
                response += "\n"

            response += f"\nLast Updated: {indicators['timestamp']}"
            return response

        except Exception as e:
            logger.error(f"Error getting indicators: {e}")
            return f"Error fetching economic indicators: {str(e)}"

    async def search_educational_content(self, topic: str) -> str:
        """Search for educational financial content"""
        try:
            results = await self.data_manager.search_financial_education(topic)

            if not results.get("educational_resources"):
                return f"No educational content found for: {topic}"

            response = f"📚 Educational Resources on {topic}:\n\n"

            for i, resource in enumerate(results["educational_resources"][:5], 1):
                response += f"{i}. {resource['title']}\n"
                response += f"   {resource['snippet'][:200]}...\n\n"

            return response

        except Exception as e:
            logger.error(f"Error searching education content: {e}")
            return f"Error finding educational content: {str(e)}"

    def calculate_investment_returns(self, query: str) -> str:
        """Calculate investment returns based on parameters"""
        try:
            # Parse query for parameters (simplified version)
            # In production, use better parsing or structured input

            # Example calculation
            principal = 10000
            rate = 0.08  # 8% annual
            years = 10

            # Compound interest calculation
            final_amount = principal * (1 + rate) ** years
            total_return = final_amount - principal
            total_return_pct = (total_return / principal) * 100

            response = f"""
💰 Investment Return Calculation:

Initial Investment: ${principal:,.2f}
Annual Return Rate: {rate*100:.1f}%
Investment Period: {years} years

Results:
- Final Amount: ${final_amount:,.2f}
- Total Return: ${total_return:,.2f}
- Total Return %: {total_return_pct:.1f}%
- Average Annual Return: ${total_return/years:,.2f}

📈 If you invest ${principal/years:,.0f} yearly:
- Final Amount: ${principal * (((1 + rate) ** years - 1) / rate):,.2f}

Note: This assumes a constant {rate*100:.1f}% annual return and doesn't account for taxes or inflation.
"""
            return response

        except Exception as e:
            logger.error(f"Error calculating returns: {e}")
            return f"Error calculating returns: {str(e)}"

    def analyze_portfolio_allocation(self, query: str) -> str:
        """Analyze and suggest portfolio allocation"""
        try:
            # Simplified portfolio analysis
            # In production, this would be more sophisticated

            response = """
📊 Recommended Portfolio Allocation:

For Moderate Risk Profile (Age 35):
- 📈 Stocks: 65%
  - US Large Cap: 40%
  - International: 15%
  - Small/Mid Cap: 10%
- 📉 Bonds: 25%
  - Government: 15%
  - Corporate: 10%
- 🏦 Alternatives: 10%
  - Real Estate (REITs): 5%
  - Commodities: 3%
  - Cash: 2%

Key Principles:
1. Age-based allocation: (110 - age)% in stocks
2. Diversify across asset classes
3. Rebalance quarterly
4. Consider tax-advantaged accounts
5. Emergency fund separate (3-6 months expenses)

Risk Assessment:
- Expected Annual Return: 7-9%
- Standard Deviation: 12-15%
- Maximum Drawdown: -20% to -25%

Adjust based on:
- Risk tolerance
- Time horizon
- Financial goals
- Market conditions
"""
            return response

        except Exception as e:
            logger.error(f"Error analyzing portfolio: {e}")
            return f"Error analyzing portfolio: {str(e)}"

# ============= Integration with LangChain Agents =============

def create_financial_agent_with_tools(llm, data_config: Dict[str, Any]):
    """
    Create a LangChain agent with real financial data tools
    """
    from langchain.agents import create_openai_tools_agent, AgentExecutor
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain.memory import ConversationBufferMemory

    # Initialize data manager
    data_manager = DataSourcesManager(data_config)

    # Create toolkit
    toolkit = FinancialToolkit(data_manager)
    tools = toolkit.get_tools()

    # Create prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are FinMentor AI, a knowledgeable financial advisor with access to real-time market data and educational resources.

Your capabilities:
1. Real-time stock data and analysis
2. Market news and economic indicators
3. Educational content search
4. Investment calculations
5. Portfolio analysis

Always:
- Provide data-driven advice
- Cite specific numbers from tools
- Consider user's risk profile
- Explain complex concepts simply
- Warn about risks

Current context: {context}"""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    # Create agent
    agent = create_openai_tools_agent(llm, tools, prompt)

    # Create memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    # Create executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        max_iterations=5
    )

    return agent_executor, toolkit