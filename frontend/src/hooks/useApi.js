import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import api from '../services/api';

// Chat hooks
export const useSendMessage = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ message, conversationId }) =>
      api.sendChatMessage(message, conversationId),
    onSuccess: () => {
      queryClient.invalidateQueries(['conversations']);
    },
    onError: (error) => {
      toast.error('Failed to send message');
    },
  });
};

// Conversations hooks
export const useConversations = (limit = 50, offset = 0) => {
  return useQuery({
    queryKey: ['conversations', limit, offset],
    queryFn: () => api.getConversations(limit, offset),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

export const useConversationMessages = (conversationId) => {
  return useQuery({
    queryKey: ['conversation', conversationId],
    queryFn: () => api.getConversationMessages(conversationId),
    enabled: !!conversationId,
  });
};

export const useDeleteConversation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (conversationId) => api.deleteConversation(conversationId),
    onSuccess: () => {
      queryClient.invalidateQueries(['conversations']);
      toast.success('Conversation deleted');
    },
    onError: () => {
      toast.error('Failed to delete conversation');
    },
  });
};

export const useSubmitRating = () => {
  return useMutation({
    mutationFn: ({ conversationId, rating }) =>
      api.submitSatisfactionRating(conversationId, rating),
    onSuccess: () => {
      toast.success('Thank you for your feedback!');
    },
    onError: () => {
      toast.error('Failed to submit rating');
    },
  });
};

// Stock market hooks  
export const useStockData = (category = 'gainers', cap = 'large') => {
  return useQuery({
    queryKey: ['stocks', category, cap],
    queryFn: () => fetch(`/api/market/stocks?category=${category}&cap=${cap}`).then(r => r.json()),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
};

export const useAnnouncements = (date) => {
  return useQuery({
    queryKey: ['announcements', date],
    queryFn: () => fetch(`/api/market/announcements?date=${date}`).then(r => r.json()),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

// ✅ Watchlist hooks for Profile page optimization
export const useWatchlist = () => {
  return useQuery({
    queryKey: ['watchlist'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/watchlist', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error('Failed to fetch watchlist');
      const result = await response.json();
      return result.data || result;
    },
    staleTime: 30 * 1000,
    refetchInterval: 30 * 1000,
  });
};

export const useWatchlistStats = () => {
  return useQuery({
    queryKey: ['watchlist', 'stats'],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/watchlist/stats', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error('Failed to fetch watchlist stats');
      const result = await response.json();
      return result.data || result;
    },
    staleTime: 30 * 1000,
    refetchInterval: 30 * 1000,
  });
};

export const useActivity = (page, filter) => {
  return useQuery({
    queryKey: ['activity', page, filter],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      let url = `/api/profile/activity?page=${page}&page_size=20`;
      if (filter !== 'all') url += `&activity_type=${filter}`;

      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error('Failed to fetch activity');
      return response.json();
    },
    staleTime: 2 * 60 * 1000,
    keepPreviousData: true,
  });
};
