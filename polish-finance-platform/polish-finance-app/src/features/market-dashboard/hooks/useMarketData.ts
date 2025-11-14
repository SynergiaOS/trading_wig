/**
 * React Query hook for market data
 * Handles fetching, caching, and auto-refresh of market data
 */

import { useQuery, useQueryClient } from '@tanstack/react-query';
import { fetchRealTimeData, type MarketData } from '../../../lib/dataService';
import type { MarketIndex } from '../../../types/market';

const REFRESH_INTERVAL = 30000; // 30 seconds

export function useMarketData(index: MarketIndex = 'WIG80') {
  const queryClient = useQueryClient();

  const query = useQuery<MarketData, Error>({
    queryKey: ['marketData', index],
    queryFn: () => fetchRealTimeData(index),
    refetchInterval: REFRESH_INTERVAL,
    refetchIntervalInBackground: true,
    staleTime: 25000, // Consider data stale after 25 seconds
    gcTime: 60000, // Keep in cache for 60 seconds
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  const refresh = () => {
    queryClient.invalidateQueries({ queryKey: ['marketData', index] });
  };

  return {
    ...query,
    refresh,
    companies: query.data?.companies || [],
    metadata: query.data?.metadata,
  };
}

