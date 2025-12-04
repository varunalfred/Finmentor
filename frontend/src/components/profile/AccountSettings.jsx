import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import './AccountSettings.css';

// API Base URL - uses environment variable or defaults to localhost
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const AccountSettings = () => {
  const { user, updateUser } = useAuth(); // ✅ Use AuthContext for initial data

  const [profile, setProfile] = useState({
    username: user?.username || '',
    email: user?.email || '',
    full_name: user?.full_name || '',
    age: user?.age || '',
    user_type: user?.user_type || 'beginner',
    education_level: (user?.education_level && user.education_level !== 'None') ? user.education_level : '',
    risk_tolerance: user?.risk_tolerance || 'moderate',
    financial_goals: user?.financial_goals || [],
    preferred_language: user?.preferred_language || 'en',
    preferred_output: user?.preferred_output || 'text'
  });

  const [passwords, setPasswords] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  const [loading, setLoading] = useState(false); // ✅ No initial load needed
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  const handleProfileChange = (e) => {
    setProfile({
      ...profile,
      [e.target.name]: e.target.value
    });
  };

  const handlePasswordChange = (e) => {
    setPasswords({
      ...passwords,
      [e.target.name]: e.target.value
    });
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage({ type: '', text: '' });

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/api/profile`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(profile)
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'Profile updated successfully!' });
        setTimeout(() => setMessage({ type: '', text: '' }), 3000);
      } else {
        const error = await response.json();
        setMessage({ type: 'error', text: error.detail || 'Failed to update profile' });
      }
    } catch (error) {
      console.error('Error updating profile:', error);
      setMessage({ type: 'error', text: 'An error occurred while updating profile' });
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage({ type: '', text: '' });

    // Validate passwords
    if (passwords.new_password !== passwords.confirm_password) {
      setMessage({ type: 'error', text: 'New passwords do not match' });
      setSaving(false);
      return;
    }

    if (passwords.new_password.length < 8) {
      setMessage({ type: 'error', text: 'Password must be at least 8 characters' });
      setSaving(false);
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/api/profile/change-password`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          current_password: passwords.current_password,
          new_password: passwords.new_password,
          confirm_password: passwords.confirm_password
        })
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'Password changed successfully!' });
        setPasswords({ current_password: '', new_password: '', confirm_password: '' });
        setTimeout(() => setMessage({ type: '', text: '' }), 3000);
      } else {
        const error = await response.json();
        setMessage({ type: 'error', text: error.detail || 'Failed to change password' });
      }
    } catch (error) {
      console.error('Error changing password:', error);
      setMessage({ type: 'error', text: 'An error occurred while changing password' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="account-settings loading">
        <div className="spinner"></div>
        <p>Loading settings...</p>
      </div>
    );
  }

  return (
    <div className="account-settings">
      {message.text && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="settings-section">
        <h2>Profile Details</h2>
        <form onSubmit={handleSaveProfile}>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="full_name">Full Name</label>
              <input
                type="text"
                id="full_name"
                name="full_name"
                value={profile.full_name}
                onChange={handleProfileChange}
                placeholder="Enter your full name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                type="email"
                id="email"
                name="email"
                value={profile.email}
                onChange={handleProfileChange}
                placeholder="your.email@example.com"
                disabled
              />
              <small>Email cannot be changed</small>
            </div>

            <div className="form-group">
              <label htmlFor="age">Age</label>
              <input
                type="number"
                id="age"
                name="age"
                value={profile.age}
                onChange={handleProfileChange}
                placeholder="Age"
                min="18"
                max="120"
              />
            </div>

            <div className="form-group">
              <label htmlFor="education_level">Education Level</label>
              <select
                id="education_level"
                name="education_level"
                value={profile.education_level}
                onChange={handleProfileChange}
              >
                <option value="">Not Specified</option>
                <option value="high_school">High School</option>
                <option value="bachelors">Bachelor's Degree</option>
                <option value="masters">Master's Degree</option>
                <option value="phd">PhD / Doctorate</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="user_type">Financial Knowledge Level</label>
              <select
                id="user_type"
                name="user_type"
                value={profile.user_type}
                onChange={handleProfileChange}
              >
                <option value="beginner">Beginner (Savings & Budgeting)</option>
                <option value="intermediate">Intermediate (Stocks & Bonds)</option>
                <option value="advanced">Advanced (Derivatives & Analysis)</option>
                <option value="expert">Expert (Financial Modeling)</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="risk_tolerance">Risk Tolerance</label>
              <select
                id="risk_tolerance"
                name="risk_tolerance"
                value={profile.risk_tolerance}
                onChange={handleProfileChange}
              >
                <option value="low">Low (Conservative)</option>
                <option value="moderate">Moderate (Balanced)</option>
                <option value="high">High (Aggressive)</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="preferred_language">Preferred Language</label>
              <select
                id="preferred_language"
                name="preferred_language"
                value={profile.preferred_language || 'en'}
                onChange={handleProfileChange}
              >
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
                <option value="de">German</option>
                <option value="hi">Hindi</option>
                <option value="zh">Chinese</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="preferred_output">Preferred Output Format</label>
              <select
                id="preferred_output"
                name="preferred_output"
                value={profile.preferred_output || 'text'}
                onChange={handleProfileChange}
              >
                <option value="text">Text Only</option>
                <option value="visual">Visual (Charts & Graphs)</option>
                <option value="voice">Voice / Audio</option>
              </select>
            </div>

            <div className="form-group full-width">
              <label>Financial Goals</label>
              <div className="checkbox-group">
                {['Retirement', 'Home Purchase', 'Education', 'Wealth Building', 'Travel', 'Emergency Fund'].map(goal => (
                  <label key={goal} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={profile.financial_goals?.includes(goal)}
                      onChange={(e) => {
                        const currentGoals = profile.financial_goals || [];
                        let newGoals;
                        if (e.target.checked) {
                          newGoals = [...currentGoals, goal];
                        } else {
                          newGoals = currentGoals.filter(g => g !== goal);
                        }
                        setProfile({ ...profile, financial_goals: newGoals });
                      }}
                    />
                    {goal}
                  </label>
                ))}
              </div>

              {/* Custom Goal Input */}
              <div className="custom-goal-input">
                <input
                  type="text"
                  placeholder="Add custom goal..."
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      const value = e.target.value.trim();
                      if (value && !profile.financial_goals?.includes(value)) {
                        setProfile({
                          ...profile,
                          financial_goals: [...(profile.financial_goals || []), value]
                        });
                        e.target.value = '';
                      }
                    }
                  }}
                />
                <small>Press Enter to add</small>
              </div>
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>

      <div className="settings-section">
        <h2>Change Password</h2>
        <form onSubmit={handleChangePassword}>
          <div className="form-group">
            <label htmlFor="current_password">Current Password</label>
            <input
              type="password"
              id="current_password"
              name="current_password"
              value={passwords.current_password}
              onChange={handlePasswordChange}
              placeholder="Enter current password"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="new_password">New Password</label>
            <input
              type="password"
              id="new_password"
              name="new_password"
              value={passwords.new_password}
              onChange={handlePasswordChange}
              placeholder="Enter new password (min 8 characters)"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirm_password">Confirm New Password</label>
            <input
              type="password"
              id="confirm_password"
              name="confirm_password"
              value={passwords.confirm_password}
              onChange={handlePasswordChange}
              placeholder="Confirm new password"
              required
            />
          </div>

          <div className="form-actions">
            <button type="submit" className="btn-secondary" disabled={saving}>
              {saving ? 'Changing...' : 'Change Password'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AccountSettings;
