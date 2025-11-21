import React, { useState, useEffect } from 'react';
import './ActivitySection.css';

const ActivitySection = () => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [filter, setFilter] = useState('all');
  const [dataFetched, setDataFetched] = useState(false);

  const activityTypes = {
    watchlist_add: { icon: '📌', label: 'Added to Watchlist', color: '#48bb78' },
    watchlist_remove: { icon: '🗑️', label: 'Removed from Watchlist', color: '#f56565' },
    search: { icon: '🔍', label: 'Search', color: '#8FABD4' },
    chat: { icon: '💬', label: 'Chat', color: '#667eea' },
    login: { icon: '🔐', label: 'Login', color: '#48bb78' },
    settings_change: { icon: '⚙️', label: 'Settings Changed', color: '#ed8936' },
    profile_update: { icon: '👤', label: 'Profile Updated', color: '#9f7aea' },
    password_change: { icon: '🔑', label: 'Password Changed', color: '#f56565' }
  };

  useEffect(() => {
    // Only fetch when component first mounts or filter/page changes
    if (!dataFetched || page !== 1 || filter !== 'all') {
      fetchActivities();
      setDataFetched(true);
    }
  }, [page, filter]);

  const fetchActivities = async () => {
    try {
      const token = localStorage.getItem('token');
      let url = `http://localhost:8000/api/profile/activity?page=${page}&page_size=20`;
      if (filter !== 'all') {
        url += `&activity_type=${filter}`;
      }

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setActivities(data.activities);
        setTotal(data.total);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching activities:', error);
      setLoading(false);
    }
  };

  const handleClearHistory = async () => {
    if (!confirm('Clear all activity history? This cannot be undone.')) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/profile/activity', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setActivities([]);
        setTotal(0);
      }
    } catch (error) {
      console.error('Error clearing history:', error);
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  if (loading) {
    return <div className="activity-loading"><div className="spinner"></div></div>;
  }

  return (
    <div className="activity-section">
      <div className="activity-header">
        <h2>Activity History</h2>
        <div className="activity-actions">
          <select
            className="filter-select"
            value={filter}
            onChange={(e) => { setFilter(e.target.value); setPage(1); }}
          >
            <option value="all">All Activities</option>
            <option value="watchlist_add">Watchlist Additions</option>
            <option value="watchlist_remove">Watchlist Removals</option>
            <option value="search">Searches</option>
            <option value="chat">Chat History</option>
            <option value="login">Login History</option>
            <option value="settings_change">Settings Changes</option>
          </select>
          
          <button className="clear-btn" onClick={handleClearHistory}>
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Clear History
          </button>
        </div>
      </div>

      {activities.length === 0 ? (
        <div className="empty-activities">
          <svg className="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3>No Activity Yet</h3>
          <p>Your activities will appear here</p>
        </div>
      ) : (
        <>
          <div className="activity-timeline">
            {activities.map(activity => {
              const type = activityTypes[activity.activity_type] || activityTypes.search;
              return (
                <div key={activity.id} className="activity-item">
                  <div
                    className="activity-icon"
                    style={{ backgroundColor: type.color }}
                  >
                    {type.icon}
                  </div>
                  <div className="activity-content">
                    <div className="activity-header-item">
                      <span className="activity-label">{type.label}</span>
                      <span className="activity-time">{formatTimestamp(activity.created_at)}</span>
                    </div>
                    <p className="activity-description">{activity.description}</p>
                    {activity.metadata && Object.keys(activity.metadata).length > 0 && (
                      <div className="activity-metadata">
                        {Object.entries(activity.metadata).map(([key, value]) => (
                          <span key={key} className="metadata-tag">
                            {key}: {typeof value === 'object' ? JSON.stringify(value) : value}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Pagination */}
          {total > 20 && (
            <div className="pagination">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="page-btn"
              >
                Previous
              </button>
              <span className="page-info">
                Page {page} of {Math.ceil(total / 20)}
              </span>
              <button
                onClick={() => setPage(p => p + 1)}
                disabled={page >= Math.ceil(total / 20)}
                className="page-btn"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ActivitySection;
