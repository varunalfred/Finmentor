import React, { useState, useEffect } from 'react';
import './WatchlistSection.css';

const WatchlistSection = () => {
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('date'); // date, name, price, change
  const [sortOrder, setSortOrder] = useState('desc');
  const [stats, setStats] = useState(null);
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    // Only fetch if component is visible
    if (isVisible) {
      fetchWatchlist();
      fetchStats();
    }
    
    // Auto-refresh every 30 seconds, but only when tab is active
    const interval = setInterval(() => {
      if (document.visibilityState === 'visible' && isVisible) {
        fetchWatchlist();
        fetchStats();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [isVisible]);

  const fetchWatchlist = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/watchlist', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setWatchlist(data);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching watchlist:', error);
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/watchlist/stats', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleRemove = async (symbol) => {
    if (!confirm(`Remove ${symbol} from watchlist?`)) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/watchlist/${symbol}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setWatchlist(watchlist.filter(item => item.symbol !== symbol));
        fetchStats();
      }
    } catch (error) {
      console.error('Error removing from watchlist:', error);
    }
  };

  const handleExport = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/watchlist/export', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        const blob = new Blob([data.content], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = data.filename;
        a.click();
      }
    } catch (error) {
      console.error('Error exporting watchlist:', error);
    }
  };

  const sortedWatchlist = [...watchlist]
    .filter(item => 
      item.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.company_name?.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      let compareValue = 0;
      
      switch (sortBy) {
        case 'name':
          compareValue = (a.company_name || a.symbol).localeCompare(b.company_name || b.symbol);
          break;
        case 'price':
          compareValue = (a.current_price || 0) - (b.current_price || 0);
          break;
        case 'change':
          compareValue = (a.change_percent || 0) - (b.change_percent || 0);
          break;
        case 'date':
        default:
          compareValue = new Date(a.created_at) - new Date(b.created_at);
      }
      
      return sortOrder === 'asc' ? compareValue : -compareValue;
    });

  if (loading) {
    return (
      <div className="watchlist-loading">
        <div className="spinner"></div>
        <p>Loading watchlist...</p>
      </div>
    );
  }

  return (
    <div className="watchlist-section">
      {/* Stats Cards */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon stocks-icon">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
              </svg>
            </div>
            <div className="stat-content">
              <p className="stat-label">Total Stocks</p>
              <p className="stat-value">{stats.total_stocks}</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon value-icon">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="stat-content">
              <p className="stat-label">Portfolio Value</p>
              <p className="stat-value">₹{stats.portfolio_value.toLocaleString()}</p>
            </div>
          </div>

          <div className="stat-card">
            <div className={`stat-icon ${stats.total_gain >= 0 ? 'gain-icon' : 'loss-icon'}`}>
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <div className="stat-content">
              <p className="stat-label">Total Gain/Loss</p>
              <p className={`stat-value ${stats.total_gain >= 0 ? 'gain' : 'loss'}`}>
                ₹{Math.abs(stats.total_gain).toLocaleString()} ({stats.total_gain_percent.toFixed(2)}%)
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="watchlist-controls">
        <div className="search-box">
          <svg className="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Search stocks..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="sort-controls">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="sort-select"
          >
            <option value="date">Date Added</option>
            <option value="name">Name</option>
            <option value="price">Price</option>
            <option value="change">Change %</option>
          </select>

          <button
            className="sort-order-btn"
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
          >
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {sortOrder === 'asc' ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              )}
            </svg>
          </button>

          <button className="export-btn" onClick={handleExport}>
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export
          </button>
        </div>
      </div>

      {/* Watchlist Items */}
      {sortedWatchlist.length === 0 ? (
        <div className="empty-state">
          <svg className="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
          </svg>
          <h3>No stocks in watchlist</h3>
          <p>Start adding stocks from the dashboard!</p>
        </div>
      ) : (
        <div className="watchlist-grid">
          {sortedWatchlist.map(item => (
            <div key={item.id} className="watchlist-card">
              <div className="card-header">
                <div>
                  <h3 className="stock-symbol">{item.symbol}</h3>
                  <p className="company-name">{item.company_name}</p>
                </div>
                <button
                  className="remove-btn"
                  onClick={() => handleRemove(item.symbol)}
                  title="Remove from watchlist"
                >
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>

              <div className="card-body">
                <div className="price-info">
                  <div>
                    <p className="label">Current Price</p>
                    <p className="current-price">
                      ₹{item.current_price ? item.current_price.toFixed(2) : 'N/A'}
                    </p>
                  </div>

                  {item.change !== null && (
                    <div className={`change-badge ${item.change >= 0 ? 'positive' : 'negative'}`}>
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                              d={item.change >= 0 ? "M5 10l7-7m0 0l7 7m-7-7v18" : "M19 14l-7 7m0 0l-7-7m7 7V3"} />
                      </svg>
                      <span>{item.change >= 0 ? '+' : ''}{item.change.toFixed(2)}</span>
                      <span>({item.change_percent >= 0 ? '+' : ''}{item.change_percent.toFixed(2)}%)</span>
                    </div>
                  )}
                </div>

                {item.added_price && (
                  <div className="added-info">
                    <p className="label">Added at ₹{item.added_price.toFixed(2)}</p>
                    <p className="added-date">{new Date(item.created_at).toLocaleDateString()}</p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default WatchlistSection;
