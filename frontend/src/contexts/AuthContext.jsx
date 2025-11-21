/**
 * Authentication Context
 * Manages user authentication state across the app
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Initialize auth state on mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        if (api.isAuthenticated()) {
          const storedUser = api.getStoredUser();
          
          // Verify token is still valid by fetching current user
          const result = await api.getCurrentUser();
          if (result.success) {
            setUser(result.data);
            setIsAuthenticated(true);
          } else {
            // Token invalid, clear auth
            api.logout();
            setUser(null);
            setIsAuthenticated(false);
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        setUser(null);
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (username, password) => {
    try {
      const result = await api.login(username, password);
      if (result.success) {
        const userResult = await api.getCurrentUser();
        if (userResult.success) {
          setUser(userResult.data);
          setIsAuthenticated(true);
        }
      }
      return result;
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  };

  const register = async (userData) => {
    try {
      const result = await api.register(userData);
      if (result.success) {
        // After registration, log in automatically
        const loginResult = await login(userData.username, userData.password);
        return loginResult;
      }
      return result;
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  };

  const logout = () => {
    api.logout();
    setUser(null);
    setIsAuthenticated(false);
  };

  const updateUser = (userData) => {
    setUser(prev => ({ ...prev, ...userData }));
    localStorage.setItem('user', JSON.stringify({ ...user, ...userData }));
  };

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
    updateUser
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export default AuthContext;
