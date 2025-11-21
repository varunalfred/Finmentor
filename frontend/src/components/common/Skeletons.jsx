import React from 'react';
import Skeleton from 'react-loading-skeleton';
import 'react-loading-skeleton/dist/skeleton.css';

export const StockCardSkeleton = () => (
  <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
    <Skeleton height={20} width="60%" />
    <Skeleton height={16} width="40%" className="mt-2" />
    <Skeleton height={24} width="50%" className="mt-3" />
    <div className="flex gap-2 mt-3">
      <Skeleton height={30} width={80} />
      <Skeleton height={30} width={80} />
    </div>
  </div>
);

export const MessageSkeleton = () => (
  <div className="flex gap-3 p-4">
    <Skeleton circle width={40} height={40} />
    <div className="flex-1">
      <Skeleton height={16} width="80%" />
      <Skeleton height={16} width="90%" className="mt-2" />
      <Skeleton height={16} width="70%" className="mt-2" />
    </div>
  </div>
);

export const DashboardSkeleton = () => (
  <div className="space-y-4 p-4">
    <Skeleton height={200} className="rounded-lg" />
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <StockCardSkeleton />
      <StockCardSkeleton />
      <StockCardSkeleton />
    </div>
  </div>
);

export const ConversationSkeleton = () => (
  <div className="p-3 space-y-2">
    {[1, 2, 3, 4, 5].map((i) => (
      <div key={i} className="p-3 border-b border-gray-200 dark:border-gray-700">
        <Skeleton height={16} width="80%" />
        <Skeleton height={12} width="60%" className="mt-2" />
      </div>
    ))}
  </div>
);
