/**
 * Centralized API Service
 * Handles all backend API calls with axios
 */

import axios from 'axios';

// Base configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor - Add auth token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle common errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Handle 401 Unauthorized - redirect to login
      if (error.response.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = '/signup';
      }
      
      // Extract error message
      const message = error.response.data?.detail || error.response.data?.message || 'An error occurred';
      return Promise.reject(new Error(message));
    }
    
    // Network error
    return Promise.reject(new Error('Network error. Please check your connection.'));
  }
);

// ============= API Service Object =============

const api = {
  // ============= Authentication =============
  
  /**
   * Register a new user
   */
  register: async (userData) => {
    try {
      const response = await apiClient.post('/auth/register', userData);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  },

  /**
   * Login user
   */
  login: async (username, password) => {
    try {
      // OAuth2 password flow expects form data
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await apiClient.post('/auth/token', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      // Store token
      const { access_token } = response.data;
      localStorage.setItem('access_token', access_token);

      // Get user profile
      const userProfile = await api.getCurrentUser();
      if (userProfile.success) {
        localStorage.setItem('user', JSON.stringify(userProfile.data));
      }

      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  },

  /**
   * Logout user
   */
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/signup';
  },

  /**
   * Get current user profile
   */
  getCurrentUser: async () => {
    try {
      const response = await apiClient.get('/auth/me');
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },

  /**
   * Get stored user data
   */
  getStoredUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },

  // ============= Chat / FinAdvisor =============

  /**
   * Send a chat message to the AI
   * @param {string} message - The message to send
   * @param {string} conversationId - Optional conversation ID to continue existing thread
   * @param {object} userProfile - Optional user profile override
   * @param {string} inputType - Type of input (text, voice, image, document)
   */
  sendChatMessage: async (message, conversationId = null, userProfile = null, inputType = 'text') => {
    try {
      const storedUser = api.getStoredUser();
      const profile = userProfile || {
        type: storedUser?.user_type || 'beginner',
        education_level: storedUser?.education_level || 'basic',
        preferred_language: 'en',
        preferred_output: 'text',
        user_id: storedUser?.id || 'guest',
        // Include conversation_id if provided to continue thread
        ...(conversationId && { conversation_id: conversationId })
      };

      const response = await apiClient.post('/chat', {
        message,
        input_type: inputType,
        user_profile: profile
      });

      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  },

  /**
   * Get list of user's conversations
   */
  getConversations: async (limit = 50, offset = 0) => {
    try {
      const response = await apiClient.get('/chat/conversations', {
        params: { limit, offset }
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  },

  /**
   * Get all messages from a specific conversation
   */
  getConversationMessages: async (conversationId, limit = 100) => {
    try {
      const response = await apiClient.get(`/chat/conversations/${conversationId}/messages`, {
        params: { limit }
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  },

  /**
   * Delete a conversation
   */
  deleteConversation: async (conversationId) => {
    try {
      const response = await apiClient.delete(`/chat/conversations/${conversationId}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  },

  /**
   * Submit satisfaction rating for a conversation
   */
  submitSatisfactionRating: async (conversationId, rating) => {
    try {
      const response = await apiClient.post(`/chat/conversations/${conversationId}/rating`, {
        rating
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  },

  /**
   * Get conversation history (legacy - keeping for compatibility)
   */
  getConversationHistory: async (userId, limit = 50) => {
    try {
      const response = await apiClient.get(`/chat/history/${userId}`, {
        params: { limit }
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  },

  /**
   * Clear conversation history
   */
  clearConversationHistory: async (userId) => {
    try {
      const response = await apiClient.delete(`/chat/history/${userId}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  },

  // ============= RAG / Knowledge Base =============

  /**
   * Add content to knowledge base
   */
  addToKnowledgeBase: async (content, topic, contentType = 'text') => {
    try {
      const response = await apiClient.post('/rag/add', {
        content,
        topic,
        content_type: contentType
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  },

  /**
   * Search knowledge base
   */
  searchKnowledgeBase: async (query, limit = 5) => {
    try {
      const response = await apiClient.post('/rag/search', {
        query,
        limit
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  },

  // ============= Profile / User Data =============

  /**
   * Update user profile
   */
  updateProfile: async (profileData) => {
    try {
      const response = await apiClient.put('/auth/profile', profileData);
      
      // Update stored user
      const updatedUser = { ...api.getStoredUser(), ...response.data };
      localStorage.setItem('user', JSON.stringify(updatedUser));

      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  },

  // ============= Watchlist (if backend supports it) =============

  /**
   * Get user's watchlist
   */
  getWatchlist: async () => {
    try {
      const response = await apiClient.get('/watchlist');
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  },

  /**
   * Add stock to watchlist
   */
  addToWatchlist: async (symbol, name) => {
    try {
      const response = await apiClient.post('/watchlist', {
        symbol,
        name
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  },

  /**
   * Remove stock from watchlist
   */
  removeFromWatchlist: async (symbol) => {
    try {
      const response = await apiClient.delete(`/watchlist/${symbol}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  },

  // ============= Health Check =============

  /**
   * Check backend health
   */
  healthCheck: async () => {
    try {
      const response = await apiClient.get('/health');
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }
};

export default api;
