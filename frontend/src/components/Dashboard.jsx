import React, { useState, useRef, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import StockCarousel from './dashboard/StockCarousel';
import StockMarquee from './dashboard/StockMarquee';
import StockSearch from './dashboard/StockSearch';
import LiveMarketsCarousel from './dashboard/LiveMarketsCarousel';
import CorporateAnnouncements from './dashboard/CorporateAnnouncements';
import ChatInterface from './chat/ChatInterface';
import Profile from '../pages/Profile';
import PortfolioDashboard from '../pages/PortfolioDashboard';
import UnifiedHeader from './common/UnifiedHeader';
import './Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const chatCallbacksRef = useRef({ toggleSidebar: null, newChat: null, hasMessages: false });
  const [, forceUpdate] = useState({});

  const handleNavigation = (path) => {
    navigate(path);
  };

  const registerChatCallbacks = useCallback((toggleSidebar, newChat, hasMessages) => {
    chatCallbacksRef.current = { toggleSidebar, newChat, hasMessages };
    forceUpdate({});
  }, []);

  return (
    <div className="dashboard-layout">
      {/* Unified Header for All Pages */}
      <UnifiedHeader 
        showSidebarToggle={location.pathname === '/dashboard/chat'}
        onSidebarToggle={chatCallbacksRef.current.toggleSidebar}
        showNewChatButton={location.pathname === '/dashboard/chat'}
        onNewChat={chatCallbacksRef.current.newChat}
        hasMessages={chatCallbacksRef.current.hasMessages}
      />
      
      {/* Main Content Area */}
      <main className="main-content">
        {location.pathname === '/dashboard/chat' ? (
          <div className="chat-page">
            <ChatInterface
              endpoint="/api/chat/"
              placeholder="Ask me anything about stocks, investments, portfolio, or financial planning..."
              quickActions={[
                "Analyze RELIANCE stock performance",
                "Explain mutual funds for beginners",
                "Review my portfolio risk allocation",
                "What are today's top market movers?",
                "Suggest diversification strategy",
                "How to start investing with ₹10,000?",
                "Calculate tax on my stock gains",
                "Compare SIP vs Lump sum investment"
              ]}
              registerCallbacks={registerChatCallbacks}
            />
          </div>
        ) : (
          <div className="page-wrapper">
          <div className="content-container">
            {location.pathname === '/dashboard' && (
              <div className="home-content">
                {/* Market Data Components - Only on Home Page */}
                <StockSearch />
                <StockMarquee />
                <LiveMarketsCarousel />

                {/* Corporate Announcements - Live BSE Updates */}
                <CorporateAnnouncements />

                {/* Stock Carousel */}
                <StockCarousel onAddToWatchlist={(stock, isAdding) => {
                  // Watchlist update handled by StockCarousel component
                }} />

                <div className="features-grid">
                  <div className="feature-card" onClick={() => handleNavigation('/dashboard/chat')} style={{ cursor: 'pointer' }}>
                    <h3>💬 FinMentor Chat</h3>
                    <p>AI-powered financial assistant for advice, analysis, and portfolio building</p>
                  </div>
                  <div className="feature-card" onClick={() => handleNavigation('/dashboard/portfolio')} style={{ cursor: 'pointer' }}>
                    <h3>📊 My Portfolio</h3>
                    <p>Track and visualize your investment portfolio performance</p>
                  </div>
                </div>
              </div>
            )}

            {location.pathname === '/dashboard/profile' && (
              <Profile />
            )}

            {location.pathname === '/dashboard/contact' && (
              <div className="page-content">
                <h1>Contact Us</h1>
                <p>Get in touch with our support team</p>
              </div>
            )}

            {location.pathname === '/dashboard/portfolio' && (
              <PortfolioDashboard />
            )}
          </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
