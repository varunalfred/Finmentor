/**
 * API Helper Functions
 * Provides robust fetching with retry logic and error handling
 */

/**
 * Fetch with automatic retry logic
 * @param {string} url - The URL to fetch
 * @param {Object} options - Fetch options (method, headers, body, etc.)
 * @param {number} maxRetries - Maximum number of retry attempts (default: 3)
 * @param {number} retryDelay - Delay between retries in ms (default: 1000)
 * @returns {Promise<any>} - Parsed JSON response
 */
export const fetchWithRetry = async (
  url,
  options = {},
  maxRetries = 3,
  retryDelay = 1000
) => {
  let lastError;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      console.log(`Fetch attempt ${attempt}/${maxRetries} for: ${url}`);
      
      // Add timeout to prevent hanging requests
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 second timeout
      
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      
      // Check if response is ok (status 200-299)
      if (!response.ok) {
        throw new Error(
          `HTTP error! Status: ${response.status} ${response.statusText}`
        );
      }
      
      // Try to parse JSON
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const data = await response.json();
        
        // Validate that we got data
        if (data === null || data === undefined) {
          throw new Error('Received empty or null response');
        }
        
        return data;
      } else {
        // If not JSON, get text and try to parse it
        const text = await response.text();
        
        if (!text || text.trim().length === 0) {
          throw new Error('Received empty response body');
        }
        
        // Try to parse as JSON anyway (some APIs return JSON with wrong content-type)
        try {
          const data = JSON.parse(text);
          return data;
        } catch {
          throw new Error(`Received non-JSON response: ${text.substring(0, 100)}`);
        }
      }
      
    } catch (error) {
      lastError = error;
      
      // Don't retry on abort errors (timeout)
      if (error.name === 'AbortError') {
        console.error(`Request timeout on attempt ${attempt}`);
        if (attempt === maxRetries) {
          throw new Error('Request timeout after multiple attempts');
        }
      }
      
      // Log the error
      console.error(
        `Fetch attempt ${attempt}/${maxRetries} failed:`,
        error.message
      );
      
      // If this was the last attempt, throw the error
      if (attempt === maxRetries) {
        throw new Error(
          `Failed after ${maxRetries} attempts: ${error.message}`
        );
      }
      
      // Wait before retrying (exponential backoff)
      const delay = retryDelay * Math.pow(2, attempt - 1);
      console.log(`Retrying in ${delay}ms...`);
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }
  
  // Should never reach here, but just in case
  throw lastError || new Error('Unknown error occurred');
};

/**
 * Fetch with retry specifically for BSE API
 * Adds BSE-specific headers and handling
 */
export const fetchBSEData = async (url, maxRetries = 3) => {
  return fetchWithRetry(
    url,
    {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      },
    },
    maxRetries
  );
};

/**
 * Safe JSON parse with fallback
 * @param {string} text - Text to parse
 * @param {any} fallback - Fallback value if parse fails
 * @returns {any} - Parsed object or fallback
 */
export const safeJSONParse = (text, fallback = null) => {
  try {
    return JSON.parse(text);
  } catch (error) {
    console.error('JSON parse error:', error);
    return fallback;
  }
};

/**
 * Check if response is valid and has data
 * @param {any} data - Data to validate
 * @returns {boolean} - True if data is valid
 */
export const isValidResponse = (data) => {
  if (!data) return false;
  
  // Check if it's an array with items
  if (Array.isArray(data)) {
    return data.length > 0;
  }
  
  // Check if it's an object with properties
  if (typeof data === 'object') {
    return Object.keys(data).length > 0;
  }
  
  return false;
};

/**
 * Extract array from nested response structure
 * BSE API sometimes returns data in different formats
 * @param {any} response - API response
 * @returns {Array} - Extracted array or empty array
 */
export const extractArrayFromResponse = (response) => {
  if (!response) return [];
  
  // If already an array
  if (Array.isArray(response)) {
    return response;
  }
  
  // Common BSE response structures
  if (response.Table) return response.Table;
  if (response.data) return Array.isArray(response.data) ? response.data : [];
  if (response.result) return Array.isArray(response.result) ? response.result : [];
  
  // Search for first array in object
  const arrays = Object.values(response).filter(Array.isArray);
  if (arrays.length > 0) {
    return arrays[0];
  }
  
  return [];
};

export default {
  fetchWithRetry,
  fetchBSEData,
  safeJSONParse,
  isValidResponse,
  extractArrayFromResponse,
};
