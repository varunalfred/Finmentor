import React, { useState, useEffect, useRef } from 'react';
import './LiveMarketIndicators.css';

const LiveMarketIndicators = () => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [marketData, setMarketData] = useState({
    indian_markets: [],
    global_markets: [],
    commodities: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);

  // Slide configuration - 4 indices per slide
  const slides = [
    {
      title: 'Indian Markets',
      indices: ['SENSEX', 'NIFTY 50', 'BANK NIFTY', 'NIFTY IT'],
      key: 'indian_markets'
    },
    {
      title: 'Global Markets',
      indices: ['NIKKEI 225', 'NASDAQ', 'DOW JONES', 'S&P 500'],
      key: 'global_markets'
    },
    {
      title: 'Commodities',
      indices: ['CRUDE OIL', 'GOLD', 'SILVER', 'NATURAL GAS'],
      key: 'commodities'
    }
  ];

  // Fetch market data
  const fetchMarketData = async () => {
    try {
      const response = await fetch('/api/market/live-indices');
      if (!response.ok) {
        throw new Error('Failed to fetch market data');
      }
      const data = await response.json();
      setMarketData(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching market data:', err);
      setError('Unable to load market data');
    } finally {
      setLoading(false);
    }
  };

  // Initial data load
  useEffect(() => {
    fetchMarketData();
    // Auto-refresh every 30 seconds
    const refreshInterval = setInterval(fetchMarketData, 30000);
    return () => clearInterval(refreshInterval);
  }, []);

  // Auto-rotate carousel every 5 seconds
  useEffect(() => {
    intervalRef.current = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % slides.length);
    }, 5000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [slides.length]);

  const formatValue = (value) => {
    if (value >= 1000) {
      return value.toLocaleString('en-IN', { 
        minimumFractionDigits: 2, 
        maximumFractionDigits: 2 
      });
    }
    return value.toFixed(2);
  };

  const formatChange = (change) => {
    const formatted = Math.abs(change).toFixed(2);
    return change >= 0 ? `+${formatted}` : `-${formatted}`;
  };

  const formatChangePercent = (percent) => {
    const formatted = Math.abs(percent).toFixed(2);
    return percent >= 0 ? `+${formatted}%` : `-${formatted}%`;
  };

  if (loading) {
    return (
      <div className="live-market-indicators">
        <h3 className="market-title">Live Market</h3>
        <div className="market-grid">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="market-index-card skeleton">
              <div className="skeleton-name"></div>
              <div className="skeleton-value"></div>
              <div className="skeleton-change"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="live-market-indicators">
        <h3 className="market-title">Live Market</h3>
        <div className="market-error">
          <p>{error}</p>
          <button onClick={fetchMarketData} className="retry-btn">Retry</button>
        </div>
      </div>
    );
  }

  const currentSlideData = slides[currentSlide];
  const currentIndices = marketData[currentSlideData.key] || [];

  return (
    <div className="live-market-indicators">
      <div className="market-header">
        <h3 className="market-title">Live Market</h3>
        <div className="slide-dots">
          {slides.map((_, index) => (
            <span
              key={index}
              className={`dot ${index === currentSlide ? 'active' : ''}`}
              onClick={() => setCurrentSlide(index)}
            />
          ))}
        </div>
      </div>
      
      <div className="market-grid">
        {currentIndices.map((market, index) => {
          const isPositive = market.change >= 0;
          
          return (
            <div key={index} className="market-index-card">
              <div className="index-name">{market.name}</div>
              <div className="index-value">{formatValue(market.current_price)}</div>
              <div className={`index-change ${isPositive ? 'positive' : 'negative'}`}>
                <span className="change-icon">{isPositive ? '▲' : '▼'}</span>
                <span className="change-text">
                  {formatChange(market.change)} ({formatChangePercent(market.change_percent)})
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default LiveMarketIndicators;
