"""
Market Data Router
Provides stock market data, indices, and corporate announcements
Optimized with Bulk Fetching and Database Caching
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import yfinance as yf
import logging
import httpx
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from services.database import get_db
from models.database import MarketIndex, StockPrice
from pydantic import BaseModel
from curl_cffi import requests

router = APIRouter()
logger = logging.getLogger(__name__)

# ============= SSL/Rate Limit Fix =============
# Create a custom session for yfinance to bypass SSL errors and rate limits
yf_session = requests.Session()
yf_session.verify = False
yf_session.headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

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

# ============= Helper Functions =============

async def fetch_and_store_nifty50(db: AsyncSession):
    """Bulk fetch NIFTY 50 data and store in DB (Incremental Update)"""
    try:
        logger.info("Fetching NIFTY 50 data from Yahoo Finance (Bulk)...")
        
        # 1. Determine Start Date (Smart Gap Fill)
        # Find the oldest 'last_updated' timestamp in DB to ensure we fill gaps for all stocks
        stmt = select(func.min(StockPrice.last_updated))
        result = await db.execute(stmt)
        oldest_update = result.scalar()
        
        # Default to 1 month if DB is empty or data is very old
        start_date = datetime.utcnow() - timedelta(days=30)
        
        if oldest_update:
            # If we have data, fetch from the oldest update time minus a buffer (e.g., 1 day)
            # to ensure we catch any corrections for that day
            oldest_update_naive = oldest_update.replace(tzinfo=None)
            # Ensure we don't go back further than 1 year (to keep fetch fast)
            one_year_ago = datetime.utcnow() - timedelta(days=365)
            
            if oldest_update_naive > one_year_ago:
                start_date = oldest_update_naive - timedelta(days=1)
        
        logger.info(f"Fetching data starting from: {start_date.date()}")
        
        # Bulk download
        tickers = " ".join(NIFTY_50_SYMBOLS)
        # yfinance expects 'start' as string 'YYYY-MM-DD'
        data = yf.download(tickers, start=start_date.strftime("%Y-%m-%d"), interval="1d", group_by='ticker', progress=False, session=yf_session)
        
        updated_count = 0
        
        for symbol in NIFTY_50_SYMBOLS:
            try:
                # Extract data for this symbol
                if len(NIFTY_50_SYMBOLS) > 1:
                    stock_df = data[symbol]
                else:
                    stock_df = data

                if stock_df.empty:
                    continue

                # Get valid close prices
                valid_closes = stock_df['Close'].dropna()
                
                if valid_closes.empty:
                    continue
                    
                current_price = float(valid_closes.iloc[-1])
                
                # Calculate change
                if len(valid_closes) >= 2:
                    prev_price = float(valid_closes.iloc[-2])
                    change = current_price - prev_price
                    change_percent = (change / prev_price) * 100
                else:
                    prev_price = current_price
                    change = 0.0
                    change_percent = 0.0

                # Get volume
                volume = 0
                if 'Volume' in stock_df:
                    valid_volume = stock_df['Volume'].dropna()
                    if not valid_volume.empty:
                        volume = int(valid_volume.iloc[-1])
                
                # Process New History Data
                new_history = []
                try:
                    hist_df = stock_df[['Close']].dropna()
                    for date, row in hist_df.iterrows():
                        new_history.append({
                            "date": date.strftime("%Y-%m-%d"),
                            "price": round(float(row['Close']), 2)
                        })
                except Exception as h_err:
                    logger.warning(f"Error processing history for {symbol}: {h_err}")
                    new_history = []

                # Update or Insert into DB
                clean_symbol = symbol.replace('.NS', '')
                
                stmt = select(StockPrice).where(StockPrice.symbol == clean_symbol)
                result = await db.execute(stmt)
                stock_record = result.scalar_one_or_none()
                
                if stock_record:
                    # MERGE LOGIC: Combine existing history with new history
                    existing_history = stock_record.history or []
                    
                    # Convert to dict for easy merging (Date -> Price)
                    # This automatically updates existing dates with new prices (handling corrections)
                    history_dict = {item['date']: item['price'] for item in existing_history}
                    
                    for item in new_history:
                        history_dict[item['date']] = item['price']
                    
                    # Convert back to list and sort by date
                    merged_history = [
                        {"date": date, "price": price}
                        for date, price in history_dict.items()
                    ]
                    merged_history.sort(key=lambda x: x['date'])
                    
                    # Update record
                    stock_record.current_price = current_price
                    stock_record.change = change
                    stock_record.change_percent = change_percent
                    stock_record.volume = volume
                    stock_record.history = merged_history
                    stock_record.last_updated = datetime.utcnow()
                else:
                    new_stock = StockPrice(
                        symbol=clean_symbol,
                        current_price=current_price,
                        change=change,
                        change_percent=change_percent,
                        volume=volume,
                        history=new_history,
                        last_updated=datetime.utcnow()
                    )
                    db.add(new_stock)
                
                updated_count += 1
                
            except Exception as e:
                logger.warning(f"Error processing {symbol}: {e}")
                continue
        
        await db.commit()
        logger.info(f"Successfully updated {updated_count} NIFTY 50 stocks")
        return updated_count
        
    except Exception as e:
        logger.error(f"Bulk fetch failed: {e}")
        await db.rollback()
        raise e

async def fetch_and_store_indices(db: AsyncSession):
    """Bulk fetch indices and store in DB (Incremental Update)"""
    try:
        indices_map = {
            "^NSEI": "NIFTY 50",
            "^BSESN": "SENSEX",
            "^NSEBANK": "NIFTY BANK",
            "^GSPC": "S&P 500",
            "^DJI": "Dow Jones",
            "^IXIC": "NASDAQ",
            "GC=F": "Gold",
            "CL=F": "Crude Oil",
            "SI=F": "Silver",
            "BTC-USD": "Bitcoin"
        }
        
        logger.info("Fetching Indices data from Yahoo Finance (Bulk)...")
        
        # 1. Determine Start Date (Smart Gap Fill)
        stmt = select(func.min(MarketIndex.last_updated))
        result = await db.execute(stmt)
        oldest_update = result.scalar()
        
        start_date = datetime.utcnow() - timedelta(days=30)
        
        if oldest_update:
            oldest_update_naive = oldest_update.replace(tzinfo=None)
            one_year_ago = datetime.utcnow() - timedelta(days=365)
            if oldest_update_naive > one_year_ago:
                start_date = oldest_update_naive - timedelta(days=1)
        
        logger.info(f"Fetching indices starting from: {start_date.date()}")
        
        tickers = " ".join(indices_map.keys())
        data = yf.download(tickers, start=start_date.strftime("%Y-%m-%d"), interval="1d", group_by='ticker', progress=False, session=yf_session)
        
        for symbol, name in indices_map.items():
            try:
                if len(indices_map) > 1:
                    idx_df = data[symbol]
                else:
                    idx_df = data
                
                if idx_df.empty:
                    continue
                    
                # Get valid close prices
                valid_closes = idx_df['Close'].dropna()
                
                if valid_closes.empty:
                    continue
                    
                current_price = float(valid_closes.iloc[-1])
                
                if len(valid_closes) >= 2:
                    prev_price = float(valid_closes.iloc[-2])
                    change = current_price - prev_price
                    change_percent = (change / prev_price) * 100
                else:
                    change = 0.0
                    change_percent = 0.0
                
                # Process New History
                new_history = []
                try:
                    hist_df = idx_df[['Close']].dropna()
                    for date, row in hist_df.iterrows():
                        new_history.append({
                            "date": date.strftime("%Y-%m-%d"),
                            "price": round(float(row['Close']), 2)
                        })
                except Exception as h_err:
                    logger.warning(f"Error processing history for {symbol}: {h_err}")
                    new_history = []

                # Update DB
                stmt = select(MarketIndex).where(MarketIndex.symbol == symbol)
                result = await db.execute(stmt)
                idx_record = result.scalar_one_or_none()
                
                if idx_record:
                    # MERGE LOGIC
                    existing_history = idx_record.history or []
                    history_dict = {item['date']: item['price'] for item in existing_history}
                    
                    for item in new_history:
                        history_dict[item['date']] = item['price']
                    
                    merged_history = [
                        {"date": date, "price": price}
                        for date, price in history_dict.items()
                    ]
                    merged_history.sort(key=lambda x: x['date'])
                    
                    idx_record.current_price = current_price
                    idx_record.change = change
                    idx_record.change_percent = change_percent
                    idx_record.history = merged_history
                    idx_record.last_updated = datetime.utcnow()
                else:
                    new_idx = MarketIndex(
                        symbol=symbol,
                        name=name,
                        current_price=current_price,
                        change=change,
                        change_percent=change_percent,
                        history=new_history,
                        last_updated=datetime.utcnow()
                    )
                    db.add(new_idx)
                    
            except Exception as e:
                logger.warning(f"Error processing index {symbol}: {e}")
                continue
                
        await db.commit()
        logger.info("Successfully updated indices")
        
    except Exception as e:
        logger.error(f"Indices bulk fetch failed: {e}")
        await db.rollback()

# ============= Market Data Endpoints =============

@router.get("/nifty50-stocks")
async def get_nifty50_stocks(db: AsyncSession = Depends(get_db)):
    """Get NIFTY 50 stocks (Cached in DB)"""
    try:
        # 1. Check if we have fresh data in DB
        stmt = select(StockPrice).limit(1)
        result = await db.execute(stmt)
        sample = result.scalar_one_or_none()
        
        is_stale = True
        if sample:
            # Check if data is less than 5 minutes old
            # Note: sample.last_updated is timezone aware (UTC)
            if sample.last_updated.replace(tzinfo=None) > datetime.utcnow() - timedelta(minutes=5):
                is_stale = False
        
        # 2. If stale or empty, fetch fresh data
        if is_stale:
            await fetch_and_store_nifty50(db)
            
        # 3. Return data from DB
        stmt = select(StockPrice)
        result = await db.execute(stmt)
        stocks = result.scalars().all()
        
        formatted_stocks = []
        for stock in stocks:
            formatted_stocks.append({
                "symbol": stock.symbol,
                "company_name": stock.symbol, # We can improve this with a mapping later
                "current_price": stock.current_price,
                "change": stock.change,
                "change_percent": stock.change_percent,
                "volume": stock.volume,
                "market_cap": stock.market_cap
            })
            
        return {
            "successful_fetches": len(formatted_stocks),
            "total_stocks": len(NIFTY_50_SYMBOLS),
            "stocks": formatted_stocks,
            "failed_symbols": []
        }
        
    except Exception as e:
        logger.error(f"Error in get_nifty50_stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/live-indices")
async def get_live_indices(db: AsyncSession = Depends(get_db)):
    """Get live indices (Cached in DB)"""
    try:
        # 1. Check freshness
        stmt = select(MarketIndex).limit(1)
        result = await db.execute(stmt)
        sample = result.scalar_one_or_none()
        
        is_stale = True
        if sample:
            if sample.last_updated.replace(tzinfo=None) > datetime.utcnow() - timedelta(minutes=1):
                is_stale = False
                
        # 2. Update if stale
        if is_stale:
            await fetch_and_store_indices(db)
            
        # 3. Return from DB
        stmt = select(MarketIndex)
        result = await db.execute(stmt)
        indices = result.scalars().all()
        
        # Group by category
        indian_markets = []
        global_markets = []
        commodities = []
        
        indian_symbols = ["^NSEI", "^BSESN", "^NSEBANK"]
        global_symbols = ["^GSPC", "^DJI", "^IXIC"]
        commodity_symbols = ["GC=F", "CL=F", "SI=F", "BTC-USD"]
        
        for idx in indices:
            data = {
                "symbol": idx.symbol,
                "name": idx.name,
                "current_price": idx.current_price,
                "change": idx.change,
                "change_percent": idx.change_percent,
                "history": idx.history,
                "last_updated": idx.last_updated.isoformat()
            }
            
            if idx.symbol in indian_symbols:
                indian_markets.append(data)
            elif idx.symbol in global_symbols:
                global_markets.append(data)
            elif idx.symbol in commodity_symbols:
                commodities.append(data)
                
        return {
            "indian_markets": indian_markets,
            "global_markets": global_markets,
            "commodities": commodities
        }
        
    except Exception as e:
        logger.error(f"Error in get_live_indices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stocks", response_model=List[StockData])
async def get_stocks(
    category: str = Query(..., description="Category: gainers, losers, active"),
    cap: str = Query("large", description="Market cap: large, mid, small")
):
    """Get stocks by category (gainers/losers/active) and market cap"""
    # For now, we'll just reuse the NIFTY 50 logic but filter it
    # Ideally, this should also use the DB
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
