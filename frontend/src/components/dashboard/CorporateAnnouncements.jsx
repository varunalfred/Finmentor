import React, { useMemo } from 'react';
import { useAnnouncements } from '../../hooks/useApi';

const CorporateAnnouncements = () => {
  // Format today's date as YYYY-MM-DD
  const getTodayDate = () => {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  const todayDate = useMemo(() => getTodayDate(), []);

  // ✅ Use React Query hook - automatic fetching and 5-minute refresh
  const { data: announcements = [], isLoading: loading, error: fetchError, refetch } =
    useAnnouncements(todayDate);

  const error = fetchError ? 'Failed to fetch announcements' : null;
  const lastUpdated = useMemo(() => new Date(), [announcements]);

  // ✅ No useEffect needed - React Query handles fetching and auto-refresh

  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateString;
    }
  };

  // Extract attachment URL
  const getAttachmentUrl = (attachmentName) => {
    if (!attachmentName) return null;
    // BSE typically hosts PDFs on their domain
    if (attachmentName.startsWith('http')) {
      return attachmentName;
    }
    return `https://www.bseindia.com/xml-data/corpfiling/AttachLive/${attachmentName}`;
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-800">
            Corporate Announcements
          </h2>
          <span className="text-sm text-gray-500">{getTodayDate()}</span>
        </div>
        <div className="flex flex-col items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading announcements...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-800">
            Corporate Announcements
          </h2>
          <span className="text-sm text-gray-500">{getTodayDate()}</span>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start">
            <svg
              className="h-5 w-5 text-red-400 mt-0.5"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                Error Loading Announcements
              </h3>
              <p className="mt-1 text-sm text-red-700">{error}</p>
              <button
                onClick={fetchAnnouncements}
                className="mt-3 text-sm font-medium text-red-800 hover:text-red-900 underline"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">
            Corporate Announcements
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Live updates from BSE India • {getTodayDate()}
          </p>
        </div>
        <div className="flex items-center gap-3">
          {lastUpdated && (
            <span className="text-xs text-gray-400">
              Updated: {lastUpdated.toLocaleTimeString('en-IN', {
                hour: '2-digit',
                minute: '2-digit'
              })}
            </span>
          )}
          <button
            onClick={() => refetch()}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            title="Refresh"
          >
            <svg
              className="w-5 h-5 text-gray-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
          </button>
        </div>
      </div>

      {/* Announcements Grid */}
      {announcements.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-gray-900">
            No Corporate Actions Today
          </h3>
          <p className="mt-2 text-sm text-gray-500">
            There are no announcements available for {getTodayDate()}
          </p>
        </div>
      ) : (
        <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
          {announcements.map((announcement, index) => {
            const attachmentUrl = getAttachmentUrl(announcement.ATTACHMENTNAME);

            return (
              <div
                key={index}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow bg-gradient-to-r from-white to-gray-50"
              >
                {/* Company Code Badge */}
                {announcement.SCRIPCD && (
                  <div className="flex items-center gap-2 mb-3">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-800">
                      {announcement.SCRIPCD}
                    </span>
                    {announcement.SCRIP_NAME && (
                      <span className="text-sm text-gray-600">
                        {announcement.SCRIP_NAME}
                      </span>
                    )}
                  </div>
                )}

                {/* Headline */}
                <h3 className="text-lg font-semibold text-gray-900 mb-2 leading-tight">
                  {announcement.HEADLINE || announcement.NEWS_SUBJECT || 'Announcement'}
                </h3>

                {/* Date and Time */}
                {announcement.NEWSDT && (
                  <p className="text-sm text-gray-500 mb-3 flex items-center gap-1">
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    {formatDate(announcement.NEWSDT)}
                  </p>
                )}

                {/* Additional Details */}
                {announcement.CATEGORYNAME && (
                  <p className="text-sm text-gray-600 mb-2">
                    <span className="font-medium">Category:</span> {announcement.CATEGORYNAME}
                  </p>
                )}

                {/* Attachment Link */}
                {attachmentUrl && announcement.ATTACHMENTNAME && (
                  <a
                    href={attachmentUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 mt-3 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                      />
                    </svg>
                    View Attachment
                  </a>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Footer with count */}
      {announcements.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-600 text-center">
            Showing <span className="font-semibold">{announcements.length}</span> announcement{announcements.length !== 1 ? 's' : ''} • Auto-refreshes every 5 minutes
          </p>
        </div>
      )}
    </div>
  );
};

export default CorporateAnnouncements;
