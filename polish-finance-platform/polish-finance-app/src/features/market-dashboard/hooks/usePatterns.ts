/**
 * React Query hook for patterns data
 * Handles fetching and caching of technical patterns
 */

import { useQuery } from '@tanstack/react-query';
import { fetchPatternsData, type PatternsData } from '../../../lib/dataService';

const REFRESH_INTERVAL = 60000; // 60 seconds

export function usePatterns() {
  const query = useQuery<PatternsData, Error>({
    queryKey: ['patterns'],
    queryFn: fetchPatternsData,
    refetchInterval: REFRESH_INTERVAL,
    refetchIntervalInBackground: true,
    staleTime: 55000, // Consider data stale after 55 seconds
    gcTime: 120000, // Keep in cache for 2 minutes
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 10000),
    // Patterns are non-critical, so we don't want to fail the whole app
    throwOnError: false,
  });

  return {
    ...query,
    companiesWithPatterns: query.data?.companies || [],
    totalWithPatterns: query.data?.total_with_patterns || 0,
  };
}

