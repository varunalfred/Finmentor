import axios from 'axios';

const API_BASE_URL = '/api/watchlist';

/**
 * Add stock to watchlist
 */
export const addToWatchlist = async (symbol, companyName) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/add`, {
      symbol,
      company_name: companyName
    });
    return response.data;
  } catch (error) {
    console.error('Error adding to watchlist:', error);
    throw error;
  }
};

/**
 * Remove stock from watchlist
 */
export const removeFromWatchlist = async (symbol) => {
  try {
    const response = await axios.delete(`${API_BASE_URL}/remove/${symbol}`);
    return response.data;
  } catch (error) {
    console.error('Error removing from watchlist:', error);
    throw error;
  }
};

/**
 * Get user's watchlist
 */
export const getWatchlist = async () => {
  try {
    const response = await axios.get(API_BASE_URL);
    return response.data;
  } catch (error) {
    console.error('Error fetching watchlist:', error);
    throw error;
  }
};

export default {
  addToWatchlist,
  removeFromWatchlist,
  getWatchlist
};
