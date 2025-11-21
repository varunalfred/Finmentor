import React, { useState, useEffect, useRef } from 'react';
import './StockSearch.css';

const StockSearch = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const searchRef = useRef(null);
  const debounceTimer = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Search function with debounce
  const performSearch = async (searchQuery) => {
    if (!searchQuery.trim()) {
      setResults([]);
      setShowDropdown(false);
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`/api/market/search?query=${encodeURIComponent(searchQuery)}`);
      
      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      setResults(data.results || []);
      setShowDropdown(true);
      setSelectedIndex(-1);
    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  // Handle input change with debounce
  const handleInputChange = (e) => {
    const value = e.target.value;
    setQuery(value);

    // Clear previous timer
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }

    // Set new timer
    debounceTimer.current = setTimeout(() => {
      performSearch(value);
    }, 300); // 300ms debounce
  };

  // Handle keyboard navigation
  const handleKeyDown = (e) => {
    if (!showDropdown || results.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex((prev) => 
          prev < results.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex((prev) => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0) {
          handleResultClick(results[selectedIndex]);
        }
        break;
      case 'Escape':
        setShowDropdown(false);
        setSelectedIndex(-1);
        break;
      default:
        break;
    }
  };

  // Handle result click
  const handleResultClick = (result) => {
    console.log('Selected:', result);
    // TODO: Navigate to stock detail page or open modal
    setQuery(result.symbol);
    setShowDropdown(false);
    setSelectedIndex(-1);
    
    // You can emit an event or callback here
    // For now, just logging
  };

  // Clear search
  const handleClear = () => {
    setQuery('');
    setResults([]);
    setShowDropdown(false);
    setSelectedIndex(-1);
  };

  // Format change for display
  const formatChange = (change) => {
    if (change === null || change === undefined) return '0.00';
    const formatted = Math.abs(change).toFixed(2);
    return change >= 0 ? `+${formatted}` : `-${formatted}`;
  };

  const formatChangePercent = (percent) => {
    if (percent === null || percent === undefined) return '0.00%';
    const formatted = Math.abs(percent).toFixed(2);
    return percent >= 0 ? `+${formatted}%` : `-${formatted}%`;
  };

  return (
    <div className="stock-search-container" ref={searchRef}>
      <div className="search-input-wrapper">
        <span className="search-icon">🔍</span>
        <input
          type="text"
          className="search-input"
          placeholder="Search stocks, indices, commodities..."
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => {
            if (results.length > 0) setShowDropdown(true);
          }}
        />
        {query && (
          <button className="clear-button" onClick={handleClear} aria-label="Clear search">
            ✕
          </button>
        )}
        {loading && (
          <div className="loading-spinner">
            <div className="spinner"></div>
          </div>
        )}
      </div>

      {showDropdown && (
        <div className="search-dropdown">
          {results.length > 0 ? (
            <ul className="results-list">
              {results.map((result, index) => {
                const isPositive = result.change_percent >= 0;
                const isSelected = index === selectedIndex;
                
                return (
                  <li
                    key={`${result.symbol}-${index}`}
                    className={`result-item ${isSelected ? 'selected' : ''}`}
                    onClick={() => handleResultClick(result)}
                    onMouseEnter={() => setSelectedIndex(index)}
                  >
                    <div className="result-left">
                      <div className="result-icon">
                        {result.type === 'commodity' ? '💎' : 
                         result.type === 'index' ? '📊' : '📈'}
                      </div>
                      <div className="result-info">
                        <div className="result-name">{result.name}</div>
                        <div className="result-meta">
                          <span className="result-symbol">{result.symbol}</span>
                          {result.exchange && (
                            <>
                              <span className="separator">•</span>
                              <span className="result-exchange">{result.exchange}</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="result-right">
                      <div className="result-price">
                        ₹{result.current_price?.toLocaleString('en-IN', {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2
                        }) || '0.00'}
                      </div>
                      <div className={`result-change ${isPositive ? 'positive' : 'negative'}`}>
                        <span className="change-icon">
                          {isPositive ? '▲' : '▼'}
                        </span>
                        {formatChange(result.change)} ({formatChangePercent(result.change_percent)})
                      </div>
                    </div>
                  </li>
                );
              })}
            </ul>
          ) : (
            <div className="no-results">
              <span className="no-results-icon">🔍</span>
              <p>No results found for "{query}"</p>
              <span className="no-results-hint">Try searching with ticker symbols or company names</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default StockSearch;
