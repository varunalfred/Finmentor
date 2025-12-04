import { useQuery } from '@tanstack/react-query';

export const useLiveIndices = () => {
    return useQuery({
        queryKey: ['liveIndices'],
        queryFn: () => fetch('/api/market/live-indices').then(r => r.json()),
        refetchInterval: 30000, // Refresh every 30 seconds
        staleTime: 20000, // 20 seconds
    });
};
