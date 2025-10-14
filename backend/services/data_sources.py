"""
Data Sources Integration Service
Combines multiple APIs for comprehensive financial data
"""

import os  # For environment variables
import asyncio  # For async operations
import aiohttp  # For async HTTP requests
from typing import Dict, Any, List, Optional  # Type hints
from datetime import datetime, timedelta  # Date/time operations
import yfinance as yf  # Yahoo Finance API
import json  # JSON parsing
from duckduckgo_search import DDGS, AsyncDDGS  # DuckDuckGo search (no API key needed)
import pandas as pd  # Data manipulation
import logging  # For logging events
from functools import lru_cache  # For caching function results
import hashlib  # For generating cache keys

logger = logging.getLogger(__name__)

class DataSourcesManager:
    """
    Manages multiple data sources for financial information
    Includes: Yahoo Finance, DuckDuckGo, Google Search, News APIs, Economic Data
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}  # Configuration settings
        self.cache = {}  # Cache for API results to reduce calls
        self.cache_ttl = 300  # Cache time-to-live: 5 minutes

        # Initialize API wrappers
        self._init_search_apis()  # Setup search engines
        self._init_financial_apis()  # Setup financial data sources

    def _init_search_apis(self):
        """Initialize search APIs"""

        # DuckDuckGo Search - no API key needed (always available)
        self.ddg_search = AsyncDDGS()  # Async version for performance
        self.ddg_sync = DDGS()  # Sync version as fallback
        logger.info("DuckDuckGo Search initialized")  # Log success

        # Google Search (optional - needs API keys)
        if os.getenv("GOOGLE_API_KEY") and os.getenv("GOOGLE_CSE_ID"):  # Check if keys exist
            try:
                from langchain_community.tools import GoogleSearchAPIWrapper  # Import Google wrapper
                self.google_search = GoogleSearchAPIWrapper(
                    google_api_key=os.getenv("GOOGLE_API_KEY"),  # API key
                    google_cse_id=os.getenv("GOOGLE_CSE_ID"),  # Custom Search Engine ID
                    k=5  # Return 5 results
                )
                logger.info("Google Search API initialized")  # Log success
            except ImportError:
                self.google_search = None  # Not available
        else:
            self.google_search = None  # No keys provided

        # SerpAPI (optional - for search results with metadata)
        self.serp_search = None  # Default to None
        if os.getenv("SERPAPI_API_KEY"):  # Check if API key exists
            try:
                from langchain_community.utilities import SerpAPIWrapper  # Import wrapper
                self.serp_search = SerpAPIWrapper(
                    serpapi_api_key=os.getenv("SERPAPI_API_KEY"),  # API key
                    params={"engine": "google", "gl": "us", "hl": "en"}  # US English Google results
                )
                logger.info("SerpAPI initialized")  # Log success
            except ImportError:
                pass  # Library not installed, skip

        # Bing Search (optional - placeholder for future)
        self.bing_search = None  # Not implemented yet

    def _init_financial_apis(self):
        """Initialize financial data APIs"""

        # Yahoo Finance (always available - no API key needed)
        self.yfinance = yf  # Assign yfinance module
        logger.info("Yahoo Finance initialized")  # Log success

        # Alpha Vantage (optional - for detailed market data)
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")  # Get API key if available

        # NewsAPI (optional - for financial news)
        self.news_api_key = os.getenv("NEWS_API_KEY")  # Get API key if available

        # Financial Modeling Prep (optional - for fundamental data)
        self.fmp_api_key = os.getenv("FMP_API_KEY")  # Get API key if available

    # ============= Search Functions =============

    async def search_web(self, query: str, search_type: str = "general") -> Dict[str, Any]:
        """
        Search the web using available search APIs
        DuckDuckGo is primary (no key needed), others are optional enhancements
        """

        # Add context to query based on search type
        if search_type == "financial":  # Financial searches
            query = f"finance investing {query}"  # Add financial keywords
        elif search_type == "news":  # News searches
            query = f"latest news {query}"  # Add news keywords
        elif search_type == "educational":  # Educational content
            query = f"learn understand {query}"  # Add learning keywords

        results = {
            "query": query,  # The search query
            "search_type": search_type,  # Type of search
            "sources": [],  # Which APIs returned results
            "results": []  # The actual search results
        }

        # Always try DuckDuckGo first (no API key needed)
        try:
            ddg_results = []  # Collect results
            async for r in self.ddg_search.text(query, max_results=5):  # Search asynchronously
                ddg_results.append({
                    "title": r.get("title", ""),  # Result title
                    "snippet": r.get("body", ""),  # Result description
                    "link": r.get("href", ""),  # Result URL
                    "source": "duckduckgo"  # Mark source
                })

            if ddg_results:  # If we got results
                results["sources"].append("duckduckgo")  # Add source
                results["results"].extend(ddg_results)  # Add results
        except Exception as e:
            logger.error(f"DuckDuckGo async search error: {e}")  # Log error
            # Try sync version as fallback
            try:
                ddg_results = list(self.ddg_sync.text(query, max_results=5))  # Sync search
                for r in ddg_results:  # Process each result
                    results["results"].append({
                        "title": r.get("title", ""),  # Title
                        "snippet": r.get("body", ""),  # Description
                        "link": r.get("href", ""),  # URL
                        "source": "duckduckgo"  # Source
                    })
                if results["results"]:  # If we got results
                    results["sources"].append("duckduckgo")  # Add source
            except Exception as e2:
                logger.error(f"DuckDuckGo sync search error: {e2}")  # Log fallback error

        # Optionally enhance with Google if available and needed
        if len(results["results"]) < 3 and self.google_search:  # Need more results and have Google?
            try:
                google_results = await self._async_wrapper(  # Run sync function asynchronously
                    self.google_search.run, query  # Search Google
                )
                results["sources"].append("google")
                results["results"].extend(self._parse_search_results(google_results, "google"))
            except Exception as e:
                logger.debug(f"Google search error: {e}")

        return results

    # ============= Financial Data Functions =============

    async def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive stock data"""

        cache_key = f"stock_{symbol}_{datetime.now().strftime('%Y%m%d%H')}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            ticker = self.yfinance.Ticker(symbol)

            # Get various data points
            info = ticker.info
            history = ticker.history(period="1mo")

            data = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "price": {
                    "current": info.get("currentPrice", info.get("regularMarketPrice")),
                    "open": info.get("open", info.get("regularMarketOpen")),
                    "high": info.get("dayHigh"),
                    "low": info.get("dayLow"),
                    "previous_close": info.get("previousClose"),
                    "change": info.get("regularMarketChange"),
                    "change_percent": info.get("regularMarketChangePercent")
                },
                "volume": info.get("volume", info.get("regularMarketVolume")),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "dividend_yield": info.get("dividendYield"),
                "52_week": {
                    "high": info.get("fiftyTwoWeekHigh"),
                    "low": info.get("fiftyTwoWeekLow")
                },
                "company": {
                    "name": info.get("longName", symbol),
                    "sector": info.get("sector"),
                    "industry": info.get("industry"),
                    "description": info.get("longBusinessSummary", "")[:500]
                },
                "technical": {
                    "rsi": await self._calculate_rsi(history),
                    "moving_avg": {
                        "ma_20": history['Close'].rolling(window=20).mean().iloc[-1] if len(history) >= 20 else None,
                        "ma_50": None  # Would need more history
                    }
                },
                "recommendation": info.get("recommendationKey", "none")
            }

            self.cache[cache_key] = data
            return data

        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            return {"error": str(e), "symbol": symbol}

    async def get_market_news(self, topic: str = "finance", limit: int = 5) -> List[Dict[str, Any]]:
        """Get latest financial news"""

        news_items = []

        # Try NewsAPI first
        if self.news_api_key:
            try:
                async with aiohttp.ClientSession() as session:
                    url = "https://newsapi.org/v2/everything"
                    params = {
                        "q": topic,
                        "apiKey": self.news_api_key,
                        "language": "en",
                        "sortBy": "popularity",
                        "pageSize": limit
                    }

                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            for article in data.get("articles", []):
                                news_items.append({
                                    "title": article.get("title"),
                                    "description": article.get("description"),
                                    "url": article.get("url"),
                                    "source": article.get("source", {}).get("name"),
                                    "published": article.get("publishedAt"),
                                    "api": "newsapi"
                                })
            except Exception as e:
                logger.error(f"NewsAPI error: {e}")

        # Fallback to Yahoo Finance news
        if not news_items:
            try:
                # Get news for major indices
                tickers = ["^GSPC", "^DJI", "^IXIC"]  # S&P 500, Dow, Nasdaq
                for ticker_symbol in tickers[:1]:  # Just use S&P 500 for general news
                    ticker = self.yfinance.Ticker(ticker_symbol)
                    yahoo_news = ticker.news

                    for item in yahoo_news[:limit]:
                        news_items.append({
                            "title": item.get("title"),
                            "description": item.get("summary", ""),
                            "url": item.get("link"),
                            "source": "Yahoo Finance",
                            "published": datetime.fromtimestamp(
                                item.get("providerPublishTime", 0)
                            ).isoformat(),
                            "api": "yahoo"
                        })

                    if news_items:
                        break

            except Exception as e:
                logger.error(f"Yahoo Finance news error: {e}")

        return news_items

    async def get_economic_indicators(self) -> Dict[str, Any]:
        """Get key economic indicators"""

        indicators = {
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

        # Get major indices from Yahoo Finance
        try:
            indices = {
                "S&P_500": "^GSPC",
                "DOW_JONES": "^DJI",
                "NASDAQ": "^IXIC",
                "VIX": "^VIX",
                "GOLD": "GC=F",
                "OIL": "CL=F",
                "10Y_TREASURY": "^TNX"
            }

            for name, symbol in indices.items():
                ticker = self.yfinance.Ticker(symbol)
                info = ticker.info

                indicators["data"][name] = {
                    "value": info.get("regularMarketPrice", info.get("previousClose")),
                    "change": info.get("regularMarketChange"),
                    "change_percent": info.get("regularMarketChangePercent")
                }

        except Exception as e:
            logger.error(f"Error fetching economic indicators: {e}")

        # Add Fed funds rate and inflation if available via Alpha Vantage
        if self.alpha_vantage_key:
            indicators["data"]["FED_RATE"] = await self._get_fed_rate()
            indicators["data"]["INFLATION"] = await self._get_inflation_rate()

        return indicators

    # ============= Specialized Financial APIs =============

    async def get_company_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Get detailed company fundamentals"""

        if self.fmp_api_key:
            # Use Financial Modeling Prep API
            async with aiohttp.ClientSession() as session:
                url = f"https://financialmodelingprep.com/api/v3/profile/{symbol}"
                params = {"apikey": self.fmp_api_key}

                try:
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data[0] if data else {}
                except Exception as e:
                    logger.error(f"FMP API error: {e}")

        # Fallback to Yahoo Finance
        return await self.get_stock_data(symbol)

    async def search_financial_education(self, topic: str) -> Dict[str, Any]:
        """Search for educational financial content"""

        # Add educational context to search
        educational_queries = [
            f"learn {topic} for beginners",
            f"{topic} explained simply",
            f"understanding {topic} finance",
            f"{topic} tutorial investing"
        ]

        all_results = []

        for query in educational_queries[:2]:  # Limit to avoid rate limits
            results = await self.search_web(query, "educational")
            all_results.extend(results.get("results", []))

        # Deduplicate results
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result.get("link") not in seen_urls:
                seen_urls.add(result.get("link"))
                unique_results.append(result)

        return {
            "topic": topic,
            "educational_resources": unique_results[:10]
        }

    # ============= Helper Functions =============

    async def _async_wrapper(self, func, *args, **kwargs):
        """Wrapper to run sync functions in async context"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)

    def _parse_search_results(self, raw_results: Any, source: str) -> List[Dict[str, str]]:
        """Parse search results from different sources"""

        if isinstance(raw_results, str):
            # Simple text results
            return [{
                "title": "Search Result",
                "snippet": raw_results[:500],
                "link": "",
                "source": source
            }]

        # Structured results would need more parsing
        return []

    async def _calculate_rsi(self, history: pd.DataFrame, period: int = 14) -> Optional[float]:
        """Calculate Relative Strength Index"""
        try:
            if len(history) < period:
                return None

            delta = history['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            return float(rsi.iloc[-1])
        except Exception:
            return None

    async def _get_fed_rate(self) -> Optional[Dict[str, Any]]:
        """Get Federal Reserve interest rate"""
        if not self.alpha_vantage_key:
            return None

        try:
            async with aiohttp.ClientSession() as session:
                url = "https://www.alphavantage.co/query"
                params = {
                    "function": "FEDERAL_FUNDS_RATE",
                    "apikey": self.alpha_vantage_key,
                    "interval": "monthly"
                }

                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "data" in data and data["data"]:
                            latest = data["data"][0]
                            return {
                                "value": float(latest.get("value", 0)),
                                "date": latest.get("date")
                            }
        except Exception as e:
            logger.error(f"Error fetching Fed rate: {e}")

        return None

    async def _get_inflation_rate(self) -> Optional[Dict[str, Any]]:
        """Get inflation rate (CPI)"""
        if not self.alpha_vantage_key:
            return None

        try:
            async with aiohttp.ClientSession() as session:
                url = "https://www.alphavantage.co/query"
                params = {
                    "function": "CPI",
                    "apikey": self.alpha_vantage_key,
                    "interval": "monthly"
                }

                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "data" in data and len(data["data"]) >= 13:
                            latest = float(data["data"][0].get("value", 0))
                            year_ago = float(data["data"][12].get("value", 0))
                            inflation = ((latest - year_ago) / year_ago) * 100

                            return {
                                "value": round(inflation, 2),
                                "date": data["data"][0].get("date")
                            }
        except Exception as e:
            logger.error(f"Error fetching inflation rate: {e}")

        return None

    async def aggregate_data_for_query(self, query: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate data from multiple sources for a comprehensive response
        This is the main entry point for the DSPy/LangChain agents
        """

        aggregated = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

        # Extract entities from query (stocks, topics, etc.)
        entities = self._extract_entities(query)

        # Parallel data fetching
        tasks = []

        # Add relevant data fetching tasks based on query
        if entities.get("stocks"):
            for symbol in entities["stocks"][:3]:  # Limit to 3 stocks
                tasks.append(self.get_stock_data(symbol))

        if entities.get("search_needed"):
            tasks.append(self.search_web(query, "financial"))

        if entities.get("news_needed"):
            tasks.append(self.get_market_news(query))

        if entities.get("education_needed"):
            tasks.append(self.search_financial_education(entities.get("topic", query)))

        # Always get market overview
        tasks.append(self.get_economic_indicators())

        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Task error: {result}")
            elif isinstance(result, dict):
                if "symbol" in result:
                    aggregated["data"]["stocks"] = aggregated["data"].get("stocks", [])
                    aggregated["data"]["stocks"].append(result)
                else:
                    # Merge other data
                    for key, value in result.items():
                        if key not in ["query", "timestamp"]:
                            aggregated["data"][key] = value

        return aggregated

    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract entities from query for targeted data fetching"""

        entities = {
            "stocks": [],
            "search_needed": False,
            "news_needed": False,
            "education_needed": False,
            "topic": ""
        }

        # Simple pattern matching for stock symbols
        import re

        # Look for stock symbols (1-5 uppercase letters)
        stock_pattern = r'\b[A-Z]{1,5}\b'
        potential_stocks = re.findall(stock_pattern, query)

        # Common stock symbols to validate against
        common_stocks = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA",
                        "JPM", "V", "JNJ", "WMT", "PG", "MA", "HD", "DIS", "PYPL",
                        "NFLX", "ADBE", "PFE", "KO", "PEP", "VZ", "INTC", "CSCO"]

        entities["stocks"] = [s for s in potential_stocks if s in common_stocks]

        # Detect query intent
        query_lower = query.lower()

        if any(word in query_lower for word in ["news", "latest", "today", "recent"]):
            entities["news_needed"] = True

        if any(word in query_lower for word in ["what is", "explain", "learn", "understand", "how does"]):
            entities["education_needed"] = True
            entities["topic"] = query.split("what is")[-1].split("explain")[-1].strip()

        if any(word in query_lower for word in ["should", "invest", "buy", "sell", "analysis"]):
            entities["search_needed"] = True

        return entities