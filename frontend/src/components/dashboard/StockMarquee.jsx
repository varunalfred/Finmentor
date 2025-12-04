import React, { useMemo } from 'react';
import { useNifty50Stocks } from '../../hooks/useNifty50Stocks';
import './StockMarquee.css';

const StockMarquee = () => {
  const { data: stocks, isLoading: loading } = useNifty50Stocks();

  // NIFTY 50 component stocks for fallback
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

  const nifty50Stocks = useMemo(() => {
    if (stocks && stocks.length > 0) return stocks;

    // Fallback data if API fails or returns empty
    if (!loading) {
      console.log('⚠️ Using fallback data for Stock Marquee');
      return nifty50Symbols.map((symbol, index) => ({
        symbol: symbol,
        company_name: symbol.replace('.NS', ''),
        current_price: 1000 + (index * 50),
        change: (Math.random() - 0.5) * 50,
        change_percent: (Math.random() - 0.5) * 3
      }));
    }
    return [];
  }, [stocks, loading]);

  const getChangeClass = (change) => {
    if (change > 0) return 'positive';
    if (change < 0) return 'negative';
    return 'neutral';
  };

  const formatPrice = (price) => {
    return `₹${price.toFixed(2)}`;
  };

  if (loading && nifty50Stocks.length === 0) {
    return (
      <div className="stock-marquee-container">
        <div className="marquee-loading">Loading NIFTY 50 stocks...</div>
      </div>
    );
  }

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
