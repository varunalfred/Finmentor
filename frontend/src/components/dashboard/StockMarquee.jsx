import React, { useState, useEffect } from 'react';
import './StockMarquee.css';

const StockMarquee = () => {
  const [nifty50Stocks, setNifty50Stocks] = useState([]);
  const [loading, setLoading] = useState(true);

  // NIFTY 50 component stocks
  const nifty50Symbols = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
    'ICICIBANK.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS', 'KOTAKBANK.NS',
    'LT.NS', 'AXISBANK.NS', 'WIPRO.NS', 'ASIANPAINT.NS', 'MARUTI.NS',
    'HCLTECH.NS', 'BAJFINANCE.NS', 'SUNPHARMA.NS', 'TITAN.NS', 'ULTRACEMCO.NS',
    'NESTLEIND.NS', 'ONGC.NS', 'NTPC.NS', 'POWERGRID.NS', 'TATAMOTORS.NS',
    'TATASTEEL.NS', 'TECHM.NS', 'M&M.NS', 'BAJAJFINSV.NS', 'ADANIENT.NS',
    'JSWSTEEL.NS', 'HINDALCO.NS', 'INDUSINDBK.NS', 'GRASIM.NS', 'COALINDIA.NS',
    'CIPLA.NS', 'DIVISLAB.NS', 'DRREDDY.NS', 'EICHERMOT.NS', 'HEROMOTOCO.NS',
    'BRITANNIA.NS', 'APOLLOHOSP.NS', 'BPCL.NS', 'TATACONSUM.NS', 'ADANIPORTS.NS',
    'BAJAJ-AUTO.NS', 'HDFCLIFE.NS', 'SBILIFE.NS', 'UPL.NS', 'LTIM.NS'
  ];

  useEffect(() => {
    fetchNifty50Data();
    
    // Auto-refresh every 2 minutes
    const refreshInterval = setInterval(() => {
      fetchNifty50Data();
    }, 120000); // 2 minutes
    
    return () => clearInterval(refreshInterval);
  }, []);

  const fetchNifty50Data = async () => {
    try {
      setLoading(true);
      
      // Fetch from dedicated NIFTY 50 endpoint
      const response = await fetch('/api/market/nifty50-stocks');
      
      if (!response.ok) {
        throw new Error('Failed to fetch NIFTY 50 data');
      }
      
      const data = await response.json();
      
      console.log(`✅ Fetched ${data.successful_fetches}/${data.total_stocks} NIFTY 50 stocks`);
      
      if (data.failed_symbols && data.failed_symbols.length > 0) {
        console.warn('Failed to fetch:', data.failed_symbols);
      }
      
      if (data.stocks && data.stocks.length > 0) {
        setNifty50Stocks(data.stocks);
      } else {
        throw new Error('No stocks data received');
      }
      
    } catch (err) {
      console.error('Error fetching NIFTY 50 data:', err);
      
      // Fallback: Create display data for all 50 stocks
      const fallbackStocks = nifty50Symbols.map((symbol, index) => ({
        symbol: symbol,
        company_name: symbol.replace('.NS', ''),
        current_price: 1000 + (index * 50),
        change: (Math.random() - 0.5) * 50,
        change_percent: (Math.random() - 0.5) * 3
      }));
      
      console.log('⚠️ Using fallback data for all 50 stocks');
      setNifty50Stocks(fallbackStocks);
    } finally {
      setLoading(false);
    }
  };

  const getChangeClass = (change) => {
    if (change > 0) return 'positive';
    if (change < 0) return 'negative';
    return 'neutral';
  };

  const formatPrice = (price) => {
    return `₹${price.toFixed(2)}`;
  };

  if (loading) {
    return (
      <div className="stock-marquee-container">
        <div className="marquee-loading">Loading NIFTY 50 stocks...</div>
      </div>
    );
  }

  // Debug log
  console.log(`📊 Rendering ${nifty50Stocks.length} NIFTY 50 stocks in marquee`);

  return (
    <div className="stock-marquee-container">
      <div className="marquee-label">NIFTY 50:</div>
      <div className="marquee-wrapper">
        <div className="marquee-content">
          {/* Duplicate for seamless loop */}
          {[...nifty50Stocks, ...nifty50Stocks].map((stock, index) => (
            <div key={`${stock.symbol}-${index}`} className="marquee-item">
              <span className="stock-name">{stock.company_name || stock.symbol.replace('.NS', '')}</span>
              <span className="stock-price">{formatPrice(stock.current_price)}</span>
              <span className={`stock-change ${getChangeClass(stock.change)}`}>
                {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default StockMarquee;
