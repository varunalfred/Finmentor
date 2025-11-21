# Corporate Announcements Component

## Overview
A React component that displays live corporate announcements from BSE India API with automatic refresh, retry logic, and comprehensive error handling.

## Files Created

### 1. CorporateAnnouncements.jsx
Location: `frontend/src/components/dashboard/CorporateAnnouncements.jsx`

**Features:**
- ✅ Fetches live corporate announcements from BSE India
- ✅ Auto-formats current date as YYYY-MM-DD
- ✅ Loading spinner during fetch
- ✅ Auto-refresh every 5 minutes (300,000ms)
- ✅ Manual refresh button
- ✅ Displays announcement cards with:
  - Company code (SCRIPCD)
  - Company name (SCRIP_NAME)
  - Headline/Subject
  - Date and time
  - Category
  - Downloadable attachment link
- ✅ "No announcements" empty state
- ✅ Error handling with retry button
- ✅ Styled with Tailwind CSS
- ✅ Responsive design with scrollable list

### 2. apiHelpers.js
Location: `frontend/src/utils/apiHelpers.js`

**Utility Functions:**

#### `fetchWithRetry(url, options, maxRetries, retryDelay)`
Main fetch function with retry logic.

**Parameters:**
- `url` (string): API endpoint URL
- `options` (object): Fetch options (headers, method, etc.)
- `maxRetries` (number): Max retry attempts (default: 3)
- `retryDelay` (number): Initial delay in ms (default: 1000)

**Features:**
- ✅ Automatic retry with exponential backoff
- ✅ 15-second timeout per request
- ✅ HTTP status validation
- ✅ JSON parsing with fallback
- ✅ Comprehensive error messages
- ✅ Abort controller for timeout handling

#### `fetchBSEData(url, maxRetries)`
Specialized wrapper for BSE API calls with proper headers.

#### `extractArrayFromResponse(response)`
Handles different BSE API response formats (Table, data, result, etc.)

#### `isValidResponse(data)`
Validates if response contains actual data.

#### `safeJSONParse(text, fallback)`
Safe JSON parsing with fallback value.

### 3. Dashboard.jsx (Updated)
Location: `frontend/src/components/Dashboard.jsx`

**Changes:**
- ✅ Imported CorporateAnnouncements component
- ✅ Added to home page layout (renders above StockCarousel)

---

## API Endpoint Details

**BSE India Corporate Announcements API:**
```
https://api.bseindia.com/BseIndiaAPI/api/AnnGetData/w?strCat=Company%20Update&strPrevDate={YYYY-MM-DD}&strScrip=
```

**Parameters:**
- `strCat`: Category (Company Update)
- `strPrevDate`: Date filter (YYYY-MM-DD format)
- `strScrip`: Company code filter (empty = all companies)

**Response Format:**
The API may return data in various structures:
- Direct array: `[{...}, {...}]`
- Nested in Table: `{ Table: [{...}] }`
- Other nested formats handled by `extractArrayFromResponse()`

**Key Response Fields:**
- `SCRIPCD`: Company code
- `SCRIP_NAME`: Company name
- `HEADLINE`: Announcement headline
- `NEWS_SUBJECT`: Alternative headline field
- `NEWSDT`: Date and time of announcement
- `CATEGORYNAME`: Category of announcement
- `ATTACHMENTNAME`: PDF attachment filename/URL

---

## Usage Examples

### Basic Implementation (Already Integrated)

```jsx
import CorporateAnnouncements from './components/dashboard/CorporateAnnouncements';

function Dashboard() {
  return (
    <div>
      <CorporateAnnouncements />
    </div>
  );
}
```

### Standalone Page

```jsx
import React from 'react';
import CorporateAnnouncements from './components/dashboard/CorporateAnnouncements';

function AnnouncementsPage() {
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <CorporateAnnouncements />
      </div>
    </div>
  );
}

export default AnnouncementsPage;
```

### Using Fetch Helper Independently

```jsx
import { fetchWithRetry, fetchBSEData } from './utils/apiHelpers';

// Example 1: Generic fetch with retry
async function fetchData() {
  try {
    const data = await fetchWithRetry(
      'https://api.example.com/data',
      {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
      },
      3, // max retries
      1000 // initial delay
    );
    console.log(data);
  } catch (error) {
    console.error('Failed:', error.message);
  }
}

// Example 2: BSE-specific fetch
async function fetchBSEAnnouncements() {
  try {
    const url = 'https://api.bseindia.com/BseIndiaAPI/api/AnnGetData/w?strCat=Company%20Update&strPrevDate=2025-11-14&strScrip=';
    const data = await fetchBSEData(url);
    console.log(data);
  } catch (error) {
    console.error('BSE fetch failed:', error.message);
  }
}
```

---

## Customization Guide

### Changing Refresh Interval

In `CorporateAnnouncements.jsx`, modify the `useEffect` hook:

```jsx
// Current: 5 minutes (300000ms)
useEffect(() => {
  const intervalId = setInterval(() => {
    fetchAnnouncements();
  }, 300000); // Change this value
  
  return () => clearInterval(intervalId);
}, []);

// Examples:
// 1 minute: 60000
// 10 minutes: 600000
// 30 minutes: 1800000
```

### Changing Retry Settings

In `CorporateAnnouncements.jsx`, modify the `fetchAnnouncements` call:

```jsx
const data = await fetchWithRetry(
  apiUrl,
  { method: 'GET', headers: { 'Accept': 'application/json' } },
  5,    // maxRetries: try 5 times instead of 3
  2000  // retryDelay: wait 2 seconds instead of 1
);
```

