import React from 'react';
import CorporateAnnouncements from '../components/dashboard/CorporateAnnouncements';

/**
 * Standalone Corporate Announcements Page
 * 
 * This is an example of how to use the CorporateAnnouncements component
 * in a dedicated page layout.
 */
const CorporateAnnouncementsPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Page Header */}
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Live Corporate Announcements
          </h1>
          <p className="text-lg text-gray-600">
            Real-time updates from BSE India • Today's Market Activity
          </p>
        </div>

        {/* Corporate Announcements Component */}
        <CorporateAnnouncements />

        {/* Additional Information Section */}
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">
            About Corporate Announcements
          </h3>
          <div className="grid md:grid-cols-2 gap-6 text-sm text-gray-600">
            <div>
              <h4 className="font-medium text-gray-800 mb-2">What are Corporate Announcements?</h4>
              <p>
                Corporate announcements are official communications from companies listed on the
                stock exchange. They include board meetings, dividends, acquisitions, financial
                results, and other material information that can affect stock prices.
              </p>
            </div>
            <div>
              <h4 className="font-medium text-gray-800 mb-2">Why Monitor Announcements?</h4>
              <p>
                Staying updated with corporate announcements helps investors make informed decisions.
                Material events can significantly impact stock valuations, and timely information
                provides a competitive advantage in the market.
              </p>
            </div>
            <div>
              <h4 className="font-medium text-gray-800 mb-2">Data Source</h4>
              <p>
                All announcements are fetched directly from BSE India's official API, ensuring
                accuracy and reliability. The data is refreshed automatically every 5 minutes to
                keep you updated with the latest information.
              </p>
            </div>
            <div>
              <h4 className="font-medium text-gray-800 mb-2">Key Features</h4>
              <ul className="list-disc list-inside space-y-1">
                <li>Real-time updates from BSE</li>
                <li>Auto-refresh every 5 minutes</li>
                <li>Direct PDF attachment access</li>
                <li>Company code filtering</li>
                <li>Error handling with retry</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="mt-6 text-center text-sm text-gray-500">
          <p>
            Data provided by BSE India. For official records, please visit{' '}
            <a
              href="https://www.bseindia.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              bseindia.com
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default CorporateAnnouncementsPage;
