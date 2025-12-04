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

  // Initialize auth state on mount - OPTIMIZED for performance
  useEffect(() => {
    const initAuth = async () => {
      try {
        // ✅ Use stored data immediately (no blocking)
        const storedUser = api.getStoredUser();
        if (storedUser && api.isAuthenticated()) {
          setUser(storedUser);
          setIsAuthenticated(true);
          setLoading(false);  // ✅ Unblock immediately

          // ✅ Verify token in background (non-blocking)
          api.getCurrentUser().then(result => {
            if (result.success) {
              // Update with fresh data from server
              setUser(result.data);
              localStorage.setItem('user', JSON.stringify(result.data));
            } else {
              // Token expired, logout
              console.warn('Token verification failed, logging out');
              api.logout();
              setUser(null);
              setIsAuthenticated(false);
            }
          }).catch(error => {
            console.error('Background auth verification failed:', error);
            // Don't logout on network errors, keep using cached data
          });
        } else {
          // No stored user or token
          setLoading(false);
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
        {children}  {/* ✅ No blocking - render immediately */}
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
