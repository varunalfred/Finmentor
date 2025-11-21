/**
 * ========================================
 * CORPORATE ANNOUNCEMENTS - QUICK START
 * ========================================
 * 
 * Production-ready React component for displaying live BSE India 
 * corporate announcements with auto-refresh and error handling.
 */

// ============================================
// 1. BASIC USAGE (Already Integrated)
// ============================================

import CorporateAnnouncements from './components/dashboard/CorporateAnnouncements';

function App() {
  return (
    <div>
      <CorporateAnnouncements />
    </div>
  );
}


// ============================================
// 2. CUSTOM REFRESH INTERVAL
// ============================================

// In CorporateAnnouncements.jsx, modify line ~65:
useEffect(() => {
  const intervalId = setInterval(() => {
    fetchAnnouncements();
  }, 60000); // 1 minute instead of 5 minutes
  
  return () => clearInterval(intervalId);
}, []);


// ============================================
// 3. FILTER BY COMPANY CODE
// ============================================

// Add prop support:
const CorporateAnnouncements = ({ companyCode = '' }) => {
  const fetchAnnouncements = async () => {
    const todayDate = getTodayDate();
    const apiUrl = `https://api.bseindia.com/BseIndiaAPI/api/AnnGetData/w?strCat=Company%20Update&strPrevDate=${todayDate}&strScrip=${companyCode}`;
    // ... rest of code
  };
};

// Usage:
<CorporateAnnouncements companyCode="500325" /> {/* Reliance */}


// ============================================
// 4. CUSTOM DATE RANGE
// ============================================

const CorporateAnnouncements = ({ startDate, endDate }) => {
  const fetchAnnouncements = async () => {
    const date = startDate || getTodayDate();
    const apiUrl = `https://api.bseindia.com/BseIndiaAPI/api/AnnGetData/w?strCat=Company%20Update&strPrevDate=${date}&strScrip=`;
    // ... rest
  };
};

// Usage:
<CorporateAnnouncements startDate="2025-11-10" />


// ============================================
// 5. USE FETCH HELPER INDEPENDENTLY
// ============================================

import { fetchWithRetry, fetchBSEData } from './utils/apiHelpers';

// Example: Fetch stock data with retry
async function fetchStockData(symbol) {
  try {
    const url = `https://api.example.com/stock/${symbol}`;
    const data = await fetchWithRetry(url, { method: 'GET' }, 3, 1000);
    return data;
  } catch (error) {
    console.error('Failed to fetch:', error.message);
    return null;
  }
}

// Example: BSE-specific API call
async function getBSEAnnouncements(date) {
  const url = `https://api.bseindia.com/BseIndiaAPI/api/AnnGetData/w?strCat=Company%20Update&strPrevDate=${date}&strScrip=`;
  return await fetchBSEData(url);
}


// ============================================
// 6. HANDLING CALLBACKS
// ============================================

const CorporateAnnouncements = ({ onAnnouncementClick, onRefresh }) => {
  const fetchAnnouncements = async () => {
    // ... fetch logic
    if (onRefresh) onRefresh(announcementData);
  };

  return (
    // In card render:
    <div
      onClick={() => onAnnouncementClick && onAnnouncementClick(announcement)}
      className="cursor-pointer"
    >
      {/* ... card content */}
    </div>
  );
};

// Usage:
<CorporateAnnouncements 
  onAnnouncementClick={(ann) => console.log('Clicked:', ann)}
  onRefresh={(data) => console.log('Refreshed with', data.length, 'items')}
/>


// ============================================
// 7. CUSTOM ERROR HANDLING
// ============================================

const CorporateAnnouncements = ({ onError }) => {
  const fetchAnnouncements = async () => {
    try {
      // ... fetch logic
    } catch (err) {
      setError(err.message);
      if (onError) onError(err);
    }
  };
};

// Usage:
<CorporateAnnouncements 
  onError={(error) => {
    console.error('Custom error handler:', error);
    // Send to analytics, show toast, etc.
  }}
/>


// ============================================
// 8. PAGINATION SUPPORT
// ============================================

const CorporateAnnouncements = ({ pageSize = 10 }) => {
  const [currentPage, setCurrentPage] = useState(1);
  
  const paginatedAnnouncements = announcements.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  return (
    <>
      {/* Display paginatedAnnouncements */}
      
      {/* Pagination controls */}
      <div className="flex justify-center gap-2 mt-4">
        <button onClick={() => setCurrentPage(p => Math.max(1, p - 1))}>
          Previous
        </button>
        <span>Page {currentPage}</span>
        <button onClick={() => setCurrentPage(p => p + 1)}>
          Next
        </button>
      </div>
    </>
  );
};


// ============================================
// 9. SEARCH/FILTER FUNCTIONALITY
// ============================================

const CorporateAnnouncements = () => {
  const [searchTerm, setSearchTerm] = useState('');
  
  const filteredAnnouncements = announcements.filter(ann =>
    ann.HEADLINE?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    ann.SCRIP_NAME?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    ann.SCRIPCD?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <>
      <input
        type="text"
        placeholder="Search announcements..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="w-full px-4 py-2 mb-4 border rounded-lg"
      />
      
      {/* Display filteredAnnouncements */}
    </>
  );
};


