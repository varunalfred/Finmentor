import React, { useState } from 'react';
import { addToWatchlist, removeFromWatchlist } from '../../services/watchlistService';
import { useStockData } from '../../hooks/useApi';
import './StockCarousel.css';

const StockCarousel = ({ onAddToWatchlist }) => {
  const [activeTab, setActiveTab] = useState('gainers');
  const [marketCap, setMarketCap] = useState('large');
  const [showCapDropdown, setShowCapDropdown] = useState(false);
  const [watchlist, setWatchlist] = useState(new Set());
  const [toast, setToast] = useState({ show: false, message: '', type: '' });

  // ✅ Use React Query hook - automatic caching and refetching
  const { data, isLoading: loading, error: fetchError } = useStockData(activeTab, marketCap);
  const stocks = data?.stocks || [];
  const error = fetchError ? 'Failed to load stock data. Please try again.' : null;

  const tabs = [
    { id: 'gainers', label: 'Gainers' },
    { id: 'losers', label: 'Losers' },
    { id: 'most_active', label: 'Most Active' },
    { id: '52w_high', label: '52W High' },
    { id: '52w_low', label: '52W Low' }
  ];

  const marketCapOptions = [
    { value: 'large', label: 'Large Cap' },
    { value: 'mid', label: 'Mid Cap' },
    { value: 'small', label: 'Small Cap' }
  ];

  // ✅ No useEffect or fetchStocks needed - React Query handles it

  const handleTabChange = (tabId) => {
    setActiveTab(tabId);
  };

  const handleMarketCapChange = (value) => {
    setMarketCap(value);
    setShowCapDropdown(false);
  };

  const handleBookmark = async (stock) => {
    const isInWatchlist = watchlist.has(stock.symbol);

    try {
      if (isInWatchlist) {
        // Remove from watchlist
        await removeFromWatchlist(stock.symbol);
        const newWatchlist = new Set(watchlist);
        newWatchlist.delete(stock.symbol);
        setWatchlist(newWatchlist);

        showToast('Removed from watchlist', 'success');
      } else {
        // Add to watchlist
        await addToWatchlist(stock.symbol, stock.company_name);
        const newWatchlist = new Set(watchlist);
        newWatchlist.add(stock.symbol);
        setWatchlist(newWatchlist);

        showToast('Added to watchlist', 'success');
      }

      if (onAddToWatchlist) {
        onAddToWatchlist(stock, !isInWatchlist);
      }
    } catch (err) {
      console.error('Watchlist error:', err);
      if (err.response?.status === 401) {
        showToast('Please login to use watchlist', 'error');
      } else {
        showToast('Failed to update watchlist', 'error');
      }
    }
  };

  const showToast = (message, type) => {
    setToast({ show: true, message, type });
    setTimeout(() => {
      setToast({ show: false, message: '', type: '' });
    }, 3000);
  };

  const formatPrice = (price) => {
    return `₹${price.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const formatMarketCap = (marketCap) => {
    if (marketCap >= 1e12) {
      return `₹${(marketCap / 1e12).toFixed(2)}T`;
    } else if (marketCap >= 1e9) {
      return `₹${(marketCap / 1e9).toFixed(2)}B`;
    } else if (marketCap >= 1e7) {
      return `₹${(marketCap / 1e7).toFixed(2)}Cr`;
    }
    return `₹${marketCap.toLocaleString('en-IN')}`;
  };

  const getChangeClass = (change) => {
    if (change > 0) return 'positive';
    if (change < 0) return 'negative';
    return 'neutral';
  };

  return (
    <div className="stock-carousel-container">
      {/* Toast Notification */}
      {toast.show && (
        <div className={`toast ${toast.type}`}>
          {toast.message}
        </div>
      )}

      {/* Header */}
      <div className="carousel-title-row">
        <h2 className="carousel-title">Today's stocks</h2>

        <div className="market-cap-filter">
          <button
            className="cap-dropdown-toggle"
            onClick={() => setShowCapDropdown(!showCapDropdown)}
          >
            {marketCapOptions.find(opt => opt.value === marketCap)?.label || 'Large Cap'} ↓
          </button>

          {showCapDropdown && (
            <div className="cap-dropdown-menu">
              {marketCapOptions.map((option) => (
                <button
                  key={option.value}
                  className={`cap-option ${marketCap === option.value ? 'active' : ''}`}
                  onClick={() => handleMarketCapChange(option.value)}
                >
                  {option.label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="carousel-tabs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => handleTabChange(tab.id)}
          >
            <span className="tab-icon">
              {tab.id === 'gainers' && '📈'}
              {tab.id === 'losers' && '📉'}
              {tab.id === 'most_active' && '🔥'}
              {tab.id === '52w_high' && '📊'}
              {tab.id === '52w_low' && '📉'}
            </span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Stock Table */}
      <div className="stocks-container">
        {loading ? (
          <div className="loading-state">
            {[...Array(8)].map((_, index) => (
              <div key={index} className="stock-row skeleton">
                <div className="skeleton-content"></div>
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="error-state">
            <p>{error}</p>
            <button onClick={fetchStocks} className="retry-button">
              Retry
            </button>
          </div>
        ) : stocks.length === 0 ? (
          <div className="empty-state">
            <p>No stocks found for this category</p>
          </div>
        ) : (
          <>
            {/* Table Header */}
            <div className="table-header">
              <div className="header-col stocks-col">STOCKS</div>
              <div className="header-col price-col">PRICE</div>
              <div className="header-col change-col">CHANGE</div>
            </div>

            {/* Stock Rows */}
            <div className="stock-list">
              {stocks.map((stock) => (
                <div key={stock.symbol} className="stock-row">
                  <div className="stock-info-col">
                    <div className="stock-logo">
                      {stock.logo_url ? (
                        <img src={stock.logo_url} alt={stock.company_name} />
                      ) : (
                        <div className="logo-placeholder">
                          {stock.company_name.substring(0, 2).toUpperCase()}
                        </div>
                      )}
                    </div>
                    <div className="stock-details">
                      <div className="company-name">{stock.company_name}</div>
                      <div className="stock-symbol">{stock.symbol.replace('.NS', '')}</div>
                    </div>
                  </div>

                  <div className="stock-price-col">
                    <div className="current-price">{formatPrice(stock.current_price)}</div>
                  </div>

                  <div className="stock-change-col">
                    <div className={`change-badge ${getChangeClass(stock.change)}`}>
                      <span className="change-icon">
                        {stock.change >= 0 ? '▲' : '▼'}
                      </span>
                      {Math.abs(stock.change_percent).toFixed(2)}%
                    </div>
                    <button
                      className={`bookmark-icon ${watchlist.has(stock.symbol) ? 'bookmarked' : ''}`}
                      onClick={() => handleBookmark(stock)}
                      title={watchlist.has(stock.symbol) ? 'Remove from watchlist' : 'Add to watchlist'}
                    >
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
                      </svg>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default StockCarousel;
