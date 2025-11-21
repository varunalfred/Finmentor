import React, { useState, useEffect, useRef } from 'react';
import { getMarketIndices, formatIndianNumber, getChangeColor, formatTime } from '../../services/marketService';
import './MarketTicker.css';

const MarketTicker = () => {
  const [indices, setIndices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [currentSlide, setCurrentSlide] = useState(0);
  const intervalRef = useRef(null);

  // Group indices into slides (all indices in one vertical column)
  const indicesPerSlide = 6; // Show 6 indices per slide
  const slides = [];
  for (let i = 0; i < indices.length; i += indicesPerSlide) {
    slides.push(indices.slice(i, i + indicesPerSlide));
  }

  // Fetch market data
  const fetchMarketData = async () => {
    try {
      const result = await getMarketIndices();
      
      if (result.success) {
        setIndices(result.data.indices);
        setLastUpdated(result.data.last_updated);
        setError(null);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Failed to fetch market data');
      console.error('Market data fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchMarketData();
  }, []);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const refreshInterval = setInterval(() => {
      fetchMarketData();
    }, 30000);

    return () => clearInterval(refreshInterval);
  }, []);

  // Auto-rotate carousel every 5 seconds
  useEffect(() => {
    if (slides.length > 1) {
      intervalRef.current = setInterval(() => {
        setCurrentSlide((prev) => (prev + 1) % slides.length);
      }, 5000);

      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      };
    }
  }, [slides.length]);

  const handleDotClick = (index) => {
    setCurrentSlide(index);
  };

  // Loading skeleton
  if (loading) {
    return (
      <div className="market-ticker-carousel">
        <div className="ticker-header">
          <h3>📊 Market Indices</h3>
          <span className="loading-text">Loading...</span>
        </div>
        <div className="ticker-carousel-container">
          <div className="ticker-vertical-grid">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="ticker-index-card skeleton">
                <div className="skeleton-name"></div>
                <div className="skeleton-price"></div>
                <div className="skeleton-change"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error && indices.length === 0) {
    return (
      <div className="market-ticker-carousel">
        <div className="ticker-header">
          <h3>📊 Market Indices</h3>
        </div>
        <div className="ticker-error">
          <p>{error}</p>
          <button onClick={fetchMarketData} className="retry-btn">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="market-ticker-carousel">
      <div className="ticker-header">
        <h3>� Market Indices</h3>
        <div className="ticker-controls">
          {lastUpdated && (
            <span className="last-updated">
              Updated: {formatTime(lastUpdated)}
            </span>
          )}
        </div>
      </div>

      <div className="ticker-carousel-container">
        <div className="ticker-slides-wrapper">
          <div 
            className="ticker-slides"
            style={{ transform: `translateX(-${currentSlide * 100}%)` }}
          >
            {slides.map((slideIndices, slideIndex) => (
              <div key={slideIndex} className="ticker-slide">
                <div className="ticker-vertical-grid">
                  {slideIndices.map((index) => (
                    <div 
                      key={index.symbol} 
                      className={`ticker-index-card ${getChangeColor(index.change)}`}
                    >
                      <div className="index-info">
                        <div className="index-name-section">
                          <span className="index-symbol">{index.name}</span>
                          {!index.is_market_open && (
                            <span className="market-closed" title="Market Closed">CLOSED</span>
                          )}
                        </div>
                        <div className="index-price">
                          ₹{formatIndianNumber(index.current_price)}
                        </div>
                      </div>
                      
                      <div className="index-change-section">
                        <div className={`change-badge ${getChangeColor(index.change)}`}>
                          <span className="change-icon">
                            {index.change >= 0 ? '▲' : '▼'}
                          </span>
                          <span className="change-value">
                            {index.change >= 0 ? '+' : ''}{formatIndianNumber(index.change)}
                          </span>
                          <span className="change-percent">
                            ({index.change_percent >= 0 ? '+' : ''}{index.change_percent.toFixed(2)}%)
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {slides.length > 1 && (
          <div className="carousel-dots">
            {slides.map((_, index) => (
              <button
                key={index}
                className={`dot ${index === currentSlide ? 'active' : ''}`}
                onClick={() => handleDotClick(index)}
                aria-label={`Go to slide ${index + 1}`}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MarketTicker;
