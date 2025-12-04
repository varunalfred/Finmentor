import axios from 'axios';

const API_BASE_URL = '/api';

/**
 * Fetch all market indices (Indian, Global, Commodities)
 * @returns {Promise} Market indices data
 */
export const getMarketIndices = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/market/live-indices`);

    // Transform response to match MarketTicker expectations
    // Flatten all indices into a single array
    const allIndices = [
      ...(response.data.indian_markets || []),
      ...(response.data.global_markets || []),
      ...(response.data.commodities || [])
    ];

    return {
      success: true,
      data: {
        indices: allIndices,
        last_updated: new Date().toISOString()
      }
    };
  } catch (error) {
    console.error('Error fetching market indices:', error);
    return {
      success: false,
      error: error.response?.data?.detail || 'Failed to fetch market data'
    };
  }
};





/**
 * Format currency for Indian market (INR)
 * @param {number} value - Value to format
 * @returns {string} Formatted currency string
 */
export const formatINR = (value) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
};

/**
 * Format number with Indian numbering system (lakhs, crores)
 * @param {number} value - Value to format
 * @returns {string} Formatted number string
 */
export const formatIndianNumber = (value) => {
  return new Intl.NumberFormat('en-IN').format(value);
};

/**
 * Get color class based on change value
 * @param {number} change - Change value (positive or negative)
 * @returns {string} CSS class name
 */
export const getChangeColor = (change) => {
  if (change > 0) return 'positive';
  if (change < 0) return 'negative';
  return 'neutral';
};

/**
 * Format timestamp to readable time
 * @param {string} isoString - ISO timestamp string
 * @returns {string} Formatted time string
 */
export const formatTime = (isoString) => {
  const date = new Date(isoString);
  return date.toLocaleTimeString('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

/**
 * Check if market is currently open (rough estimate)
 * Indian market hours: 9:15 AM to 3:30 PM IST (Mon-Fri)
 * @returns {boolean} True if market is likely open
 */
export const isMarketOpen = () => {
  const now = new Date();
  const day = now.getDay(); // 0 = Sunday, 6 = Saturday
  const hour = now.getHours();

  // Weekend check
  if (day === 0 || day === 6) return false;

  // Market hours check (approximate - doesn't account for timezone)
  if (hour >= 9 && hour < 16) return true;

  return false;
};

/**
 * Fetch live market indices (Indian markets, global markets, commodities)
 * @returns {Promise} Live indices data grouped by category
 */
export const getLiveIndices = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/market/live-indices`);
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    console.error('Error fetching live indices:', error);
    return {
      success: false,
      error: error.response?.data?.detail || 'Failed to fetch live indices'
    };
  }
};