// ============================================
// 10. EXPORT TO CSV
// ============================================

const CorporateAnnouncements = () => {
  const exportToCSV = () => {
    const headers = ['Company Code', 'Company Name', 'Headline', 'Date'];
    const rows = announcements.map(ann => [
      ann.SCRIPCD,
      ann.SCRIP_NAME,
      ann.HEADLINE,
      ann.NEWSDT
    ]);
    
    const csv = [headers, ...rows]
      .map(row => row.map(cell => `"${cell}"`).join(','))
      .join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `announcements-${getTodayDate()}.csv`;
    a.click();
  };

  return (
    <button onClick={exportToCSV}>Export to CSV</button>
  );
};


// ============================================
// 11. CATEGORY FILTERING
// ============================================

const categories = [
  'Company Update',
  'Board Meeting',
  'Financial Results',
  'Dividend',
  'Acquisition'
];

const CorporateAnnouncements = () => {
  const [selectedCategory, setSelectedCategory] = useState('Company Update');
  
  const fetchAnnouncements = async () => {
    const apiUrl = `https://api.bseindia.com/BseIndiaAPI/api/AnnGetData/w?strCat=${encodeURIComponent(selectedCategory)}&strPrevDate=${getTodayDate()}&strScrip=`;
    // ... fetch
  };

  return (
    <>
      <select 
        value={selectedCategory}
        onChange={(e) => setSelectedCategory(e.target.value)}
      >
        {categories.map(cat => (
          <option key={cat} value={cat}>{cat}</option>
        ))}
      </select>
      {/* ... rest */}
    </>
  );
};


// ============================================
// 12. WEBSOCKET REAL-TIME UPDATES
// ============================================

const CorporateAnnouncements = () => {
  useEffect(() => {
    // Note: BSE doesn't provide WebSocket, this is conceptual
    const ws = new WebSocket('wss://example.com/announcements');
    
    ws.onmessage = (event) => {
      const newAnnouncement = JSON.parse(event.data);
      setAnnouncements(prev => [newAnnouncement, ...prev]);
    };
    
    return () => ws.close();
  }, []);
};


// ============================================
// 13. TOAST NOTIFICATIONS
// ============================================

import { toast } from 'react-toastify';

const CorporateAnnouncements = () => {
  const fetchAnnouncements = async () => {
    try {
      // ... fetch
      toast.success(`Loaded ${announcementData.length} announcements`);
    } catch (err) {
      toast.error(`Failed to load announcements: ${err.message}`);
    }
  };
};


// ============================================
// 14. LOCAL STORAGE CACHING
// ============================================

const CorporateAnnouncements = () => {
  const fetchAnnouncements = async () => {
    try {
      // Check cache first
      const cached = localStorage.getItem('announcements-cache');
      const cacheTime = localStorage.getItem('announcements-cache-time');
      
      if (cached && cacheTime) {
        const age = Date.now() - parseInt(cacheTime);
        if (age < 300000) { // 5 minutes
          setAnnouncements(JSON.parse(cached));
          setLoading(false);
          return;
        }
      }
      
      // Fetch new data
      const data = await fetchBSEData(apiUrl);
      
      // Update cache
      localStorage.setItem('announcements-cache', JSON.stringify(data));
      localStorage.setItem('announcements-cache-time', Date.now().toString());
      
      setAnnouncements(data);
    } catch (err) {
      // Use cached data as fallback
      const cached = localStorage.getItem('announcements-cache');
      if (cached) {
        setAnnouncements(JSON.parse(cached));
      }
    }
  };
};


// ============================================
// 15. TESTING EXAMPLE
// ============================================

import { render, screen, waitFor } from '@testing-library/react';
import CorporateAnnouncements from './CorporateAnnouncements';

// Mock the API
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve([
      {
        SCRIPCD: '500325',
        SCRIP_NAME: 'Reliance Industries',
        HEADLINE: 'Board Meeting',
        NEWSDT: '2025-11-14'
      }
    ])
  })
);

test('renders announcements', async () => {
  render(<CorporateAnnouncements />);
  
  // Check loading state
  expect(screen.getByText(/Loading announcements/i)).toBeInTheDocument();
  
  // Wait for data
  await waitFor(() => {
    expect(screen.getByText(/Reliance Industries/i)).toBeInTheDocument();
  });
  
  // Check announcement details
  expect(screen.getByText(/Board Meeting/i)).toBeInTheDocument();
});


// ============================================
// END OF QUICK REFERENCE
// ============================================

/**
 * For full documentation, see:
 * frontend/CORPORATE_ANNOUNCEMENTS_README.md
 * 
 * Component Location:
 * frontend/src/components/dashboard/CorporateAnnouncements.jsx
 * 
 * Utilities Location:
 * frontend/src/utils/apiHelpers.js
 */
