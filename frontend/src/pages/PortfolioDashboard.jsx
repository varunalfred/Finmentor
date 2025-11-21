import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './PortfolioDashboard.css';

const PortfolioDashboard = () => {
  const navigate = useNavigate();
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPortfolioData();
  }, []);

  const fetchPortfolioData = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      // const response = await fetch('/api/portfolio');
      // const data = await response.json();
      
      // Mock data for now
      const mockData = {
        totalValue: 125000,
        totalInvested: 100000,
        returns: 25000,
        returnsPercent: 25.0,
        riskScore: 'Medium',
        holdings: [
          { symbol: 'TCS', name: 'Tata Consultancy Services', quantity: 50, avgPrice: 3200, currentPrice: 3500, value: 175000, change: 9.38 },
          { symbol: 'INFY', name: 'Infosys', quantity: 100, avgPrice: 1400, currentPrice: 1550, value: 155000, change: 10.71 },
          { symbol: 'HDFC', name: 'HDFC Bank', quantity: 80, avgPrice: 1600, currentPrice: 1580, value: 126400, change: -1.25 },
          { symbol: 'RELIANCE', name: 'Reliance Industries', quantity: 40, avgPrice: 2400, currentPrice: 2650, value: 106000, change: 10.42 }
        ],
        allocation: {
          equity: 70,
          debt: 20,
          gold: 10
        }
      };
      
      setPortfolio(mockData);
      setLoading(false);
    } catch (err) {
      setError('Failed to load portfolio data');
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="portfolio-loading">
        <div className="spinner"></div>
        <p>Loading portfolio...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="portfolio-error">
        <p>{error}</p>
        <button onClick={fetchPortfolioData}>Retry</button>
      </div>
    );
  }

  return (
    <div className="portfolio-dashboard">
      <div className="portfolio-header">
        <h1>My Portfolio</h1>
        <button className="refresh-btn" onClick={fetchPortfolioData}>
          🔄 Refresh
        </button>
      </div>

      {/* Summary Cards */}
      <div className="portfolio-summary">
        <div className="summary-card">
          <div className="card-icon">💰</div>
          <div className="card-content">
            <p className="card-label">Total Value</p>
            <h3 className="card-value">{formatCurrency(portfolio?.totalValue || 0)}</h3>
          </div>
        </div>

        <div className="summary-card positive">
          <div className="card-icon">📈</div>
          <div className="card-content">
            <p className="card-label">Total Returns</p>
            <h3 className="card-value">
              {formatCurrency(portfolio?.returns || 0)}
              <span className="percent">+{portfolio?.returnsPercent}%</span>
            </h3>
          </div>
        </div>

        <div className="summary-card">
          <div className="card-icon">💵</div>
          <div className="card-content">
            <p className="card-label">Invested Amount</p>
            <h3 className="card-value">{formatCurrency(portfolio?.totalInvested || 0)}</h3>
          </div>
        </div>

        <div className="summary-card">
          <div className="card-icon">⚠️</div>
          <div className="card-content">
            <p className="card-label">Risk Level</p>
            <h3 className="card-value risk-badge">{portfolio?.riskScore || 'N/A'}</h3>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="portfolio-grid">
        {/* Holdings Table */}
        <div className="portfolio-card holdings-card">
          <h2>Holdings</h2>
          <div className="holdings-table">
            <table>
              <thead>
                <tr>
                  <th>Stock</th>
                  <th>Quantity</th>
                  <th>Avg Price</th>
                  <th>Current Price</th>
                  <th>Value</th>
                  <th>Change %</th>
                </tr>
              </thead>
              <tbody>
                {portfolio?.holdings.map((holding) => (
                  <tr key={holding.symbol}>
                    <td>
                      <div className="stock-cell">
                        <strong>{holding.symbol}</strong>
                        <span className="stock-name">{holding.name}</span>
                      </div>
                    </td>
                    <td>{holding.quantity}</td>
                    <td>{formatCurrency(holding.avgPrice)}</td>
                    <td>{formatCurrency(holding.currentPrice)}</td>
                    <td><strong>{formatCurrency(holding.value)}</strong></td>
                    <td>
                      <span className={`change-badge ${holding.change >= 0 ? 'positive' : 'negative'}`}>
                        {holding.change >= 0 ? '▲' : '▼'} {Math.abs(holding.change).toFixed(2)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Asset Allocation */}
        <div className="portfolio-card allocation-card">
          <h2>Asset Allocation</h2>
          <div className="allocation-chart">
            <div className="allocation-item">
              <div className="allocation-bar">
                <div 
                  className="allocation-fill equity" 
                  style={{ width: `${portfolio?.allocation.equity}%` }}
                ></div>
              </div>
              <div className="allocation-label">
                <span>📊 Equity</span>
                <strong>{portfolio?.allocation.equity}%</strong>
              </div>
            </div>
            
            <div className="allocation-item">
              <div className="allocation-bar">
                <div 
                  className="allocation-fill debt" 
                  style={{ width: `${portfolio?.allocation.debt}%` }}
                ></div>
              </div>
              <div className="allocation-label">
                <span>🏦 Debt</span>
                <strong>{portfolio?.allocation.debt}%</strong>
              </div>
            </div>
            
            <div className="allocation-item">
              <div className="allocation-bar">
                <div 
                  className="allocation-fill gold" 
                  style={{ width: `${portfolio?.allocation.gold}%` }}
                ></div>
              </div>
              <div className="allocation-label">
                <span>💛 Gold</span>
                <strong>{portfolio?.allocation.gold}%</strong>
              </div>
            </div>
          </div>
        </div>

        {/* AI Recommendations */}
        <div className="portfolio-card recommendations-card">
          <h2>AI Recommendations</h2>
          <div className="recommendations-list">
            <div className="recommendation-item">
              <div className="rec-icon">💡</div>
              <div className="rec-content">
                <h4>Rebalance Portfolio</h4>
                <p>Your equity allocation is higher than recommended. Consider moving some funds to debt instruments.</p>
              </div>
            </div>
            
            <div className="recommendation-item">
              <div className="rec-icon">📉</div>
              <div className="rec-content">
                <h4>Review HDFC Position</h4>
                <p>HDFC is down 1.25%. Consider averaging down or evaluating your position.</p>
              </div>
            </div>
            
            <div className="recommendation-item">
              <div className="rec-icon">🎯</div>
              <div className="rec-content">
                <h4>Diversification Suggestion</h4>
                <p>Consider adding mid-cap stocks to improve diversification and potential returns.</p>
              </div>
            </div>
          </div>
          
          <button 
            className="ask-finmentor-btn"
            onClick={() => navigate('/dashboard/chat')}
          >
            💬 Ask FinMentor AI for Details
          </button>
        </div>
      </div>
    </div>
  );
};

export default PortfolioDashboard;
