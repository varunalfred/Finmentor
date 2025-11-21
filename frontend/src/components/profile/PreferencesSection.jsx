import React, { useState, useEffect } from 'react';
import './PreferencesSection.css';

const PreferencesSection = () => {
  const [preferences, setPreferences] = useState({
    theme: 'light',
    email_notifications: true,
    price_alerts_enabled: true,
    watchlist_notifications: true,
    daily_digest: false,
    weekly_summary: true,
    auto_refresh_interval: 30,
    preferred_market_cap: 'all',
    default_currency: 'INR',
    price_change_threshold: 5.0
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    fetchPreferences();
  }, []);

  const fetchPreferences = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/profile/preferences', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setPreferences(data);
      }
    } catch (error) {
      console.error('Error fetching preferences:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setPreferences({
      ...preferences,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage({ type: '', text: '' });

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/profile/preferences', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(preferences)
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'Preferences saved successfully!' });
        setTimeout(() => setMessage({ type: '', text: '' }), 3000);
      } else {
        const error = await response.json();
        setMessage({ type: 'error', text: error.detail || 'Failed to save preferences' });
      }
    } catch (error) {
      console.error('Error saving preferences:', error);
      setMessage({ type: 'error', text: 'An error occurred while saving preferences' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="preferences-section loading">
        <div className="spinner"></div>
        <p>Loading preferences...</p>
      </div>
    );
  }

  return (
    <div className="preferences-section">
      {message.text && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSave}>
        <div className="pref-category">
          <h3>Appearance</h3>
          <div className="pref-item">
            <div className="pref-label">
              <label htmlFor="theme">Theme</label>
              <span className="pref-description">Choose your preferred color scheme</span>
            </div>
            <select
              id="theme"
              name="theme"
              value={preferences.theme}
              onChange={handleChange}
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="system">System Default</option>
            </select>
          </div>
        </div>

        <div className="pref-category">
          <h3>Notifications</h3>
          <div className="pref-item">
            <div className="pref-label">
              <label htmlFor="email_notifications">Email Notifications</label>
              <span className="pref-description">Receive important updates via email</span>
            </div>
            <label className="toggle-switch">
              <input
                type="checkbox"
                id="email_notifications"
                name="email_notifications"
                checked={preferences.email_notifications}
                onChange={handleChange}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>

          <div className="pref-item">
            <div className="pref-label">
              <label htmlFor="price_alerts_enabled">Price Alerts</label>
              <span className="pref-description">Get notified when prices change significantly</span>
            </div>
            <label className="toggle-switch">
              <input
                type="checkbox"
                id="price_alerts_enabled"
                name="price_alerts_enabled"
                checked={preferences.price_alerts_enabled}
                onChange={handleChange}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>

          <div className="pref-item">
            <div className="pref-label">
              <label htmlFor="watchlist_notifications">Watchlist Notifications</label>
              <span className="pref-description">Get updates about your watchlist stocks</span>
            </div>
            <label className="toggle-switch">
              <input
                type="checkbox"
                id="watchlist_notifications"
                name="watchlist_notifications"
                checked={preferences.watchlist_notifications}
                onChange={handleChange}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>

          <div className="pref-item">
            <div className="pref-label">
              <label htmlFor="daily_digest">Daily Digest</label>
              <span className="pref-description">Receive a daily summary email</span>
            </div>
            <label className="toggle-switch">
              <input
                type="checkbox"
                id="daily_digest"
                name="daily_digest"
                checked={preferences.daily_digest}
                onChange={handleChange}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>

          <div className="pref-item">
            <div className="pref-label">
              <label htmlFor="weekly_summary">Weekly Summary</label>
              <span className="pref-description">Receive a weekly portfolio summary</span>
            </div>
            <label className="toggle-switch">
              <input
                type="checkbox"
                id="weekly_summary"
                name="weekly_summary"
                checked={preferences.weekly_summary}
                onChange={handleChange}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>
        </div>

        <div className="pref-category">
          <h3>Data & Display</h3>
          <div className="pref-item">
            <div className="pref-label">
              <label htmlFor="auto_refresh_interval">Auto-Refresh Interval (seconds)</label>
              <span className="pref-description">How often to update stock prices</span>
            </div>
            <input
              type="number"
              id="auto_refresh_interval"
              name="auto_refresh_interval"
              value={preferences.auto_refresh_interval}
              onChange={handleChange}
              min="10"
              max="300"
            />
          </div>

          <div className="pref-item">
            <div className="pref-label">
              <label htmlFor="preferred_market_cap">Preferred Market Cap</label>
              <span className="pref-description">Filter stocks by market capitalization</span>
            </div>
            <select
              id="preferred_market_cap"
              name="preferred_market_cap"
              value={preferences.preferred_market_cap}
              onChange={handleChange}
            >
              <option value="all">All</option>
              <option value="large">Large Cap</option>
              <option value="mid">Mid Cap</option>
              <option value="small">Small Cap</option>
            </select>
          </div>

          <div className="pref-item">
            <div className="pref-label">
              <label htmlFor="default_currency">Default Currency</label>
              <span className="pref-description">Your preferred display currency</span>
            </div>
            <select
              id="default_currency"
              name="default_currency"
              value={preferences.default_currency}
              onChange={handleChange}
            >
              <option value="INR">INR (₹)</option>
              <option value="USD">USD ($)</option>
              <option value="EUR">EUR (€)</option>
              <option value="GBP">GBP (£)</option>
            </select>
          </div>

          <div className="pref-item">
            <div className="pref-label">
              <label htmlFor="price_change_threshold">Price Change Alert Threshold (%)</label>
              <span className="pref-description">Minimum % change to trigger alerts</span>
            </div>
            <input
              type="number"
              id="price_change_threshold"
              name="price_change_threshold"
              value={preferences.price_change_threshold}
              onChange={handleChange}
              min="0"
              max="100"
              step="0.1"
            />
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" className="btn-save" disabled={saving}>
            {saving ? 'Saving...' : 'Save Preferences'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default PreferencesSection;
