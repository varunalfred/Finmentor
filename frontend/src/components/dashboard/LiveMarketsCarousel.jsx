import React, { useState, useEffect, useRef } from 'react';
import './LiveMarketsCarousel.css';

const LiveMarketsCarousel = () => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [marketData, setMarketData] = useState({
    indian_markets: [],
    global_markets: [],
    commodities: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isPaused, setIsPaused] = useState(false);
  const intervalRef = useRef(null);
  const dataRefreshRef = useRef(null);

  const slides = [
    { key: 'indian_markets', title: 'Indian Markets', data: marketData.indian_markets },
    { key: 'global_markets', title: 'Global Markets', data: marketData.global_markets },
    { key: 'commodities', title: 'Commodities', data: marketData.commodities }
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
      setError('Unable to load market data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Initial data load
  useEffect(() => {
    fetchMarketData();
  }, []);

  // Auto-refresh data every 30 seconds
  useEffect(() => {
    dataRefreshRef.current = setInterval(() => {
      fetchMarketData();
    }, 30000);

    return () => {
      if (dataRefreshRef.current) {
        clearInterval(dataRefreshRef.current);
      }
    };
  }, []);

  // Auto-rotate carousel every 5 seconds
  useEffect(() => {
    if (!isPaused && !loading) {
      intervalRef.current = setInterval(() => {
        setCurrentSlide((prev) => (prev + 1) % slides.length);
      }, 5000);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isPaused, loading, slides.length]);

  const handleDotClick = (index) => {
    setCurrentSlide(index);
  };

  const handlePrevious = () => {
    setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length);
  };

  const handleNext = () => {
    setCurrentSlide((prev) => (prev + 1) % slides.length);
  };

  const formatValue = (value) => {
    if (value >= 1000) {
      return value.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
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

  const isMarketClosed = (lastUpdated) => {
    // Simple check - could be enhanced with actual market hours
    const now = new Date();
    const updateTime = new Date(lastUpdated);
    const diffMinutes = (now - updateTime) / (1000 * 60);
    return diffMinutes > 60; // Consider closed if no update in last hour
  };

  if (loading) {
    return (
      <div className="live-markets-carousel">
        <h2 className="carousel-title">Live Markets</h2>
        <div className="carousel-container">
          <div className="markets-grid">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="market-card skeleton">
                <div className="skeleton-title"></div>
                <div className="skeleton-value"></div>
                <div className="skeleton-change"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="live-markets-carousel">
        <h2 className="carousel-title">Live Markets</h2>
        <div className="carousel-container">
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            <p>{error}</p>
            <button onClick={fetchMarketData} className="retry-button">
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  const currentSlideData = slides[currentSlide];

  return (
    <div 
      className="live-markets-carousel"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      <div className="carousel-header">
        <h2 className="carousel-title">Live Markets</h2>
        <div className="carousel-controls">
          <button 
            onClick={handlePrevious} 
            className="nav-button"
            aria-label="Previous slide"
          >
            ‹
          </button>
          <button 
            onClick={handleNext} 
            className="nav-button"
            aria-label="Next slide"
          >
            ›
          </button>
        </div>
      </div>

      <div className="carousel-container">
        <div className="carousel-slides">
          <div 
            className="slide-wrapper"
            style={{ transform: `translateX(-${currentSlide * 100}%)` }}
          >
            {slides.map((slide, slideIndex) => (
              <div key={slide.key} className="carousel-slide">
                <h3 className="slide-title">{slide.title}</h3>
                <div className="markets-grid">
                  {slide.data.length > 0 ? (
                    slide.data.map((market, index) => {
                      const isPositive = market.change >= 0;
                      const isClosed = market.last_updated && isMarketClosed(market.last_updated);
                      
                      return (
                        <div key={index} className="market-card">
                          <div className="market-header">
                            <span className="market-name">{market.name}</span>
                            {isClosed && <span className="closed-badge">CLOSED</span>}
                          </div>
                          <div className="market-value">
                            {formatValue(market.current_price)}
                          </div>
                          <div className={`market-change ${isPositive ? 'positive' : 'negative'}`}>
                            <span className="change-icon">
                              {isPositive ? '▲' : '▼'}
                            </span>
                            <span className="change-value">
                              {formatChange(market.change)}
                            </span>
                            <span className="change-percent">
                              ({formatChangePercent(market.change_percent)})
                            </span>
                          </div>
                          {market.last_updated && (
                            <div className="last-updated">
                              Updated: {new Date(market.last_updated).toLocaleTimeString('en-IN', {
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </div>
                          )}
                        </div>
                      );
                    })
                  ) : (
                    <div className="no-data">No data available</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

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
      </div>
    </div>
  );
};

export default LiveMarketsCarousel;
