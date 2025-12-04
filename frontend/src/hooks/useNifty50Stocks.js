import { useQuery } from '@tanstack/react-query';

export const useNifty50Stocks = () => {
    return useQuery({
        queryKey: ['nifty50'],
        queryFn: async () => {
            const response = await fetch('/api/market/nifty50-stocks');
            if (!response.ok) throw new Error('Failed to fetch NIFTY 50 data');
            const data = await response.json();
            return data.stocks || [];
        },
        staleTime: 1000 * 60 * 5, // 5 minutes
        refetchInterval: 1000 * 60 * 2, // 2 minutes
    });
};
