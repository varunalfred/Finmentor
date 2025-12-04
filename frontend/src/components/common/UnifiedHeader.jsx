import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTheme } from '../../contexts/ThemeContext';
import { useAuth } from '../../contexts/AuthContext';
import './UnifiedHeader.css';

const UnifiedHeader = ({
  showSidebarToggle = false,
  onSidebarToggle,
  showNewChatButton = false,
  onNewChat,
  hasMessages = false
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { toggleTheme, isDark } = useTheme();
  const { logout } = useAuth();

  const menuItems = [
    { id: 'home', label: 'Home', path: '/dashboard' },
    { id: 'profile', label: 'Profile', path: '/dashboard/profile' },
    { id: 'chat', label: 'FinMentor Chat', path: '/dashboard/chat' },
    { id: 'community', label: '🌍 Community', path: '/dashboard/community' },
    { id: 'portfolio', label: 'My Portfolio', path: '/dashboard/portfolio' },
    { id: 'contact', label: 'Contact Us', path: '/dashboard/contact' }
  ];

  const handleNavigation = (path) => {
    console.log('Navigating to:', path);
    navigate(path);
  };

  const handleLogout = () => {
    logout();
  };

  const getPageTitle = () => {
    const currentItem = menuItems.find(item => item.path === location.pathname);
    return currentItem ? currentItem.label : 'FinMentor AI';
  };

  return (
    <header className="unified-header">
      <div className="header-left">
        {showSidebarToggle && (
          <button
            className="sidebar-toggle-btn"
            onClick={onSidebarToggle}
            aria-label="Toggle sidebar"
            title="Conversation History"
          >
            ☰
          </button>
        )}
        <div className="header-brand">
          <h2>{getPageTitle()}</h2>
        </div>
      </div>

      <nav className="header-nav">
        {menuItems.map((item) => (
          <button
            key={item.id}
            className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
            onClick={() => handleNavigation(item.path)}
          >
            {item.label}
          </button>
        ))}
      </nav>

      <div className="header-actions">
        {showNewChatButton && hasMessages && (
          <button
            className="new-conversation-btn"
            onClick={onNewChat}
            title="Start a new conversation"
          >
            + New Chat
          </button>
        )}
        <button
          className="theme-toggle-btn"
          onClick={toggleTheme}
          aria-label="Toggle theme"
        >
          {isDark ? '☀️' : '🌙'}
        </button>
        <button
          className="logout-btn"
          onClick={handleLogout}
        >
          Logout
        </button>
      </div>
    </header>
  );
};

export default UnifiedHeader;
