"""
Market Data Router
Provides stock market data, indices, and corporate announcements
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import yfinance as yf
import logging
import httpx
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)

# ============= Response Models =============

class StockData(BaseModel):
    """Stock data response"""
    symbol: str
    name: str
    price: float
    change: float
    changePercent: float
    volume: Optional[int] = None
    marketCap: Optional[float] = None

class IndexData(BaseModel):
    """Market index data"""
    name: str
    value: float
    change: float
    changePercent: float
    timestamp: str

class AnnouncementData(BaseModel):
    """Corporate announcement"""
    company: str
    category: str
    subject: str
    date: str
    attachment: Optional[str] = None

# ============= NIFTY 50 Stocks =============

NIFTY_50_SYMBOLS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "HCLTECH.NS",
    "SUNPHARMA.NS", "BAJFINANCE.NS", "TITAN.NS", "ULTRACEMCO.NS", "WIPRO.NS",
    "NESTLEIND.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "M&M.NS",
    "TATAMOTORS.NS", "TECHM.NS", "ADANIPORTS.NS", "COALINDIA.NS", "BAJAJFINSV.NS",
    "HINDALCO.NS", "GRASIM.NS", "DIVISLAB.NS", "DRREDDY.NS", "CIPLA.NS",
    "BRITANNIA.NS", "EICHERMOT.NS", "HEROMOTOCO.NS", "TATACONSUM.NS", "SHREECEM.NS",
    "INDUSINDBK.NS", "APOLLOHOSP.NS", "JSWSTEEL.NS", "TATASTEEL.NS", "BPCL.NS",
    "UPL.NS", "BAJAJ-AUTO.NS", "SBILIFE.NS", "HDFCLIFE.NS", "ADANIENT.NS"
]

# ============= Market Data Endpoints =============

@router.get("/nifty50-stocks")
async def get_nifty50_stocks():
    """Get current data for all NIFTY 50 stocks"""
    try:
        stocks_data = []
        failed_symbols = []
        
        # Fetch data in batches to avoid rate limiting
        for symbol in NIFTY_50_SYMBOLS:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="2d")
                
                if len(hist) >= 2:
                    current_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[-2]
                    change = current_price - prev_price
                    change_percent = (change / prev_price) * 100
                else:
                    # Fallback to current data only
                    current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
                    change = info.get('regularMarketChange', 0)
                    change_percent = info.get('regularMarketChangePercent', 0)
                
                stock_data = {
                    "symbol": symbol.replace('.NS', ''),
                    "company_name": info.get('longName', info.get('shortName', symbol)),
                    "current_price": round(current_price, 2),
                    "change": round(change, 2),
                    "change_percent": round(change_percent, 2),
                    "volume": info.get('volume'),
                    "market_cap": info.get('marketCap')
                }
                stocks_data.append(stock_data)
                
            except Exception as e:
                logger.warning(f"Failed to fetch data for {symbol}: {e}")
                failed_symbols.append(symbol)
                continue
        
        if not stocks_data:
            raise HTTPException(status_code=503, detail="Unable to fetch market data")
        
        # Return wrapped response matching frontend expectations
        return {
            "successful_fetches": len(stocks_data),
            "total_stocks": len(NIFTY_50_SYMBOLS),
            "stocks": stocks_data,
            "failed_symbols": failed_symbols
        }
        
    except Exception as e:
        logger.error(f"Error fetching NIFTY 50 data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch NIFTY 50 data: {str(e)}")


@router.get("/live-indices")
async def get_live_indices():
    """Get live data for major Indian indices, global markets, and commodities"""
    try:
        # Indian indices
        indian_indices = {
            "^NSEI": "NIFTY 50",
            "^BSESN": "SENSEX",
            "^NSEBANK": "NIFTY BANK"
            # Note: ^NSEIT is delisted, removed to prevent errors
        }
        
        # Global indices
        global_indices = {
            "^GSPC": "S&P 500",
            "^DJI": "Dow Jones",
            "^IXIC": "NASDAQ",
            "^FTSE": "FTSE 100"
        }
        
        # Commodities
        commodities = {
            "GC=F": "Gold",
            "CL=F": "Crude Oil",
            "SI=F": "Silver",
            "BTC-USD": "Bitcoin"
        }
        
        def fetch_indices(symbols_dict):
            data = []
            for symbol, name in symbols_dict.items():
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="2d")
                    
                    if len(hist) >= 2:
                        current_value = hist['Close'].iloc[-1]
                        prev_value = hist['Close'].iloc[-2]
                        change = current_value - prev_value
                        change_percent = (change / prev_value) * 100
                        
                        index_data = {
                            "name": name,
                            "current_price": round(current_value, 2),
                            "change": round(change, 2),
                            "change_percent": round(change_percent, 2),
                            "last_updated": datetime.now().isoformat()
                        }
                        data.append(index_data)
                        
                except Exception as e:
                    logger.warning(f"Failed to fetch {name}: {e}")
                    continue
            return data
        
        indian_data = fetch_indices(indian_indices)
        global_data = fetch_indices(global_indices)
        commodities_data = fetch_indices(commodities)
        
        # Return structured response matching frontend expectations
        return {
            "indian_markets": indian_data,
            "global_markets": global_data,
            "commodities": commodities_data
        }
        
    except Exception as e:
        logger.error(f"Error fetching indices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch indices: {str(e)}")


@router.get("/stocks", response_model=List[StockData])
async def get_stocks(
    category: str = Query(..., description="Category: gainers, losers, active"),
    cap: str = Query("large", description="Market cap: large, mid, small")
):
    """Get stocks by category (gainers/losers/active) and market cap"""
    try:
        # Use NIFTY 50 as base for large cap
        if cap == "large":
            symbols = NIFTY_50_SYMBOLS[:20]  # Top 20 for performance
        else:
            # For mid/small cap, use a subset
            symbols = NIFTY_50_SYMBOLS[20:35]
        
        stocks_data = []
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")
                info = ticker.info
                
                if len(hist) >= 2:
                    current_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[-2]
                    change = current_price - prev_price
                    change_percent = (change / prev_price) * 100
                    
                    stock_data = StockData(
                        symbol=symbol.replace('.NS', ''),
                        name=info.get('longName', info.get('shortName', symbol)),
                        price=round(current_price, 2),
                        change=round(change, 2),
                        changePercent=round(change_percent, 2),
                        volume=hist['Volume'].iloc[-1] if 'Volume' in hist else None,
                        marketCap=info.get('marketCap')
                    )
                    stocks_data.append(stock_data)
                    
            except Exception as e:
                logger.warning(f"Failed to fetch {symbol}: {e}")
                continue
        
        # Filter by category
        if category == "gainers":
            stocks_data = sorted(stocks_data, key=lambda x: x.changePercent, reverse=True)[:10]
        elif category == "losers":
            stocks_data = sorted(stocks_data, key=lambda x: x.changePercent)[:10]
        elif category == "active":
            stocks_data = sorted(stocks_data, key=lambda x: x.volume or 0, reverse=True)[:10]
        
        return stocks_data
        
    except Exception as e:
        logger.error(f"Error fetching stocks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch stocks: {str(e)}")


# ============= Corporate Announcements (CORS Proxy) =============

@router.get("/announcements", response_model=List[AnnouncementData])
async def get_announcements(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    category: str = Query("Company Update", description="Announcement category")
):
    """Proxy endpoint for BSE India corporate announcements (fixes CORS)"""
    try:
        # BSE India API endpoint
        url = "https://api.bseindia.com/BseIndiaAPI/api/AnnGetData/w"
        params = {
            "strCat": category,
            "strPrevDate": date,
            "strScrip": ""
        }
        
        # Make request from backend (no CORS issues)
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse and format the response
            announcements = []
            if isinstance(data, list):
                for item in data[:50]:  # Limit to 50 announcements
                    announcement = AnnouncementData(
                        company=item.get('SCRIP_CD', ''),
                        category=item.get('CATEGORYNAME', category),
                        subject=item.get('NEWS_SUBJECT', ''),
                        date=item.get('NEWS_DT', date),
                        attachment=item.get('ATTACHMENTNAME')
                    )
                    announcements.append(announcement)
            
            return announcements
            
    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching announcements: {e}")
        # Return empty list instead of error when BSE API is down
        return []
    except Exception as e:
        logger.error(f"Error fetching announcements: {e}")
        # Return empty list instead of error for graceful degradation
        return []


@router.get("/stock/{symbol}")
async def get_stock_detail(symbol: str):
    """Get detailed information for a specific stock"""
    try:
        # Add .NS suffix for NSE stocks if not present
        if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
            symbol = f"{symbol}.NS"
        
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="1mo")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail="Stock not found")
        
        current_price = hist['Close'].iloc[-1]
        prev_close = info.get('previousClose', hist['Close'].iloc[-2] if len(hist) >= 2 else current_price)
        change = current_price - prev_close
        change_percent = (change / prev_close) * 100 if prev_close else 0
        
        return {
            "symbol": symbol.replace('.NS', '').replace('.BO', ''),
            "name": info.get('longName', info.get('shortName', symbol)),
            "price": round(current_price, 2),
            "change": round(change, 2),
            "changePercent": round(change_percent, 2),
            "volume": int(hist['Volume'].iloc[-1]) if 'Volume' in hist else None,
            "marketCap": info.get('marketCap'),
            "pe": info.get('trailingPE'),
            "eps": info.get('trailingEps'),
            "high52w": info.get('fiftyTwoWeekHigh'),
            "low52w": info.get('fiftyTwoWeekLow'),
            "sector": info.get('sector'),
            "industry": info.get('industry'),
            "history": [
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "open": round(row['Open'], 2),
                    "high": round(row['High'], 2),
                    "low": round(row['Low'], 2),
                    "close": round(row['Close'], 2),
                    "volume": int(row['Volume']) if 'Volume' in row else None
                }
                for date, row in hist.iterrows()
            ][-30:]  # Last 30 days
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stock detail for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch stock details: {str(e)}"
        )