### Adding More Fields to Display

In `CorporateAnnouncements.jsx`, add fields to the announcement card:

```jsx
{/* Add new field */}
{announcement.NEW_FIELD_NAME && (
  <p className="text-sm text-gray-600">
    <span className="font-medium">Label:</span> {announcement.NEW_FIELD_NAME}
  </p>
)}
```

### Filtering by Company

Add a company filter prop:

```jsx
const CorporateAnnouncements = ({ companyCode = '' }) => {
  const getTodayDate = () => { /* ... */ };
  
  const fetchAnnouncements = async () => {
    const todayDate = getTodayDate();
    const apiUrl = `https://api.bseindia.com/BseIndiaAPI/api/AnnGetData/w?strCat=Company%20Update&strPrevDate=${todayDate}&strScrip=${companyCode}`;
    // ... rest of code
  };
  
  // ... rest of component
};

// Usage:
<CorporateAnnouncements companyCode="RELIANCE" />
```

### Custom Styling

The component uses Tailwind CSS classes. To customize:

```jsx
// Change card background
<div className="border border-gray-200 rounded-lg p-4 bg-blue-50"> 
  {/* was: bg-gradient-to-r from-white to-gray-50 */}

// Change header color
<h2 className="text-2xl font-bold text-blue-800">
  {/* was: text-gray-800 */}

// Change button style
<button className="px-4 py-2 bg-green-600 hover:bg-green-700">
  {/* was: bg-blue-600 hover:bg-blue-700 */}
```

---

## Error Handling

### Network Errors
- Automatically retries 3 times with exponential backoff (1s, 2s, 4s)
- Shows error message with "Try Again" button
- Logs detailed errors to console

### Invalid Responses
- Validates response status (200-299)
- Checks for empty/null responses
- Parses JSON with fallback handling
- Extracts arrays from various nested structures

### Timeout Handling
- 15-second timeout per request attempt
- Aborts request if timeout exceeded
- Does not retry on timeout (moves to next attempt)

---

## Testing

### Manual Testing

1. **Initial Load:**
   - Component should show loading spinner
   - After 1-3 seconds, announcements should appear

2. **Empty State:**
   - On days with no announcements, shows "No Corporate Actions Today"

3. **Refresh:**
   - Click refresh button
   - Should show loading and fetch new data

4. **Auto-refresh:**
   - Wait 5 minutes
   - Component should automatically refresh

5. **Error Handling:**
   - Disable network in DevTools
   - Component should show error after 3 retry attempts
   - Click "Try Again" to retry

6. **Attachments:**
   - Click "View Attachment" button
   - Should open PDF in new tab

### Console Logs

The component logs the following:
```
Fetching announcements for date: 2025-11-14
Fetch attempt 1/3 for: https://api.bseindia.com/...
Fetched 15 announcements
Auto-refreshing announcements...
```

---

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

**Requirements:**
- JavaScript ES6+ support
- Fetch API support
- AbortController support (for timeouts)

---

## Performance Optimization

### Current Optimizations:
1. **Caching:** Results stored in state until next fetch
2. **Debouncing:** 5-minute refresh interval prevents excessive API calls
3. **Lazy rendering:** Announcements list is scrollable, not paginated
4. **Conditional rendering:** Only renders when on dashboard page

### Future Enhancements:
- Add Redis/localStorage caching for offline support
- Implement pagination for 100+ announcements
- Add WebSocket support for real-time updates
- Service worker for background refresh

---

## Troubleshooting

### Issue: "No announcements showing"
**Solutions:**
1. Check console for API errors
2. Verify date format is correct (YYYY-MM-DD)
3. Check if BSE API is accessible from your network
4. Try accessing API URL directly in browser

### Issue: "CORS errors"
**Solutions:**
1. If developing locally, use a CORS proxy
2. Configure backend proxy in `vite.config.js`:
```js
export default {
  server: {
    proxy: {
      '/bse-api': {
        target: 'https://api.bseindia.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/bse-api/, '')
      }
    }
  }
}
```

### Issue: "Attachment links not working"
**Solutions:**
1. Some PDFs require authentication
2. Try opening in incognito mode
3. BSE may have rate limits on attachment downloads

### Issue: "Component not showing"
**Solutions:**
1. Verify Tailwind CSS is configured
2. Check import path is correct
3. Ensure `apiHelpers.js` exists in `src/utils/`
4. Check console for import errors

---

## Production Deployment

### Environment Variables

Create `.env` file:
```env
VITE_BSE_API_URL=https://api.bseindia.com/BseIndiaAPI/api/AnnGetData/w
VITE_REFRESH_INTERVAL=300000
VITE_MAX_RETRIES=3
```

Use in component:
```jsx
const apiUrl = `${import.meta.env.VITE_BSE_API_URL}?strCat=Company%20Update&strPrevDate=${todayDate}&strScrip=`;
```

### Build Optimization

In `vite.config.js`:
```js
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'corporate': ['./src/components/dashboard/CorporateAnnouncements.jsx']
        }
      }
    }
  }
}
```

---

## License & Credits

**Component Author:** GitHub Copilot  
**API Provider:** BSE India (Bombay Stock Exchange)  
**Framework:** React 18.2+  
**Styling:** Tailwind CSS  
**Icons:** Heroicons (embedded as SVG)

---

## Support

For issues or questions:
1. Check console logs for errors
2. Verify API endpoint is accessible
3. Review this documentation
4. Check Tailwind CSS configuration

Happy coding! 🚀
