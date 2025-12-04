import { useQuery } from '@tanstack/react-query';

export const useStockSearch = (query) => {
    return useQuery({
        queryKey: ['stockSearch', query],
        queryFn: async () => {
            if (!query || query.length < 2) return [];
            const response = await fetch(`/api/market/search?query=${encodeURIComponent(query)}`);
            if (!response.ok) throw new Error('Search failed');
            const data = await response.json();
            return data.results || [];
        },
        enabled: !!query && query.length >= 2,
        staleTime: 1000 * 60 * 5, // 5 minutes cache
        keepPreviousData: true,
    });
};
